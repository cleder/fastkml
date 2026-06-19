---
title: "GX Extensions API"
description: "Reference for Google extension namespace classes including gx tracks and array data."
---

Import paths:

```python
from fastkml.gx import Angle, MultiTrack, SimpleArrayData, SimpleArrayField, Track, TrackItem, track_items_to_geometry, tracks_to_geometry
```

Source files:

- `fastkml/gx/__init__.py`
- `fastkml/gx/data.py`
- `fastkml/gx/track.py`

## Array metadata

```python
SimpleArrayField(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, name: Optional[str] = None, type_: Optional[DataType] = None, display_name: Optional[str] = None, **kwargs: Any) -> None
SimpleArrayData(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, name: Optional[str] = None, data: Optional[Iterable[str]] = None, **kwargs: Any) -> None
```

## Track classes

```python
class Angle:
    @property
    def coords(self) -> PointType

@dataclass(frozen=True)
class TrackItem:
    when: KmlDateTime
    coord: geo.Point
    angle: Optional[Angle] = None

Track(
    *,
    ns: Optional[str] = None,
    name_spaces: Optional[dict[str, str]] = None,
    id: Optional[str] = None,
    target_id: Optional[str] = None,
    altitude_mode: Optional[AltitudeMode] = None,
    track_items: Optional[Iterable[TrackItem]] = None,
    whens: Optional[Iterable[KmlDateTime]] = None,
    coords: Optional[Iterable[PointType]] = None,
    angles: Optional[Iterable[PointType]] = None,
    extended_data: Optional[ExtendedData] = None,
    **kwargs: Any,
) -> None
MultiTrack(
    *,
    ns: Optional[str] = None,
    name_spaces: Optional[dict[str, str]] = None,
    id: Optional[str] = None,
    target_id: Optional[str] = None,
    altitude_mode: Optional[AltitudeMode] = None,
    tracks: Optional[Iterable[Track]] = None,
    interpolate: Optional[bool] = None,
    **kwargs: Any,
) -> None
```

Public properties and functions:

```python
Track.geometry -> Optional[geo.LineString]
Track.whens -> tuple[KmlDateTime, ...]
Track.coords -> tuple[PointType, ...]
Track.angles -> tuple[PointType, ...]
MultiTrack.geometry -> Optional[geo.MultiLineString]
def track_items_to_geometry(track_items: Iterable[TrackItem]) -> geo.LineString
def tracks_to_geometry(tracks: Iterable[Track]) -> geo.MultiLineString
```

Example:

```python
from datetime import datetime, timezone
from fastkml import KmlDateTime
from fastkml.gx import Track

track = Track(
    whens=[
        KmlDateTime(datetime(2025, 5, 7, 10, 0 tzinfo=timezone.utc)),
        KmlDateTime(datetime(2025, 5, 7, 10, 5 tzinfo=timezone.utc)),
    ],
    coords=[(13.4, 52.5, 0), (13.41, 52.51, 0)],
    angles=[(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)],
)

print(track.geometry.wkt)
print(track.coords[0])
```

`Track` is the most important `gx` class. It encodes one moving object across multiple timestamps without forcing you to create a separate placemark per position.
