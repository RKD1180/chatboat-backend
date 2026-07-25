import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
from config.database import run_migrations
from routes import api_router

# Run migrations on startup
run_migrations()

app = FastAPI(title="Chatbot Backend", version="1.0.0")

# CORS - Support multiple frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
