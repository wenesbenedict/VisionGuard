"""Restricted-zone monitoring with dwell-time rule."""

import time
from collections import defaultdict
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from .. import models

# (zone_id, track_id) -> (entry_epoch, breached_flag)
_zone_timers: Dict[Tuple[int, int], Tuple[float, bool]] = defaultdict(
    lambda: (0.0, False)
)

DWELL_SECONDS = 3.0


def point_in_polygon(px: float, py: float, polygon: List[List[float]]) -> bool:
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


def zone_breaches(db: Session, camera_id: int, persons, now: float = None) -> List[dict]:
    zones = db.query(models.SafetyZone).filter(
        models.SafetyZone.camera_id == camera_id
    ).all()
    breaches = []
    if now is None:
        now = time.time()
    for zone in zones:
        if not zone.coordinates or len(zone.coordinates) < 3:
            continue
        inside_now = set()
        for p in persons:
            if p.get("track_id") is None:
                continue
            cx = (p["bbox"][0] + p["bbox"][2]) / 2
            cy = (p["bbox"][1] + p["bbox"][3]) / 2
            if point_in_polygon(cx, cy, zone.coordinates):
                key = (zone.id, p["track_id"])
                entry, breached = _zone_timers[key]
                if entry == 0.0:
                    _zone_timers[key] = (now, False)
                    entry = now
                inside_now.add(key)
                if not breached and now - entry >= DWELL_SECONDS:
                    _zone_timers[key] = (entry, True)
                    breaches.append({
                        "zone": zone,
                        "person": p,
                        "duration": now - entry,
                    })
        # reset timers for tracks that left
        for key in [k for k in _zone_timers if k[0] == zone.id and k not in inside_now]:
            del _zone_timers[key]
    return breaches
