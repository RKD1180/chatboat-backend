from fastapi import HTTPException, status
from config.database import get_connection
from config.response import PaginatedData
from modules.projects.model import Project
from modules.projects.schema import ProjectCreate, ProjectUpdate


def create(data: ProjectCreate, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO projects (name, description, model, user_id, created_at, updated_at)
               VALUES (%s, %s, %s, %s, NOW(), NOW())
               RETURNING id, name, description, model, user_id, created_at, updated_at""",
            (data.name, data.description, data.model, user_id),
        )
        project = cur.fetchone()
        conn.commit()
        cur.close()
        return Project.from_row(project).to_dict()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()


def list(user_id: str, page: int = 1, limit: int = 10) -> PaginatedData:
    conn = get_connection()
    try:
        cur = conn.cursor()
        offset = (page - 1) * limit
        cur.execute("SELECT COUNT(*) FROM projects WHERE user_id = %s", (user_id,))
        total = cur.fetchone()[0]
        cur.execute(
            """SELECT id, name, description, model, user_id, created_at, updated_at
               FROM projects WHERE user_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s""",
            (user_id, limit, offset),
        )
        projects = cur.fetchall()
        cur.close()
        return PaginatedData(
            data=[Project.from_row(p).to_dict() for p in projects],
            total=total,
            page=page,
            limit=limit,
            totalPages=(total + limit - 1) // limit,
        )
    finally:
        conn.close()


def get(project_id: str, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, description, model, user_id, created_at, updated_at FROM projects WHERE id = %s AND user_id = %s",
            (project_id, user_id),
        )
        project = cur.fetchone()
        cur.close()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return Project.from_row(project).to_dict()
    finally:
        conn.close()


def update(project_id: str, data: ProjectUpdate, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        updates = []
        values = []
        for field, value in data.model_dump(exclude_none=True).items():
            updates.append(f"{field} = %s")
            values.append(value)
        updates.append("updated_at = NOW()")
        values.extend([project_id, user_id])
        cur.execute(
            f"""UPDATE projects SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
                RETURNING id, name, description, model, user_id, created_at, updated_at""",
            values,
        )
        project = cur.fetchone()
        conn.commit()
        cur.close()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return Project.from_row(project).to_dict()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()


def delete(project_id: str, user_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM projects WHERE id = %s AND user_id = %s", (project_id, user_id))
        conn.commit()
        cur.close()
    finally:
        conn.close()
