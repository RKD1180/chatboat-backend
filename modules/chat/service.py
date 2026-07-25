from typing import Optional
from fastapi import HTTPException, status
from config.database import get_connection
from modules.chat.model import Conversation, Message
from modules.chat.schema import CreateConversationRequest, SendMessageRequest
from modules.chat.gemini import chat as gemini_chat
from modules.training.service import find_relevant


def create_conversation(data: CreateConversationRequest, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO conversations (project_id, user_id, title, created_at, updated_at)
               VALUES (%s, %s, %s, NOW(), NOW())
               RETURNING id, project_id, user_id, title, created_at, updated_at""",
            (data.projectId, user_id, data.title or "New Chat"),
        )
        conv = cur.fetchone()
        conn.commit()
        cur.close()
        return Conversation.from_row(conv).to_dict()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()


def get_conversations(user_id: str, project_id: Optional[str] = None) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if project_id:
            cur.execute(
                """SELECT id, project_id, user_id, title, created_at, updated_at
                   FROM conversations WHERE user_id = %s AND project_id = %s ORDER BY updated_at DESC""",
                (user_id, project_id),
            )
        else:
            cur.execute(
                """SELECT id, project_id, user_id, title, created_at, updated_at
                   FROM conversations WHERE user_id = %s ORDER BY updated_at DESC""",
                (user_id,),
            )
        rows = cur.fetchall()
        cur.close()
        return [Conversation.from_row(r).to_dict() for r in rows]
    finally:
        conn.close()


def delete_conversation(conversation_id: str, user_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM conversations WHERE id = %s AND user_id = %s", (conversation_id, user_id))
        conn.commit()
        cur.close()
    finally:
        conn.close()


def update_conversation(conversation_id: str, user_id: str, title: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """UPDATE conversations SET title = %s, updated_at = NOW() 
               WHERE id = %s AND user_id = %s
               RETURNING id, project_id, user_id, title, created_at, updated_at""",
            (title, conversation_id, user_id),
        )
        conv = cur.fetchone()
        conn.commit()
        cur.close()
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        return Conversation.from_row(conv).to_dict()
    finally:
        conn.close()


async def send_message(conversation_id: str, data: SendMessageRequest, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, project_id, user_id, title, created_at, updated_at FROM conversations WHERE id = %s AND user_id = %s",
            (conversation_id, user_id),
        )
        conv = cur.fetchone()
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        
        project_id = conv[1]
        conversation_title = conv[3]
        
        cur.execute("SELECT model FROM projects WHERE id = %s AND user_id = %s", (project_id, user_id))
        project = cur.fetchone()
        model = project[0] if project and project[0] else "gemini-flash-latest"
        
        # Auto-generate title from first message
        if conversation_title == "New Chat" or not conversation_title:
            title = data.content[:50] + ("..." if len(data.content) > 50 else "")
            cur.execute("UPDATE conversations SET title = %s WHERE id = %s", (title, conversation_id))
            conn.commit()
        
        relevant_training = await find_relevant(user_id, project_id, data.content, 5)
        
        cur.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (%s, 'user', %s, NOW())",
            (conversation_id, data.content),
        )
        conn.commit()
        
        cur.execute(
            "SELECT id, conversation_id, role, content, created_at FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
            (conversation_id,),
        )
        history_rows = cur.fetchall()
        history = [Message.from_row(r).to_dict() for r in history_rows]
        
        system_prompt = ""
        if relevant_training:
            context = "\n\n".join(
                f"[Source {i + 1}] (Similarity: {t['similarity']:.2f})\n{t['content']}"
                for i, t in enumerate(relevant_training)
            )
            system_prompt = f"""You are a helpful assistant. Use the following training data to answer questions accurately.

Training Data:
{context}

---
Instructions:
- Answer ONLY based on the training data provided
- If the training data doesn't contain relevant information to answer the question, respond politely: "I'm sorry, but I don't have information about that in my training data. Please try asking something related to the provided documents."
- Never make up or hallucinate information
- Always cite which source you're using when referencing training data
- Be concise and accurate"""
        else:
            system_prompt = """You are a helpful assistant. However, no training data has been provided for this project.

Instructions:
- Politely inform the user that no training data is available
- Suggest they add training data (text or PDF) before asking questions
- Response example: "I don't have any training data to answer your question yet. Please add some training data (text or PDF) in the Training tab first." """
        
        messages_for_ai = []
        if system_prompt:
            messages_for_ai.append({"role": "system", "content": system_prompt})
        messages_for_ai.extend([{"role": m["role"], "content": m["content"]} for m in history])
        
        ai_response = await gemini_chat(messages_for_ai, model)
        
        cur.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (%s, 'assistant', %s, NOW())",
            (conversation_id, ai_response),
        )
        cur.execute("UPDATE conversations SET updated_at = NOW() WHERE id = %s", (conversation_id,))
        conn.commit()
        cur.close()
        
        return {
            "userMessage": history[-1] if history else {},
            "assistantMessage": {"role": "assistant", "content": ai_response},
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()


def get_messages(conversation_id: str, user_id: str) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM conversations WHERE id = %s AND user_id = %s", (conversation_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        cur.execute(
            "SELECT id, conversation_id, role, content, created_at FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
            (conversation_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return [Message.from_row(r).to_dict() for r in rows]
    finally:
        conn.close()
