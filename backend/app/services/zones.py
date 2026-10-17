"""Restricted-zone monitoring with a video-time dwell threshold."""

import time

from sqlalchemy.orm import Session

from .. import models

DWELL_SECONDS = 3.0


def point_in_polygon(px: float, py: float, polygon: list[list[float]]) -> bool:
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (
            px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


class ZoneTracker:
    """Dwell timers scoped to one video analysis request."""

    def __init__(self) -> None:
        self._timers: dict[tuple[int, int], tuple[float, bool]] = {}

    def zone_breaches(
        self,
        db: Session,
        camera_id: int,
        persons,
        now: float | None = None,
    ) -> list[dict]:
        camera_zones = db.query(models.SafetyZone).filter(
            models.SafetyZone.camera_id == camera_id
        ).all()
        breaches = []
        if now is None:
            now = time.time()
        for zone in camera_zones:
            if not zone.coordinates or len(zone.coordinates) < 3:
                continue
            inside_now = set()
            for person in persons:
                track_id = person.get("track_id")
                if track_id is None:
                    continue
                center_x = (person["bbox"][0] + person["bbox"][2]) / 2
                center_y = (person["bbox"][1] + person["bbox"][3]) / 2
                if point_in_polygon(center_x, center_y, zone.coordinates):
                    key = (zone.id, track_id)
                    entry, breached = self._timers.get(key, (0.0, False))
                    if entry == 0.0:
                        entry, breached = now, False
                        self._timers[key] = (entry, breached)
                    inside_now.add(key)
                    if not breached and now - entry >= DWELL_SECONDS:
                        self._timers[key] = (entry, True)
                        breaches.append({
                            "zone": zone,
                            "person": person,
                            "duration": now - entry,
                        })
            for key in [key for key in self._timers if key[0] == zone.id and key not in inside_now]:
                del self._timers[key]
        return breaches


# Compatibility wrapper for callers outside the video-analysis route.
_default_tracker = ZoneTracker()


def zone_breaches(db: Session, camera_id: int, persons, now: float | None = None) -> list[dict]:
    return _default_tracker.zone_breaches(db, camera_id, persons, now)
