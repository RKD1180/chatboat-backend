from fastapi import APIRouter
from modules.auth.route import router as auth_router
from modules.projects.route import router as projects_router
from modules.training.route import router as training_router
from modules.chat.route import router as chat_router
from modules.prompts.route import router as prompts_router
from modules.files.route import router as files_router
from modules.settings.route import router as settings_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(training_router)
api_router.include_router(chat_router)
api_router.include_router(prompts_router)
api_router.include_router(files_router)
api_router.include_router(settings_router)
