import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import api_router

app = FastAPI(title="Chatbot Backend", version="1.0.0")

# CORS - Support multiple frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Chatbot Backend API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
