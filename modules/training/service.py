import io
import re
from typing import List
from fastapi import HTTPException, status, UploadFile
from config.database import get_connection
from modules.training.model import TrainingData
from modules.training.schema import TextRequest
from modules.training.embedding import (
    generate_embedding,
    find_relevant_chunks_from_db,
)
from PyPDF2 import PdfReader


async def add_text(data: TextRequest, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        embedding = await generate_embedding(data.content)
        embedding_str = f"[{','.join(str(x) for x in embedding)}]" if embedding else None
        cur.execute(
            """INSERT INTO training_data (project_id, user_id, content, type, embeddings, created_at)
               VALUES (%s, %s, %s, 'text', %s::vector, NOW())
               RETURNING id, project_id, user_id, content, type, file_name, metadata, created_at""",
            (data.projectId, user_id, data.content, embedding_str),
        )
        training = cur.fetchone()
        conn.commit()
        cur.close()
        return TrainingData.from_row(training).to_dict()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()


async def add_pdf(project_id: str, file: UploadFile, user_id: str) -> dict:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")
    try:
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        
        if not text.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No text content found in PDF")
        
        # Store full text as single entry
        full_text = text.strip()
        embedding = await generate_embedding(full_text)
        embedding_str = f"[{','.join(str(x) for x in embedding)}]" if embedding else None
        
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO training_data (project_id, user_id, content, type, file_name, metadata, embeddings, created_at)
                   VALUES (%s, %s, %s, 'pdf', %s, %s, %s::vector, NOW())
                   RETURNING id, project_id, user_id, content, type, file_name, metadata, created_at""",
                (project_id, user_id, full_text, file.filename, f'{{"pages": {len(pdf_reader.pages)}}}', embedding_str),
            )
            training = cur.fetchone()
            conn.commit()
            cur.close()
            return TrainingData.from_row(training).to_dict()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid PDF file: {str(e)}")


def list(project_id: str, user_id: str) -> List[dict]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, project_id, user_id, content, type, file_name, metadata, created_at
               FROM training_data WHERE user_id = %s AND project_id = %s ORDER BY created_at DESC""",
            (user_id, project_id),
        )
        rows = cur.fetchall()
        cur.close()
        return [TrainingData.from_row(r).to_dict() for r in rows]
    finally:
        conn.close()


def delete(training_id: str, user_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM training_data WHERE id = %s AND user_id = %s", (training_id, user_id))
        conn.commit()
        cur.close()
    finally:
        conn.close()


async def find_relevant(user_id: str, project_id: str, query: str, top_k: int = 5) -> List[dict]:
    return await find_relevant_chunks_from_db(user_id, project_id, query, top_k)
