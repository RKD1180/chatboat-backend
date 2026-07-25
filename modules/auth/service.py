from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import jwt, JWTError
import psycopg2
from config import settings
from config.database import get_connection
from modules.auth.model import User
from modules.auth.schema import RegisterRequest, LoginRequest, RefreshRequest


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRES_IN)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def register(data: RegisterRequest) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO users (email, display_name, created_at, updated_at) 
               VALUES (%s, %s, NOW(), NOW()) 
               RETURNING id, email, display_name, created_at, updated_at""",
            (data.email, data.name or data.email.split("@")[0]),
        )
        user_row = cur.fetchone()
        conn.commit()
        user = User.from_row(user_row)
        access_token = create_access_token(user.id)
        return {
            "user": user.to_dict(),
            "tokens": {
                "accessToken": access_token,
                "refreshToken": access_token,
            },
        }
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(e)}")
    finally:
        cur.close()
        conn.close()


def login(data: LoginRequest) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, display_name, created_at, updated_at FROM users WHERE email = %s",
            (data.email,),
        )
        user_row = cur.fetchone()
        cur.close()
        if not user_row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user = User.from_row(user_row)
        access_token = create_access_token(user.id)
        return {
            "user": user.to_dict(),
            "tokens": {
                "accessToken": access_token,
                "refreshToken": access_token,
            },
        }
    finally:
        conn.close()


def refresh_token(data: RefreshRequest) -> dict:
    try:
        payload = jwt.decode(data.refreshToken, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        access_token = create_access_token(user_id)
        return {
            "accessToken": access_token,
            "refreshToken": access_token,
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_profile(user: dict) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, display_name, created_at, updated_at FROM users WHERE id = %s",
            (user["id"],),
        )
        user_row = cur.fetchone()
        cur.close()
        if not user_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return User.from_row(user_row).to_dict()
    finally:
        conn.close()
