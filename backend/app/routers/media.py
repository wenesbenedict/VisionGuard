from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from .. import models
from ..config import SNAPSHOT_DIR, UPLOAD_DIR
from ..services import auth

router = APIRouter(prefix="/api/media", tags=["media"])


@router.get("/{media_type}/{filename}")
def get_media(
    media_type: str,
    filename: str,
    user: models.User = Depends(auth.get_current_user),
):
    directories = {"snapshots": SNAPSHOT_DIR, "uploads": UPLOAD_DIR}
    root_value = directories.get(media_type)
    if not root_value or Path(filename).name != filename:
        raise HTTPException(status_code=404, detail="Media not found")

    root = Path(root_value).resolve()
    target = (root / filename).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=404, detail="Media not found")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(target)
