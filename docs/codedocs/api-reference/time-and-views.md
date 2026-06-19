---
title: "Time And Views API"
description: "Reference for KML date handling, time primitives, saved viewpoints, and region visibility controls."
---

Import paths:

```python
from fastkml import Camera, KmlDateTime, LookAt, TimeSpan, TimeStamp
from fastkml.views import LatLonAltBox, Lod, Region
```

Source files:

- `fastkml/times.py`
- `fastkml/views.py`

## Signatures

```python
adjust_date_to_resolution(dt: Union[date, datetime], resolution: Optional[DateTimeResolution] = None) -> Union[date, datetime]
KmlDateTime(dt: Union[date, datetime], resolution: Optional[DateTimeResolution] = None) -> None
TimeStamp(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, timestamp: Optional[KmlDateTime] = None, **kwargs: Any) -> None
TimeSpan(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, begin: Optional[KmlDateTime] = None, end: Optional[KmlDateTime] = None, **kwargs: Any) -> None
Camera(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, longitude: Optional[float] = None, latitude: Optional[float] = None, altitude: Optional[float] = None, heading: Optional[float] = None, tilt: Optional[float] = None, roll: Optional[float] = None, altitude_mode: Optional[AltitudeMode] = None, **kwargs: Any) -> None
LookAt(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, longitude: Optional[float] = None, latitude: Optional[float] = None, altitude: Optional[float] = None, heading: Optional[float] = None, tilt: Optional[float] = None, range: Optional[float] = None, altitude_mode: Optional[AltitudeMode] = None, **kwargs: Any) -> None
LatLonAltBox(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, north: Optional[float] = None, south: Optional[float] = None, east: Optional[float] = None, west: Optional[float] = None, min_altitude: Optional[float] = None, max_altitude: Optional[float] = None, altitude_mode: Optional[AltitudeMode] = None, **kwargs: Any) -> None
Lod(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, min_lod_pixels: Optional[int] = None, max_lod_pixels: Optional[int] = None, min_fade_extent: Optional[int] = None, max_fade_extent: Optional[int] = None, **kwargs: Any) -> None
Region(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, lat_lon_alt_box: Optional[LatLonAltBox] = None, lod: Optional[Lod] = None, **kwargs: Any) -> None
```

Public methods and properties:

```python
KmlDateTime.parse(cls, datestr: str) -> Optional[KmlDateTime]
KmlDateTime.get_ns_id(cls) -> str
str(KmlDateTime) -> KML datetime string
```

Example:

```python
from datetime import datetime, timezone
from fastkml import Camera, KmlDateTime, TimeStamp
from fastkml.views import LatLonAltBox, Lod, Region

stamp = TimeStamp(timestamp=KmlDateTime(datetime(2025, 5, 7, 10, 0 tzinfo=timezone.utc)))
camera = Camera(longitude=13.4 latitude=52.5 altitude=500 heading=15 tilt=45 roll=0)
region = Region(
    lat_lon_alt_box=LatLonAltBox(north=52.6 south=52.4 east=13.5 west=13.2),
    lod=Lod(min_lod_pixels=256, max_lod_pixels=-1),
)

print(str(stamp.timestamp))
print(camera.heading)
print(bool(region))
```

Reach for `KmlDateTime.parse()` when consuming external timestamp strings. Use `Camera` when you need explicit camera orientation and `LookAt` when you want the viewer focused on a target point with a range.
