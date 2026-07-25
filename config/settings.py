import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "raton1234")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRES_IN = int(os.getenv("JWT_EXPIRES_IN", "7"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", "8000"))
ENV = os.getenv("ENV", "development")

# Support multiple frontend URLs (comma-separated)
FRONTEND_URLS = os.getenv("FRONTEND_URLS", "http://localhost:3000").split(",")

# For backward compatibility
FRONTEND_URL = FRONTEND_URLS[0] if FRONTEND_URLS else "http://localhost:3000"
