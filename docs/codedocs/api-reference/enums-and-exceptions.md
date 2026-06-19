---
title: "Enums And Exceptions"
description: "Reference for the public enumerations and exception types used across fastkml."
---

Import paths:

```python
from fastkml.enums import AltitudeMode, ColorMode, DataType, DateTimeResolution, DisplayMode, GridOrigin, PairKey, RefreshMode, RelaxedEnum, Shape, Units, Verbosity, ViewRefreshMode
from fastkml.exceptions import FastKMLError, GeometryError, KMLParseError, KMLSchemaError, KMLWriteError
```

Source files:

- `fastkml/enums.py`
- `fastkml/exceptions.py`

## Enums

```python
Verbosity: terse, normal, verbose
DateTimeResolution: datetime, date, year_month, year
AltitudeMode: clamp_to_ground, relative_to_ground, absolute, clamp_to_sea_floor, relative_to_sea_floor
DataType: string, int_, uint, short, ushort, float_, double, bool_
RefreshMode: on_change, on_interval, on_expire
ViewRefreshMode: never, on_stop, on_request, on_region
ColorMode: normal, random
DisplayMode: default, hide
Shape: rectangle, cylinder, sphere
GridOrigin: lower_left, upper_left
Units: fraction, pixels, inset_pixels
PairKey: normal, highlight
```

`RelaxedEnum` is the base class for most of these enums and provides case-insensitive matching through `_missing_()`. `AltitudeMode.get_ns_id()` is especially important because some altitude modes belong to the `gx` namespace rather than the base KML namespace.

Example:

```python
from fastkml.enums import AltitudeMode, PairKey

print(AltitudeMode("CLAMPTOGROUND"))
print(AltitudeMode.relative_to_sea_floor.get_ns_id())
print(PairKey.highlight.value)
```

## Exceptions

```python
class FastKMLError(Exception)
class KMLParseError(FastKMLError)
class KMLWriteError(FastKMLError)
class KMLSchemaError(FastKMLError)
class GeometryError(FastKMLError)
```

Typical usage:

- `GeometryError` is raised when mutually exclusive geometry inputs are provided.
- `KMLSchemaError` is raised for schema-specific problems such as missing `Schema.id`.
- `KMLWriteError` is raised when geometry conversion cannot map a source geometry to a supported KML type.

Example:

```python
from fastkml.exceptions import GeometryError
from fastkml.geometry import Coordinates, Point

try:
    Point(geometry=None, kml_coordinates=Coordinates(coords=[(1.0, 2.0, 0.0)]))
except GeometryError as exc:
    print(type(exc).__name__)
```

These enums and exceptions are small, but they define the vocabulary used throughout the rest of the public API. Knowing them makes the higher-level modules much easier to reason about.

One practical tip is to prefer enum members over raw strings in application code even though `RelaxedEnum` will often accept case-insensitive string input. Using `AltitudeMode.relative_to_ground` or `ColorMode.random` directly gives you better editor support and makes invalid states easier to catch before serialization. The exception hierarchy is similarly small on purpose: you can catch `FastKMLError` for broad application-level handling or catch specific subclasses like `GeometryError` when you want precise recovery behavior.
