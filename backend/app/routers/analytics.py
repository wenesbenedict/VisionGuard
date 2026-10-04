from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    incidents = db.query(models.Incident).all()
    today = datetime.utcnow().date()
    today_count = sum(1 for i in incidents if i.timestamp.date() == today)
    by_type = Counter(i.type for i in incidents)
    by_severity = Counter(i.severity for i in incidents)
    by_status = Counter(i.status for i in incidents)
    by_camera = Counter()
    for i in incidents:
        cam = db.get(models.Camera, i.camera_id) if i.camera_id else None
        by_camera[cam.name if cam else "Unknown"] += 1
    return {
        "total": len(incidents),
        "today": today_count,
        "by_type": dict(by_type),
        "by_severity": dict(by_severity),
        "by_status": dict(by_status),
        "by_camera": dict(by_camera),
    }


@router.get("/incidents")
def incidents_over_time(db: Session = Depends(get_db), days: int = 7):
    since = datetime.utcnow() - timedelta(days=days)
    incidents = (
        db.query(models.Incident)
        .filter(models.Incident.timestamp >= since)
        .all()
    )
    by_day = Counter(i.timestamp.strftime("%Y-%m-%d") for i in incidents)
    return [{"date": d, "count": by_day.get(d, 0)} for d in sorted(by_day)]
