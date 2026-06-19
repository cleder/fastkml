---
title: "Containers And Features"
description: "Reference for Snippet, Folder, Document, Placemark, and NetworkLink."
---

Import paths:

```python
from fastkml import Document, Folder, NetworkLink, Placemark, Snippet
```

Source files:

- `fastkml/containers.py`
- `fastkml/features.py`

## `Snippet`

```python
class Snippet(_XMLObject):
    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        text: Optional[str] = None,
        max_lines: Optional[int] = None,
        **kwargs: Any,
    ) -> None
```

Use `Snippet` when you want the short label shown in viewers separate from the full description balloon.

## `Folder`

```python
class Folder(_Container)
```

`Folder` inherits the `_Container` constructor:

```python
def __init__(
    self,
    ns: Optional[str] = None,
    name_spaces: Optional[dict[str, str]] = None,
    id: Optional[str] = None,
    target_id: Optional[str] = None,
    name: Optional[str] = None,
    visibility: Optional[bool] = None,
    isopen: Optional[bool] = None,
    atom_link: Optional[atom.Link] = None,
    atom_author: Optional[atom.Author] = None,
    address: Optional[str] = None,
    phone_number: Optional[str] = None,
    snippet: Optional[Snippet] = None,
    description: Optional[str] = None,
    view: Optional[Union[Camera, LookAt]] = None,
    times: Optional[Union[TimeSpan, TimeStamp]] = None,
    style_url: Optional[StyleUrl] = None,
    styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
    region: Optional[Region] = None,
    extended_data: Optional[ExtendedData] = None,
    features: Optional[Iterable[_Feature]] = None,
    **kwargs: Any,
) -> None
```

Public method:

```python
def append(self, kmlobj: _Feature) -> None
```

## `Document`

```python
class Document(_Container):
    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        features: Optional[Iterable[_Feature]] = None,
        schemata: Optional[Iterable[Schema]] = None,
        **kwargs: Any,
    ) -> None
```

Additional public method:

```python
def get_style_by_url(self, style_url: str) -> Optional[Union[Style, StyleMap]]
```

## `Placemark`

```python
class Placemark(_Feature):
    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        kml_geometry: Optional[KmlGeometry] = None,
        geometry: Optional[Union[GeoType, GeoCollectionType]] = None,
        **kwargs: Any,
    ) -> None
```

Additional public property:

```python
@property
def geometry(self) -> Optional[AnyGeometryType]
```

`geometry` and `kml_geometry` are mutually exclusive on input.

## `NetworkLink`

```python
class NetworkLink(_Feature):
    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        refresh_visibility: Optional[bool] = None,
        fly_to_view: Optional[bool] = None,
        link: Optional[Link] = None,
        **kwargs: Any,
    ) -> None
```

Use it when the KML should reference remote or periodically refreshed content through `fastkml.links.Link`.

Example combining the family:

```python
from fastkml import Document, Folder, NetworkLink, Placemark, Snippet
from fastkml.links import Link
from pygeoif import Point

folder = Folder(name="Operational")
folder.append(Placemark(name="HQ" geometry=Point(-122.4, 37.78, 0) snippet=Snippet(text="Primary site", max_lines=1)))
folder.append(NetworkLink(name="Remote feed" link=Link(href="https://example.com/feed.kml")))

doc = Document(id="doc" features=[folder])
print(doc.features[0].features[0].name)
```
