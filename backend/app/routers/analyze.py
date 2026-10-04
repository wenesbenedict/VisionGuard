import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import UPLOAD_DIR
from ..database import get_db
from ..services import detector, incident_engine, zones
from ..services.ws import manager

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("/video", response_model=schemas.AnalysisResult)
async def analyze_video(
    file: UploadFile = File(...),
    camera_id: int = Form(...),
    db: Session = Depends(get_db),
):
    if not db.get(models.Camera, camera_id):
        raise HTTPException(status_code=404, detail="Camera not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "video.mp4")[1] or ".mp4"
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    frames_processed = 0
    persons_total = 0
    incident_ids = []

    for t, frame, dets, violations in detector.analyze_video(path):
        frames_processed += 1
        persons_total += len(dets["persons"])
        incident_engine.store_detections(db, camera_id, dets["persons"])

        for b in zones.zone_breaches(db, camera_id, dets["persons"], now=t):
            snapshot = detector.save_snapshot(frame, prefix=f"zone{camera_id}")
            inc = incident_engine.create_zone_breach(
                db, camera_id, b, snapshot, path,
            )
            incident_ids.append(inc.id)
            await manager.broadcast({
                "event": "incident",
                "id": inc.id,
                "type": inc.type,
                "severity": inc.severity,
                "description": inc.description,
                "timestamp": str(inc.timestamp),
            })

        for v in violations:
            snapshot = detector.save_snapshot(frame, prefix=f"cam{camera_id}")
            inc = incident_engine.create_ppe_violation(
                db, camera_id, v, frame, snapshot, path,
            )
            incident_ids.append(inc.id)
            await manager.broadcast({
                "event": "incident",
                "id": inc.id,
                "type": inc.type,
                "severity": inc.severity,
                "description": inc.description,
                "timestamp": str(inc.timestamp),
            })

    return schemas.AnalysisResult(
        camera_id=camera_id,
        frames_processed=frames_processed,
        persons_detected=persons_total,
        incidents_created=len(incident_ids),
        incident_ids=incident_ids,
    )
