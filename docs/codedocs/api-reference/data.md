---
title: "Data API"
description: "Reference for untyped data, schema-backed data, and extended metadata containers."
---

Import paths:

```python
from fastkml import Data, ExtendedData, Schema, SchemaData, SimpleData, SimpleField
from fastkml.gx import SimpleArrayData, SimpleArrayField
```

Source files:

- `fastkml/data.py`
- `fastkml/gx/data.py`

## Exported classes and signatures

```python
SimpleField(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, name: Optional[str] = None, type_: Optional[DataType] = None, display_name: Optional[str] = None, **kwargs: Any) -> None
Schema(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, name: Optional[str] = None, fields: Optional[Iterable[SimpleField]] = None, array_fields: Optional[Iterable[SimpleArrayField]] = None, **kwargs: Any) -> None
Data(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, name: Optional[str] = None, value: Optional[str] = None, display_name: Optional[str] = None, **kwargs: Any) -> None
SimpleData(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, name: Optional[str] = None, value: Optional[str] = None, **kwargs: Any) -> None
SchemaData(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, schema_url: Optional[str] = None, data: Optional[Iterable[SimpleData]] = None, array_data: Optional[Iterable[SimpleArrayData]] = None, **kwargs: Any) -> None
ExtendedData(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, elements: Optional[Iterable[Union[Data, SchemaData]]] = None, **kwargs: Any) -> None
SimpleArrayField(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, name: Optional[str] = None, type_: Optional[DataType] = None, display_name: Optional[str] = None, **kwargs: Any) -> None
SimpleArrayData(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, id: Optional[str] = None, target_id: Optional[str] = None, name: Optional[str] = None, data: Optional[Iterable[str]] = None, **kwargs: Any) -> None
```

Public methods:

```python
Schema.append(self, field: Union[SimpleField, SimpleArrayField]) -> None
SchemaData.append_data(self, data: Union[SimpleData, SimpleArrayData]) -> None
```

Important return behavior:

- Constructors return instances only when required inputs are present.
- `Schema` raises `KMLSchemaError` if `id` is missing.
- Empty metadata objects often serialize to nothing because their `__bool__()` methods return `False`.

Example:

```python
from fastkml import ExtendedData, SchemaData, SimpleData
from fastkml.gx import SimpleArrayData

schema_data = SchemaData(
    schema_url="#asset-schema",
    data=[SimpleData(name="status" value="active")],
    array_data=[SimpleArrayData(name="reading" data=["10.2", "10.8"])],
)
extended = ExtendedData(elements=[schema_data])
print(extended.elements[0].schema_url)
```

Use `Data` for lightweight metadata, `Schema` plus `SchemaData` for typed data contracts, and the `gx` array classes when a schema field must hold a list rather than a scalar value.
