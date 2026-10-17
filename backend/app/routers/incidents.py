from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import auth

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=List[schemas.IncidentOut])
def list_incidents(
    camera_id: Optional[int] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    q = db.query(models.Incident)
    if camera_id is not None:
        q = q.filter(models.Incident.camera_id == camera_id)
    if type:
        q = q.filter(models.Incident.type == type)
    if status:
        q = q.filter(models.Incident.status == status)
    return q.order_by(models.Incident.timestamp.desc()).all()


@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    incident = db.get(models.Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}/status", response_model=schemas.IncidentOut)
def update_status(incident_id: int, body: schemas.IncidentStatusUpdate,
                  db: Session = Depends(get_db),
                  user: models.User = Depends(auth.require_role("ADMIN", "SAFETY_OFFICER", "SUPERVISOR"))):
    incident = db.get(models.Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if body.status not in ("OPEN", "UNDER_REVIEW", "RESOLVED"):
        raise HTTPException(status_code=400, detail="Invalid status")
    incident.status = body.status
    db.commit()
    db.refresh(incident)
    return incident
