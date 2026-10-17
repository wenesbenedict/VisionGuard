"""Potential-fall heuristic based on temporal bounding-box aspect ratios."""

from collections import defaultdict, deque
from typing import Deque

NORMAL_RATIO = 1.5
FALLBACK_RATIO = 1.1


class FallTracker:
    """Track fall heuristics for one analyzed video, not process-global IDs."""

    def __init__(self) -> None:
        self._history: dict[int, Deque[tuple[float, float]]] = defaultdict(
            lambda: deque(maxlen=10)
        )
        self._fall_reported: dict[int, bool] = defaultdict(bool)

    def check_falls(self, persons, now: float) -> list[dict]:
        falls = []
        seen = set()
        for person in persons:
            track_id = person.get("track_id")
            if track_id is None:
                continue
            width = max(person["bbox"][2] - person["bbox"][0], 1e-6)
            height = max(person["bbox"][3] - person["bbox"][1], 1e-6)
            ratio = height / width
            history = self._history[track_id]
            history.append((now, ratio))
            seen.add(track_id)

            if len(history) >= 2 and not self._fall_reported[track_id]:
                previous_ratios = [value for _, value in list(history)[:-1]]
                was_upright = any(value >= NORMAL_RATIO for value in previous_ratios)
                currently_horizontal = all(
                    value <= FALLBACK_RATIO for _, value in list(history)[-2:]
                )
                if was_upright and currently_horizontal:
                    self._fall_reported[track_id] = True
                    falls.append({"person": person, "ratio": ratio})

        for track_id in list(self._history):
            if track_id not in seen:
                del self._history[track_id]
                self._fall_reported.pop(track_id, None)
        return falls


# Compatibility wrapper for callers outside the video-analysis route.
_default_tracker = FallTracker()


def check_falls(persons, now: float) -> list[dict]:
    return _default_tracker.check_falls(persons, now)
