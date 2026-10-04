from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON,
)
from sqlalchemy.orm import relationship

from .database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source = Column(String, nullable=False)  # upload path, webcam index, RTSP
    location = Column(String, default="")
    status = Column(String, default="ONLINE")
    created_at = Column(DateTime, default=datetime.utcnow)

    incidents = relationship("Incident", back_populates="camera")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    type = Column(String, nullable=False)  # PPE_VIOLATION, ZONE_BREACH, FALL
    severity = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH
    confidence = Column(Float, default=0.0)
    tracking_id = Column(String, nullable=True)
    description = Column(Text, default="")
    snapshot_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    ai_summary = Column(Text, nullable=True)
    status = Column(String, default="OPEN")  # OPEN, UNDER_REVIEW, RESOLVED
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    camera = relationship("Camera", back_populates="incidents")


class SafetyZone(Base):
    __tablename__ = "safety_zones"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    name = Column(String, nullable=False)
    zone_type = Column(String, default="RESTRICTED")
    coordinates = Column(JSON)  # list of [x, y] points
    created_at = Column(DateTime, default=datetime.utcnow)


class DetectionEvent(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    tracking_id = Column(String, nullable=True)
    object_type = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    bbox = Column(JSON)  # [x1, y1, x2, y2]
    timestamp = Column(DateTime, default=datetime.utcnow)
