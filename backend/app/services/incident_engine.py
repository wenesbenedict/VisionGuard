"""Incident engine: converts raw detections into structured safety incidents."""

from typing import List

from sqlalchemy.orm import Session

from .. import models


def create_ppe_violation(db: Session, camera_id: int, violation, frame,
                         snapshot_path, video_path) -> models.Incident:
    missing = ", ".join(violation["missing"])
    incident = models.Incident(
        camera_id=camera_id,
        type="PPE_VIOLATION",
        severity="MEDIUM",
        confidence=violation["person"]["confidence"],
        description=f"Worker detected without required PPE: {missing}",
        snapshot_url=snapshot_path,
        video_url=video_path,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def store_detections(db: Session, camera_id: int, persons) -> None:
    for p in persons:
        db.add(models.DetectionEvent(
            camera_id=camera_id,
            object_type="person",
            confidence=p["confidence"],
            bbox=p["bbox"],
        ))
    db.commit()
