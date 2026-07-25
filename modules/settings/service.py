from fastapi import HTTPException, status
from config.database import get_connection
from modules.settings.model import Settings
from modules.settings.schema import SettingsUpdate, ProfileUpdate


def get_settings(user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user_id, theme, language, notifications, created_at, updated_at FROM settings WHERE user_id = %s",
            (user_id,),
        )
        settings_row = cur.fetchone()
        cur.close()
        
        if not settings_row:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO settings (user_id, theme, language, notifications, created_at, updated_at)
                   VALUES (%s, 'dark', 'en', true, NOW(), NOW())
                   RETURNING id, user_id, theme, language, notifications, created_at, updated_at""",
                (user_id,),
            )
            settings_row = cur.fetchone()
            conn.commit()
            cur.close()
        
        return Settings.from_row(settings_row).to_dict()
    finally:
        conn.close()


def update_settings(data: SettingsUpdate, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM settings WHERE user_id = %s", (user_id,))
        if not cur.fetchone():
            cur.execute(
                """INSERT INTO settings (user_id, theme, language, notifications, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, NOW(), NOW())""",
                (user_id, data.theme or "dark", data.language or "en", data.notifications if data.notifications is not None else True),
            )
        
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        if updates:
            updates["updated_at"] = "NOW()"
            set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
            values = list(updates.values()) + [user_id]
            cur.execute(
                f"""UPDATE settings SET {set_clause}
                    WHERE user_id = %s
                    RETURNING id, user_id, theme, language, notifications, created_at, updated_at""",
                values,
            )
        
        settings_row = cur.fetchone()
        conn.commit()
        cur.close()
        return Settings.from_row(settings_row).to_dict()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()


def get_profile(user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, email, display_name, created_at FROM users WHERE id = %s", (user_id,))
        user_row = cur.fetchone()
        cur.close()
        if not user_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {
            "id": user_row[0],
            "email": user_row[1],
            "name": user_row[2] or user_row[1].split("@")[0],
            "createdAt": str(user_row[3]),
        }
    finally:
        conn.close()


def update_profile(data: ProfileUpdate, user_id: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        if not updates:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
        
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        values = list(updates.values()) + [user_id]
        
        cur.execute(
            f"""UPDATE users SET {set_clause}
                WHERE id = %s
                RETURNING id, email, display_name, created_at""",
            values,
        )
        user_row = cur.fetchone()
        conn.commit()
        cur.close()
        
        return {
            "id": user_row[0],
            "email": user_row[1],
            "name": user_row[2] or user_row[1].split("@")[0],
            "createdAt": str(user_row[3]),
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()
