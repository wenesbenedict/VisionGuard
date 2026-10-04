"""Fall detection: temporal bbox posture analysis per track."""

from collections import defaultdict, deque
from typing import Deque, Dict, List, Tuple

# track_id -> deque of (timestamp, aspect_ratio=height/width)
_history: Dict[int, Deque[Tuple[float, float]]] = defaultdict(
    lambda: deque(maxlen=10)
)
_fall_reported: Dict[int, bool] = defaultdict(bool)

NORMAL_RATIO = 1.5
FALLBACK_RATIO = 1.1


def check_falls(persons, now: float) -> List[dict]:
    falls = []
    seen = set()
    for p in persons:
        if p.get("track_id") is None:
            continue
        w = max(p["bbox"][2] - p["bbox"][0], 1e-6)
        h = max(p["bbox"][3] - p["bbox"][1], 1e-6)
        ratio = h / w
        hist = _history[p["track_id"]]
        hist.append((now, ratio))
        seen.add(p["track_id"])

        if len(hist) >= 2 and not _fall_reported[p["track_id"]]:
            prev_ratios = [r for _, r in list(hist)[:-1]]
            was_normal = any(r >= NORMAL_RATIO for r in prev_ratios)
            horizontal_now = all(r <= FALLBACK_RATIO for _, r in list(hist)[-2:])
            if was_normal and horizontal_now:
                _fall_reported[p["track_id"]] = True
                falls.append({"person": p, "ratio": ratio})

    for tid in list(_history.keys()):
        if tid not in seen:
            del _history[tid]
            _fall_reported.pop(tid, None)

    return falls
