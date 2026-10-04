from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .database import Base, engine
from fastapi import WebSocket, WebSocketDisconnect
from .routers import health, cameras, incidents, analyze, zones, analytics, auth as auth_router
from .services.ws import manager
from .services import auth
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
app.include_router(zones.router)
app.include_router(analytics.router)
app.include_router(auth_router.router)

from .database import SessionLocal

with SessionLocal() as _db:
    auth.seed_admin(_db)


@app.websocket("/ws/incidents")
async def ws_incidents(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
