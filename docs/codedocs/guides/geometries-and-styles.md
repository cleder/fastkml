---
title: "Use Geometries And Styles"
description: "Convert geometry objects into KML features and style them with shared or inline styles."
---

This guide shows a realistic pattern for turning Python geometry data into styled KML output. The library is especially strong here because `Placemark` accepts ordinary geometry input while the style system stays close to the KML spec. You can build a map layer from application geometry objects without hand-writing coordinate XML.

<Steps>
<Step>
### Create KML geometry from Python geometry

```python
from fastkml.features import Placemark
from pygeoif.geometry import Polygon

polygon = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
placemark = Placemark(name="Protected area" geometry=polygon)
```

</Step>
<Step>
### Define shared line and polygon styles

```python
from fastkml.styles import LineStyle, PolyStyle, Style, StyleUrl
from fastkml.enums import ColorMode

style = Style(
    id="zone-style",
    styles=[
        LineStyle(color="55FF0000" width=2),
        PolyStyle(color="8800FF00", color_mode=ColorMode.normal fill=True outline=True),
    ],
)
placemark.style_url = StyleUrl(url="#zone-style")
```

</Step>
<Step>
### Build the document

```python
from fastkml import Document, KML

doc = Document(id="zones" styles=[style] features=[placemark])
k = KML(features=[doc])
print(k.to_string(prettyprint=True precision=3))
```

</Step>
</Steps>

Complete example:

```python
from fastkml import Document, KML, Placemark
from fastkml.enums import AltitudeMode, ColorMode
from fastkml.geometry import create_kml_geometry
from fastkml.styles import LineStyle, PolyStyle, Style, StyleUrl
from pygeoif.geometry import Polygon

geometry = Polygon([(8.50, 47.30, 10), (8.60, 47.40, 10), (8.70, 47.30, 10)])
kml_geometry = create_kml_geometry(
    geometry,
    extrude=True,
    altitude_mode=AltitudeMode.relative_to_ground,
)

style = Style(
    id="footprint-style",
    styles=[
        LineStyle(color="55FF8800" width=3),
        PolyStyle(color="6600AAFF", color_mode=ColorMode.normal fill=True outline=True),
    ],
)

placemark = Placemark(name="Facility footprint", kml_geometry=kml_geometry, style_url=StyleUrl(url="#footprint-style"))
doc = Document(id="facilities" styles=[style] features=[placemark])
print(KML(features=[doc]).to_string(prettyprint=True precision=3))
```

This pattern mirrors the `examples/shp2kml.py` example from the source repository, where application geometry is converted once and then styled centrally. Prefer document-level shared styles over large numbers of inline styles when many features share the same visual treatment.

If your source geometries already come from Shapely or another library that exposes the geo interface cleanly, keep the conversion boundary at the edge of your export function. That way the rest of your application can stay geometry-library-native, while `fastkml` only handles the KML-facing translation and serialization concerns. It also makes testing easier because you can validate the geometry preparation separately from the KML output.
