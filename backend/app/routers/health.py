import os

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..config import PPE_MODEL
from ..database import engine

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {
        "status": "ok",
        "database": "ok",
        "ppe_model_weights_available": os.path.isfile(PPE_MODEL),
    }
