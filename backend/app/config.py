import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./visionguard.db",
)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
SNAPSHOT_DIR = os.getenv("SNAPSHOT_DIR", "snapshots")
PERSON_MODEL = os.getenv("PERSON_MODEL", "yolov8n.pt")
PPE_MODEL = os.getenv("PPE_MODEL", "ppe.pt")  # custom PPE weights if present
FRAME_SAMPLE_RATE = int(os.getenv("FRAME_SAMPLE_RATE", "10"))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.4"))
JWT_SECRET = os.getenv("JWT_SECRET", "")
CORS_ALLOWED_ORIGINS = tuple(
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
)
MAX_VIDEO_SIZE_BYTES = int(os.getenv("MAX_VIDEO_SIZE_BYTES", str(500 * 1024 * 1024)))
