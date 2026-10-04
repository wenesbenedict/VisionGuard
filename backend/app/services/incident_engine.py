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
        tracking_id=(
            str(violation["person"]["track_id"])
            if violation["person"].get("track_id") is not None
            else None
        ),
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
            tracking_id=str(p["track_id"]) if p.get("track_id") is not None else None,
        ))
    db.commit()


def create_zone_breach(db: Session, camera_id: int, breach, snapshot_path,
                       video_path) -> models.Incident:
    incident = models.Incident(
        camera_id=camera_id,
        type="ZONE_BREACH",
        severity="HIGH",
        confidence=breach["person"]["confidence"],
        tracking_id=str(breach["person"]["track_id"]),
        description=(
            f"Person #{breach['person']['track_id']} entered restricted zone "
            f"'{breach['zone'].name}' for {breach['duration']:.1f}s"
        ),
        snapshot_url=snapshot_path,
        video_url=video_path,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
