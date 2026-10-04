from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import auth

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


@router.get("", response_model=List[schemas.CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(models.Camera).all()


@router.post("", response_model=schemas.CameraOut)
def create_camera(
    cam: schemas.CameraCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.require_role("ADMIN", "SAFETY_OFFICER")),
):
    camera = models.Camera(**cam.model_dump())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.delete("/{camera_id}")
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.require_role("ADMIN")),
):
    camera = db.get(models.Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    db.delete(camera)
    db.commit()
    return {"deleted": camera_id}
