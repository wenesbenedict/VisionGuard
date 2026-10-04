import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://visionguard:visionguard@localhost:5432/visionguard",
)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
SNAPSHOT_DIR = os.getenv("SNAPSHOT_DIR", "snapshots")
PERSON_MODEL = os.getenv("PERSON_MODEL", "yolov8n.pt")
PPE_MODEL = os.getenv("PPE_MODEL", "ppe.pt")  # custom PPE weights if present
FRAME_SAMPLE_RATE = int(os.getenv("FRAME_SAMPLE_RATE", "10"))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.4"))
