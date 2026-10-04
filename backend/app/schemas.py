from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class CameraBase(BaseModel):
    name: str
    source: str
    location: str = ""
    status: str = "ONLINE"


class CameraCreate(CameraBase):
    pass


class CameraOut(CameraBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentOut(BaseModel):
    id: int
    camera_id: Optional[int]
    type: str
    severity: str
    confidence: float
    tracking_id: Optional[str]
    description: str
    snapshot_url: Optional[str]
    video_url: Optional[str]
    ai_summary: Optional[str]
    status: str
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentStatusUpdate(BaseModel):
    status: str


class DetectionEventOut(BaseModel):
    id: int
    camera_id: Optional[int]
    tracking_id: Optional[str]
    object_type: str
    confidence: float
    bbox: Optional[List[float]]
    timestamp: datetime

    class Config:
        from_attributes = True


class AnalysisResult(BaseModel):
    camera_id: int
    frames_processed: int
    persons_detected: int
    incidents_created: int
    incident_ids: List[int]
