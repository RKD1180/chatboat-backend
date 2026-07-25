from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import settings
from config.database import get_connection

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, email, display_name, avatar_url, created_at, updated_at FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return {
            "id": row[0],
            "email": row[1],
            "display_name": row[2],
            "avatar_url": row[3],
            "created_at": row[4],
            "updated_at": row[5],
        }
    finally:
        conn.close()
