from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .database import Base, engine
from .routers import health, cameras, incidents, analyze
from .config import SNAPSHOT_DIR, UPLOAD_DIR

Base.metadata.create_all(bind=engine)

app = FastAPI(title="VisionGuard AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(SNAPSHOT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="."), name="static")

app.include_router(health.router)
app.include_router(cameras.router)
app.include_router(incidents.router)
app.include_router(analyze.router)
