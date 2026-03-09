from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/")
def root():
    return {"message": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/health")
def health_check():
    return {"status": "healthy"}
