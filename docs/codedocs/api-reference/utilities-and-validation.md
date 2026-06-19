---
title: "Utilities And Validation"
description: "Reference for traversal helpers, XML schema validation, and namespace/backend configuration."
---

Import paths:

```python
from fastkml.utils import find, find_all, has_attribute_values
from fastkml.validator import get_schema_parser, validate
from fastkml import config
```

Source files:

- `fastkml/utils.py`
- `fastkml/validator.py`
- `fastkml/config.py`

## Utility functions

```python
has_attribute_values(obj: object, **kwargs: Any) -> bool
find_all(
    obj: object,
    *,
    of_type: Optional[Union[type[object], tuple[type[object], ...]]] = None,
    **kwargs: Any,
) -> Generator[object, None, None]
find(
    obj: object,
    *,
    of_type: Optional[Union[type[object], tuple[type[object], ...]]] = None,
    **kwargs: Any,
) -> Optional[object]
```

`find_all()` recursively walks object attributes and iterables. `find()` is just `next(find_all(...), None)`.

## Validation functions

```python
get_schema_parser(schema: Optional[pathlib.Path] = None) -> etree.XMLSchema
validate(
    *,
    schema: Optional[pathlib.Path] = None,
    element: Optional[Element] = None,
    file_to_validate: Optional[pathlib.Path] = None,
) -> Optional[bool]
```

`validate()` returns `True` for valid input, raises on invalid input, and returns `None` when the XMLSchema backend is unavailable.

## Configuration helpers

```python
set_etree_implementation(implementation: ModuleType) -> None
register_namespaces(**namespaces: str) -> None
set_default_namespaces() -> None
```

Exported constants:

```python
KMLNS = "{http://www.opengis.net/kml/2.2}"
ATOMNS = "{http://www.w3.org/2005/Atom}"
GXNS = "{http://www.google.com/kml/ext/2.2}"
DEFAULT_NAME_SPACES = {"kml": "...", "atom": "...", "gx": "..."}
```

Example:

```python
from fastkml import KML, Placemark
from fastkml.utils import find_all
from fastkml.validator import validate

k = KML.from_string('<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark><name>A</name></Placemark></Document></kml>')
placemarks = list(find_all(k, of_type=Placemark))
print(len(placemarks))
print(validate(element=k.etree_element()))
```

Use the utility helpers when you need object-tree traversal. Use the validator when you need schema-level guarantees before saving or publishing KML.

The configuration helpers are most useful in framework or platform integration code rather than in ordinary document authoring. `set_etree_implementation()` lets you swap the XML backend explicitly, while `register_namespaces()` and `set_default_namespaces()` make sure parsed and serialized documents retain the prefixes your workflow expects. In most applications you will never call them directly, but they explain why fastkml can support both `lxml` and the standard library XML stack without changing the public model classes.
