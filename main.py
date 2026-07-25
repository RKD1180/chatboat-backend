import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
from routes import api_router

# Only run migrations in non-Vercel environment
if not os.environ.get("VERCEL"):
    try:
        from config.database import run_migrations
        run_migrations()
    except Exception as e:
        print(f"Migration warning: {e}")

app = FastAPI(title="Chatbot Backend", version="1.0.0")

# CORS - Support multiple frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files (only in non-Vercel environment)
if not os.environ.get("VERCEL"):
    os.makedirs("uploads", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Chatbot Backend API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.ENV == "development")
