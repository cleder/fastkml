---
title: "Geometry API"
description: "Reference for coordinate wrappers, geometry classes, and geometry conversion helpers."
---

Import paths:

```python
from fastkml import Coordinates, InnerBoundaryIs, LinearRing, LineString, MultiGeometry, OuterBoundaryIs, Point, Polygon, create_kml_geometry
```

Source file: `fastkml/geometry.py`

## Exported classes

```python
class Coordinates(_XMLObject)
class Point(_Geometry)
class LineString(_Geometry)
class LinearRing(LineString)
class OuterBoundaryIs(BoundaryIs)
class InnerBoundaryIs(BoundaryIs)
class Polygon(_Geometry)
class MultiGeometry(_BaseObject)
```

Exact constructor signatures:

```python
Coordinates(*, ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, coords: Optional[LineType] = None, **kwargs: Any) -> None
Point(*, ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, extrude: Optional[bool] = None, altitude_mode: Optional[AltitudeMode] = None, geometry: Optional[geo.Point] = None, kml_coordinates: Optional[Coordinates] = None, **kwargs: Any) -> None
LineString(*, ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, extrude: Optional[bool] = None, tessellate: Optional[bool] = None, altitude_mode: Optional[AltitudeMode] = None, geometry: Optional[geo.LineString] = None, kml_coordinates: Optional[Coordinates] = None, **kwargs: Any) -> None
LinearRing(*, ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, extrude: Optional[bool] = None, tessellate: Optional[bool] = None, altitude_mode: Optional[AltitudeMode] = None, geometry: Optional[geo.LinearRing] = None, kml_coordinates: Optional[Coordinates] = None, **kwargs: Any) -> None
OuterBoundaryIs(*, ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, geometry: Optional[geo.LinearRing] = None, kml_geometry: Optional[LinearRing] = None, **kwargs: Any) -> None
InnerBoundaryIs(*, ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, geometry: Optional[geo.LinearRing] = None, kml_geometry: Optional[LinearRing] = None, **kwargs: Any) -> None
Polygon(*, ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, extrude: Optional[bool] = None, tessellate: Optional[bool] = None, altitude_mode: Optional[AltitudeMode] = None, outer_boundary: Optional[OuterBoundaryIs] = None, inner_boundaries: Optional[Iterable[InnerBoundaryIs]] = None, geometry: Optional[geo.Polygon] = None, **kwargs: Any) -> None
MultiGeometry(*, ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, extrude: Optional[bool] = None, tessellate: Optional[bool] = None, altitude_mode: Optional[AltitudeMode] = None, kml_geometries: Optional[Iterable[Union[Point, LineString, Polygon, LinearRing, Self, Track, MultiTrack]]] = None, geometry: Optional[MultiGeometryType] = None, **kwargs: Any) -> None
```

Common public properties:

```python
Point.geometry -> Optional[geo.Point]
LineString.geometry -> Optional[geo.LineString]
LinearRing.geometry -> Optional[geo.LinearRing]
OuterBoundaryIs.geometry -> Optional[geo.LinearRing]
InnerBoundaryIs.geometry -> Optional[geo.LinearRing]
Polygon.geometry -> Optional[geo.Polygon]
MultiGeometry.geometry -> Optional[MultiGeometryType]
```

Helper functions:

```python
def create_kml_geometry(
    geometry: Union[GeoType, GeoCollectionType],
    *,
    ns: Optional[str] = None,
    name_spaces: Optional[dict[str, str]] = None,
    id: Optional[str] = None,
    target_id: Optional[str] = None,
    extrude: Optional[bool] = None,
    tessellate: Optional[bool] = None,
    altitude_mode: Optional[AltitudeMode] = None,
) -> KMLGeometryType
```

Example:

```python
from fastkml.geometry import MultiGeometry, create_kml_geometry
from pygeoif import GeometryCollection, Point, Polygon

collection = GeometryCollection([Point(8.5, 47.3, 0), Polygon([(8.5, 47.3, 0), (8.6, 47.4, 0), (8.7, 47.3, 0)])])
kml_geometry = create_kml_geometry(collection)

assert isinstance(kml_geometry, MultiGeometry)
print(len(kml_geometry.kml_geometries))
```

Prefer `create_kml_geometry()` when the source geometry type is not known ahead of time. Prefer the specific classes when you want direct control over boundaries, altitude flags, or coordinate wrappers.
