---
title: "Links, Models, And Overlays"
description: "Reference for linked resources, 3D model helpers, and the overlay class family."
---

Import paths:

```python
from fastkml import (
    GroundOverlay,
    Icon,
    ImagePyramid,
    LatLonBox,
    Link,
    Model,
    OverlayXY,
    PhotoOverlay,
    RotationXY,
    Scale,
    ScreenOverlay,
    ScreenXY,
    Size,
    ViewVolume,
)
from fastkml.model import Alias, Location, Orientation, ResourceMap
```

Source files:

- `fastkml/links.py`
- `fastkml/model.py`
- `fastkml/overlays.py`

## Resource links

```text
Link(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, href: Optional[str] = None, refresh_mode: Optional[RefreshMode] = None, refresh_interval: Optional[float] = None, view_refresh_mode: Optional[ViewRefreshMode] = None, view_refresh_time: Optional[float] = None, view_bound_scale: Optional[float] = None, view_format: Optional[str] = None, http_query: Optional[str] = None, **kwargs: Any) -> None
Icon(...) -> None
```

`Icon` inherits `Link` and is used by `IconStyle` and the overlay classes.

## Model helpers

```text
Location(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, altitude: Optional[float] = None, latitude: Optional[float] = None, longitude: Optional[float] = None, **kwargs: Any) -> None
Orientation(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, heading: Optional[float] = None, tilt: Optional[float] = None, roll: Optional[float] = None, **kwargs: Any) -> None
Scale(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None, **kwargs: Any) -> None
Alias(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, target_href: Optional[str] = None, source_href: Optional[str] = None, **kwargs: Any) -> None
ResourceMap(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, aliases: Optional[Iterable[Alias]] = None, **kwargs: Any) -> None
Model(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, altitude_mode: Optional[AltitudeMode] = None, location: Optional[Location] = None, orientation: Optional[Orientation] = None, scale: Optional[Scale] = None, link: Optional[Link] = None, resource_map: Optional[ResourceMap] = None, **kwargs: Any) -> None
```

Public property:

```text
Location.geometry -> Optional[Point]
Model.geometry -> Optional[Point]
```

## Overlay family

```text
ViewVolume(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, left_fov: Optional[float] = None, right_fov: Optional[float] = None, bottom_fov: Optional[float] = None, top_fov: Optional[float] = None, near: Optional[float] = None, **kwargs: Any) -> None
ImagePyramid(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, tile_size: Optional[int] = None, max_width: Optional[int] = None, max_height: Optional[int] = None, grid_origin: Optional[GridOrigin] = None, **kwargs: Any) -> None
LatLonBox(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, north: Optional[float] = None, south: Optional[float] = None, east: Optional[float] = None, west: Optional[float] = None, rotation: Optional[float] = None, **kwargs: Any) -> None
PhotoOverlay(..., rotation: Optional[float] = None, view_volume: Optional[ViewVolume] = None, image_pyramid: Optional[ImagePyramid] = None, point: Optional[Point] = None, shape: Optional[Shape] = None, **kwargs: Any) -> None
GroundOverlay(..., altitude: Optional[float] = None, altitude_mode: Optional[AltitudeMode] = None, lat_lon_box: Optional[LatLonBox] = None, **kwargs: Any) -> None
OverlayXY(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, x: Optional[float] = None, y: Optional[float] = None, x_units: Optional[Units] = None, y_units: Optional[Units] = None, **kwargs: Any) -> None
ScreenXY(...) -> None
RotationXY(...) -> None
Size(...) -> None
ScreenOverlay(..., overlay_xy: Optional[OverlayXY] = None, screen_xy: Optional[ScreenXY] = None, rotation_xy: Optional[RotationXY] = None, size: Optional[Size] = None, rotation: Optional[float] = None, **kwargs: Any) -> None
```

Example:

```python
from fastkml import GroundOverlay, Icon, LatLonBox, Link, Model
from fastkml.model import Location

overlay = GroundOverlay(
    name="Weather radar",
    icon=Icon(href="https://example.com/radar.png"),
    lat_lon_box=LatLonBox(north=51.0, south=49.0, east=9.0, west=7.0),
)
model = Model(
    location=Location(latitude=47.37, longitude=8.54, altitude=500),
    link=Link(href="https://example.com/asset.dae"),
)

print(bool(overlay.lat_lon_box))
print(model.geometry)
```

Use `GroundOverlay` for terrain-aligned rasters, `ScreenOverlay` for HUD or logo graphics, `PhotoOverlay` for immersive image placement, and `Model` when you need to place a 3D asset at a specific geographic location.
