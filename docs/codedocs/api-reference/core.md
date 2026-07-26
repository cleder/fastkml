---
title: "Core API"
description: "Reference for the root KML document class and the common XML object methods shared across the public model."
---

This page covers the root entry point exported from `fastkml` and the shared methods inherited by most public classes from `_XMLObject` in `fastkml/base.py`.

## Import Paths

```python
from fastkml import KML
```

Source files:

- `fastkml/kml.py`
- `fastkml/base.py`

## `KML`

Signature:

```text
class KML(_XMLObject):
    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        features: Optional[Iterable[kml_children]] = None,
        **kwargs: Any,
    ) -> None
```

Constructor options:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ns` | `Optional[str]` | `None` | Namespace prefix wrapper. Use `""` to emit unprefixed KML tags. |
| `name_spaces` | `Optional[dict[str, str]]` | `None` | Extra namespace mappings merged with `config.NAME_SPACES`. |
| `features` | `Optional[Iterable[kml_children]]` | `None` | Top-level features such as `Document`, `Folder`, `Placemark`, overlays, or `NetworkLinkControl`. |

Public methods:

```text
def append(self, kmlobj: kml_children) -> None
def etree_element(self, precision: Optional[int] = None, verbosity: Verbosity = Verbosity.normal) -> Element
@classmethod
def parse(
    cls,
    file: Union[Path, str, IO[AnyStr]],
    *,
    ns: Optional[str] = None,
    name_spaces: Optional[dict[str, str]] = None,
    strict: bool = True,
    validate: Optional[bool] = None,
) -> Self
def write(
    self,
    file_path: Path,
    *,
    prettyprint: bool = True,
    precision: Optional[int] = None,
    verbosity: Verbosity = Verbosity.normal,
) -> None
```

Returns:

- `append()` mutates `features` in place and returns `None`.
- `etree_element()` returns the root XML element for the document.
- `parse()` returns a populated `KML` instance.
- `write()` writes `.kml` text or `.kmz` ZIP output based on the path suffix.

Example:

```python
from pathlib import Path
from fastkml import Document, KML

k = KML(features=[Document(id="doc", name="Demo")])
k.write(Path("demo.kml"), prettyprint=True)

parsed = KML.parse(Path("demo.kml"), validate=False)
print(parsed.features[0].name)
```

## Shared `_XMLObject` Methods

Most exported classes in the library inherit these methods:

```text
def etree_element(self, precision: Optional[int] = None, verbosity: Verbosity = Verbosity.normal) -> Element
def populate_element(self, element: Element, precision: Optional[int] = None, verbosity: Verbosity = Verbosity.normal) -> None
def to_string(
    self,
    *,
    prettyprint: bool = True,
    precision: Optional[int] = None,
    verbosity: Verbosity = Verbosity.normal,
) -> str
def validate(self) -> Optional[bool]
@classmethod
def class_from_element(
    cls,
    *,
    ns: str,
    name_spaces: Optional[dict[str, str]] = None,
    element: Element,
    strict: bool,
) -> Self
@classmethod
def from_string(
    cls,
    string: str,
    *,
    ns: Optional[str] = None,
    name_spaces: Optional[dict[str, str]] = None,
    strict: bool = True,
) -> Self
```

Usage pattern:

```python
from fastkml import KML

k = KML.from_string(
    '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Demo</name></Document></kml>'
)
print(k.to_string(prettyprint=True))
print(k.validate())
```

These methods are the reason the entire library feels uniform. Whether you are working with a `Style`, `Polygon`, `NetworkLinkControl`, or `Track`, the object can usually be parsed from XML and serialized back out with the same method names.
