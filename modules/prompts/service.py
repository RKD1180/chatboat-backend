from fastapi import HTTPException, status
from config.database import get_connection
from modules.prompts.model import Prompt
from modules.prompts.schema import PromptCreate, PromptUpdate


def create(data: PromptCreate, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO prompts (project_id, user_id, name, content, is_default, created_at)
               VALUES (%s, %s, %s, %s, %s, NOW())
               RETURNING id, project_id, user_id, name, content, is_default, created_at""",
            (data.projectId, user_id, data.name, data.content, data.isDefault),
        )
        prompt = cur.fetchone()
        conn.commit()
        cur.close()
        return Prompt.from_row(prompt).to_dict()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()


def list(project_id: str, user_id: str) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, project_id, user_id, name, content, is_default, created_at
               FROM prompts WHERE user_id = %s AND project_id = %s ORDER BY created_at DESC""",
            (user_id, project_id),
        )
        rows = cur.fetchall()
        cur.close()
        return [Prompt.from_row(r).to_dict() for r in rows]
    finally:
        conn.close()


def get(prompt_id: str, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, project_id, user_id, name, content, is_default, created_at FROM prompts WHERE id = %s AND user_id = %s",
            (prompt_id, user_id),
        )
        prompt = cur.fetchone()
        cur.close()
        if not prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
        return Prompt.from_row(prompt).to_dict()
    finally:
        conn.close()


def update(prompt_id: str, data: PromptUpdate, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM prompts WHERE id = %s AND user_id = %s", (prompt_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
        
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        if not updates:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
        
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        values = list(updates.values()) + [prompt_id, user_id]
        
        cur.execute(
            f"""UPDATE prompts SET {set_clause}
                WHERE id = %s AND user_id = %s
                RETURNING id, project_id, user_id, name, content, is_default, created_at""",
            values,
        )
        prompt = cur.fetchone()
        conn.commit()
        cur.close()
        return Prompt.from_row(prompt).to_dict()
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()


def delete(prompt_id: str, user_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM prompts WHERE id = %s AND user_id = %s", (prompt_id, user_id))
        conn.commit()
        cur.close()
    finally:
        conn.close()
