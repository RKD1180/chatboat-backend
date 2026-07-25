import os
import uuid
from fastapi import HTTPException, status, UploadFile
from config.database import get_connection
from modules.files.model import File

UPLOAD_DIR = "uploads"


async def upload(project_id: str, file: UploadFile, user_id: str) -> dict:
    if os.environ.get("VERCEL"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File upload not supported on Vercel")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    try:
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_name = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO files (project_id, user_id, name, original_name, mime_type, size, path, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                   RETURNING id, project_id, user_id, name, original_name, mime_type, size, path, created_at""",
                (project_id, user_id, unique_name, file.filename, file.content_type, len(content), file_path),
            )
            file_record = cur.fetchone()
            conn.commit()
            cur.close()
            return File.from_row(file_record).to_dict()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def list(project_id: str, user_id: str) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, project_id, user_id, name, original_name, mime_type, size, path, created_at
               FROM files WHERE user_id = %s AND project_id = %s ORDER BY created_at DESC""",
            (user_id, project_id),
        )
        rows = cur.fetchall()
        cur.close()
        return [File.from_row(r).to_dict() for r in rows]
    finally:
        conn.close()


def delete(file_id: str, user_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT path FROM files WHERE id = %s AND user_id = %s", (file_id, user_id))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
        file_path = row[0]
        if os.path.exists(file_path):
            os.remove(file_path)
        
        cur.execute("DELETE FROM files WHERE id = %s AND user_id = %s", (file_id, user_id))
        conn.commit()
        cur.close()
    finally:
        conn.close()
