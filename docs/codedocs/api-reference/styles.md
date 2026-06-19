---
title: "Styles API"
description: "Reference for URLs, style selectors, color styles, and style maps."
---

Import paths:

```python
from fastkml import BalloonStyle, HotSpot, IconStyle, LabelStyle, LineStyle, Pair, PolyStyle, Style, StyleMap, StyleUrl
```

Source file: `fastkml/styles.py`

## Exported classes and signatures

```python
StyleUrl(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, url: Optional[str] = None, **kwargs: Any) -> None
HotSpot(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, x: Optional[float] = None, y: Optional[float] = None, xunits: Optional[Units] = None, yunits: Optional[Units] = None, **kwargs: Any) -> None
IconStyle(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, color: Optional[str] = None, color_mode: Optional[ColorMode] = None, scale: Optional[float] = None, heading: Optional[float] = None, icon: Optional[Icon] = None, icon_href: Optional[str] = None, hot_spot: Optional[HotSpot] = None, **kwargs: Any) -> None
LineStyle(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, color: Optional[str] = None, color_mode: Optional[ColorMode] = None, width: Optional[float] = None, **kwargs: Any) -> None
PolyStyle(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, color: Optional[str] = None, color_mode: Optional[ColorMode] = None, fill: Optional[bool] = None, outline: Optional[bool] = None, **kwargs: Any) -> None
LabelStyle(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, color: Optional[str] = None, color_mode: Optional[ColorMode] = None, scale: Optional[float] = None, **kwargs: Any) -> None
BalloonStyle(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, bg_color: Optional[str] = None, text_color: Optional[str] = None, text: Optional[str] = None, display_mode: Optional[DisplayMode] = None, **kwargs: Any) -> None
Style(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, styles: Optional[Iterable[AnyStyle]] = None, **kwargs: Any) -> None
Pair(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, key: Optional[PairKey] = None, style: Optional[Union[StyleUrl, Style]] = None, **kwargs: Any) -> None
StyleMap(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, pairs: Optional[Iterable[Pair]] = None, **kwargs: Any) -> None
```

Public convenience properties:

```python
IconStyle.icon_href -> Optional[str]
StyleMap.normal -> Optional[Union[StyleUrl, Style]]
StyleMap.highlight -> Optional[Union[StyleUrl, Style]]
```

Constructor highlights:

| Class | Key options | Notes |
|-------|-------------|-------|
| `StyleUrl` | `url` | References shared styles with `#id` or external URLs. |
| `IconStyle` | `icon`, `icon_href`, `scale`, `heading`, `hot_spot` | `icon_href` is a shortcut for building `Icon`. |
| `LineStyle` | `color`, `color_mode`, `width` | Used for paths and polygon outlines. |
| `PolyStyle` | `color`, `fill`, `outline` | Used for polygon fills and extrusion walls. |
| `Style` | `styles` | Aggregates multiple substyles into one reusable style group. |
| `StyleMap` | `pairs` | Maps `normal` and `highlight` modes to a style or style URL. |

Example:

```python
from fastkml import Document, Placemark
from fastkml.styles import IconStyle, Pair, Style, StyleMap, StyleUrl
from fastkml.enums import PairKey
from pygeoif import Point

normal = Style(id="normal" styles=[IconStyle(icon_href="https://example.com/normal.png")])
highlight = Style(id="highlight" styles=[IconStyle(icon_href="https://example.com/highlight.png")])
style_map = StyleMap(
    id="place-style",
    pairs=[
        Pair(key=PairKey.normal style=StyleUrl(url="#normal")),
        Pair(key=PairKey.highlight style=StyleUrl(url="#highlight")),
    ],
)
placemark = Placemark(name="Depot" geometry=Point(1, 2, 0), style_url=StyleUrl(url="#place-style"))
doc = Document(styles=[normal, highlight, style_map] features=[placemark])
print(doc.get_style_by_url("#place-style").normal.url)
```

If you only need one-off styling, put `Style` objects directly in a feature’s `styles` list. If multiple features share the same style, give the style an `id`, store it on the document, and reference it with `StyleUrl`.
