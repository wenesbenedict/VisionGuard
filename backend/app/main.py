from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ALLOWED_ORIGINS
from .database import Base, SessionLocal, engine
from .routers import (
    analytics,
    analyze,
    auth as auth_router,
    cameras,
    health,
    incidents,
    media,
    zones,
)
from .services import auth
from .services.ws import manager

# Fail closed rather than issue tokens signed with a public development key.
auth.validate_secret()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VisionGuard AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router)
app.include_router(cameras.router)
app.include_router(incidents.router)
app.include_router(analyze.router)
app.include_router(zones.router)
app.include_router(analytics.router)
app.include_router(auth_router.router)
app.include_router(media.router)


@app.websocket("/ws/incidents")
async def ws_incidents(websocket: WebSocket):
    token = auth.websocket_token(
        websocket.headers.get("sec-websocket-protocol", "")
    )
    if not token:
        await websocket.close(code=1008)
        return
    try:
        with SessionLocal() as db:
            auth.get_user_from_token(db, token)
    except HTTPException:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, subprotocol="visionguard")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
