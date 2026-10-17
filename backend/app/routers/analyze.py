import os
import shutil
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import MAX_VIDEO_SIZE_BYTES, UPLOAD_DIR
from ..database import SessionLocal, get_db
from ..services import auth, detector, fall, incident_engine, zones
from ..services.ai_summary import summarize_incident
from ..services.ws import manager

router = APIRouter(prefix="/api/analyze", tags=["analyze"])
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".mpeg", ".mpg"}
UPLOAD_CHUNK_BYTES = 1024 * 1024


def _summarize(incident_ids):
    db = SessionLocal()
    try:
        for iid in incident_ids:
            inc = db.get(models.Incident, iid)
            if inc and not inc.ai_summary:
                inc.ai_summary = summarize_incident(inc)
                db.commit()
    finally:
        db.close()


async def _store_upload(file: UploadFile) -> str:
    suffix = os.path.splitext(file.filename or "")[1].lower()
    if suffix not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported video file extension")
    content_type = (file.content_type or "").lower()
    if content_type and not (content_type.startswith("video/") or content_type == "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Upload must be a video")
    if MAX_VIDEO_SIZE_BYTES <= 0:
        raise HTTPException(status_code=500, detail="Video upload limit is not configured")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{suffix}")
    total = 0
    try:
        with open(path, "wb") as destination:
            while chunk := await file.read(UPLOAD_CHUNK_BYTES):
                total += len(chunk)
                if total > MAX_VIDEO_SIZE_BYTES:
                    raise HTTPException(status_code=413, detail="Video exceeds the upload size limit")
                destination.write(chunk)
        if total == 0:
            raise HTTPException(status_code=400, detail="Uploaded video is empty")
    except Exception:
        if os.path.exists(path):
            os.remove(path)
        raise
    return path


@router.post("/video", response_model=schemas.AnalysisResult)
async def analyze_video(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    camera_id: int = Form(...),
    db: Session = Depends(get_db),
    user=Depends(auth.require_role("ADMIN", "SAFETY_OFFICER")),
):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            request_size = int(content_length)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Content-Length")
        if request_size > MAX_VIDEO_SIZE_BYTES + 1024 * 1024:
            raise HTTPException(status_code=413, detail="Video exceeds the upload size limit")
    if not db.get(models.Camera, camera_id):
        raise HTTPException(status_code=404, detail="Camera not found")

    path = await _store_upload(file)
    try:
        detector.validate_video(path)
    except ValueError:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=422, detail="Uploaded file is not a decodable video")
    frames_processed = 0
    persons_total = 0
    incident_ids = []
    fall_tracker = fall.FallTracker()
    zone_tracker = zones.ZoneTracker()

    try:
        for t, frame, dets, violations in detector.analyze_video(path):
            frames_processed += 1
            persons_total += len(dets["persons"])
            incident_engine.store_detections(db, camera_id, dets["persons"])

            for fall_event in fall_tracker.check_falls(dets["persons"], now=t):
                snapshot = detector.save_snapshot(frame, prefix=f"fall{camera_id}")
                clip = detector.save_clip(path, t)
                inc = incident_engine.create_fall_incident(
                    db, camera_id, fall_event, snapshot, clip,
                )
                incident_ids.append(inc.id)
                await manager.broadcast({
                    "event": "incident", "id": inc.id, "type": inc.type,
                    "severity": inc.severity, "description": inc.description,
                    "timestamp": str(inc.timestamp),
                })

            for breach in zone_tracker.zone_breaches(db, camera_id, dets["persons"], now=t):
                snapshot = detector.save_snapshot(frame, prefix=f"zone{camera_id}")
                clip = detector.save_clip(path, t)
                inc = incident_engine.create_zone_breach(
                    db, camera_id, breach, snapshot, clip,
                )
                incident_ids.append(inc.id)
                await manager.broadcast({
                    "event": "incident", "id": inc.id, "type": inc.type,
                    "severity": inc.severity, "description": inc.description,
                    "timestamp": str(inc.timestamp),
                })

            for violation in violations:
                snapshot = detector.save_snapshot(frame, prefix=f"cam{camera_id}")
                clip = detector.save_clip(path, t)
                inc = incident_engine.create_ppe_violation(
                    db, camera_id, violation, frame, snapshot, clip,
                )
                incident_ids.append(inc.id)
                await manager.broadcast({
                    "event": "incident", "id": inc.id, "type": inc.type,
                    "severity": inc.severity, "description": inc.description,
                    "timestamp": str(inc.timestamp),
                })
    except ValueError as exc:
        raise HTTPException(status_code=500, detail="Video processing failed") from exc

    if incident_ids:
        background_tasks.add_task(_summarize, incident_ids)

    return schemas.AnalysisResult(
        camera_id=camera_id,
        frames_processed=frames_processed,
        persons_detected=persons_total,
        incidents_created=len(incident_ids),
        incident_ids=incident_ids,
        ppe_detection_active=detector.ppe_detection_active(),
    )
