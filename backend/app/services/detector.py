import logging
import os
from datetime import datetime
from typing import List, Dict, Any

import cv2

from ..config import (
    PERSON_MODEL, PPE_MODEL, FRAME_SAMPLE_RATE, MIN_CONFIDENCE,
    SNAPSHOT_DIR,
)

logger = logging.getLogger(__name__)

_person_model = None
_ppe_model = None


def _load_model(path):
    try:
        from ultralytics import YOLO
        return YOLO(path)
    except Exception as exc:
        logger.error("Failed to load model %s: %s", path, exc)
        return None


def get_models():
    global _person_model, _ppe_model
    if _person_model is None:
        _person_model = _load_model(PERSON_MODEL)
    if _ppe_model is None and os.path.exists(PPE_MODEL):
        _ppe_model = _load_model(PPE_MODEL)
    return _person_model, _ppe_model


def _bbox(det) -> List[float]:
    return [float(v) for v in det.xyxy[0].tolist()]


def detect_frame(frame) -> Dict[str, List[Dict[str, Any]]]:
    person_model, ppe_model = get_models()
    persons, helmets, vests = [], [], []

    if person_model is not None:
        results = person_model.track(
            frame, persist=True, tracker="bytetrack.yaml", verbose=False
        )
        for r in results:
            for det in r.boxes:
                cls = int(det.cls[0])
                label = person_model.names.get(cls, str(cls))
                conf = float(det.conf[0])
                if conf < MIN_CONFIDENCE:
                    continue
                if label == "person":
                    tid = int(det.id[0]) if det.id is not None else None
                    persons.append({
                        "bbox": _bbox(det),
                        "confidence": conf,
                        "track_id": tid,
                    })

    if ppe_model is not None:
        results = ppe_model(frame, verbose=False)
        for r in results:
            for det in r.boxes:
                cls = int(det.cls[0])
                label = ppe_model.names.get(cls, str(cls)).lower()
                conf = float(det.conf[0])
                if conf < MIN_CONFIDENCE:
                    continue
                item = {"bbox": _bbox(det), "confidence": conf}
                if "helmet" in label or "hardhat" in label:
                    helmets.append(item)
                elif "vest" in label:
                    vests.append(item)

    return {"persons": persons, "helmets": helmets, "vests": vests}


def _center(bbox):
    return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)


def _overlaps(person_bbox, item_bbox):
    """True if item bbox center lies within the person bbox."""
    cx, cy = _center(item_bbox)
    return (
        person_bbox[0] <= cx <= person_bbox[2]
        and person_bbox[1] <= cy <= person_bbox[3]
    )


def evaluate_ppe(persons, helmets, vests) -> List[Dict[str, Any]]:
    """Return a violation dict for each person missing required PPE."""
    violations = []
    has_ppe_model = get_models()[1] is not None
    for p in persons:
        missing = []
        if has_ppe_model:
            if not any(_overlaps(p["bbox"], h["bbox"]) for h in helmets):
                missing.append("helmet")
            if not any(_overlaps(p["bbox"], v["bbox"]) for v in vests):
                missing.append("vest")
        if missing:
            violations.append({"person": p, "missing": missing})
    return violations


def analyze_video(video_path: str):
    """Yield (frame_index, frame, detections, violations) for sampled frames."""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    idx = 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            idx += 1
            if idx % FRAME_SAMPLE_RATE != 0:
                continue
            dets = detect_frame(frame)
            violations = evaluate_ppe(
                dets["persons"], dets["helmets"], dets["vests"]
            )
            yield idx / fps, frame, dets, violations
    finally:
        cap.release()


def save_snapshot(frame, prefix: str = "incident") -> str:
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    name = f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    path = os.path.join(SNAPSHOT_DIR, name)
    cv2.imwrite(path, frame)
    return path


def save_clip(video_path: str, center_t: float, half: float = 2.0) -> str:
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    name = f"clip_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.mp4"
    out_path = os.path.join(SNAPSHOT_DIR, name)
    out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    start = max(0.0, center_t - half)
    end = center_t + half
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if t > end:
            break
        out.write(frame)
    cap.release()
    out.release()
    return out_path
