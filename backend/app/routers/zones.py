from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/zones", tags=["zones"])


@router.get("", response_model=List[schemas.SafetyZoneOut])
def list_zones(camera_id: int = None, db: Session = Depends(get_db)):
    q = db.query(models.SafetyZone)
    if camera_id is not None:
        q = q.filter(models.SafetyZone.camera_id == camera_id)
    return q.all()


@router.post("", response_model=schemas.SafetyZoneOut)
def create_zone(zone: schemas.SafetyZoneCreate, db: Session = Depends(get_db)):
    if not db.get(models.Camera, zone.camera_id):
        raise HTTPException(status_code=404, detail="Camera not found")
    z = models.SafetyZone(**zone.model_dump())
    db.add(z)
    db.commit()
    db.refresh(z)
    return z


@router.delete("/{zone_id}")
def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    z = db.get(models.SafetyZone, zone_id)
    if not z:
        raise HTTPException(status_code=404, detail="Zone not found")
    db.delete(z)
    db.commit()
    return {"deleted": zone_id}
