from fastapi import APIRouter
from app.api.endpoints import auth, users

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(users.router, prefix="/users", tags=["users"])