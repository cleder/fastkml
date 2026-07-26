---
title: "Extended Data"
description: "Use untyped data, typed schema data, and gx array fields to attach application metadata to KML features."
---

KML has two metadata paths, and `fastkml` models both. `Data` stores simple untyped name-value pairs, while `Schema`, `SchemaData`, `SimpleField`, and the `gx` array classes model typed feature metadata. These abstractions exist because real KML documents often need application-specific fields such as asset IDs, classifications, measurements, or time series that the base KML schema does not include.

The relevant code lives in `fastkml/data.py` and `fastkml/gx/data.py`. `ExtendedData` is the main wrapper and can contain both `Data` and `SchemaData`. `Schema` is usually attached to a `Document`, while `SchemaData` is attached to a feature and points back to the schema through `schema_url`. This mirrors how the KML spec separates schema declaration from schema-backed values.

## How It Relates To Other Concepts

- `ExtendedData` is a regular feature attribute on `_Feature`, so it travels with placemarks and overlays.
- `gx:Track` can also hold `ExtendedData`, and its special registration is completed in `_registry_setup.py`.
- Validation matters more here than in plain text metadata because typed schemas are easier to misuse.

## How It Works Internally

`ExtendedData.elements` is a mixed list of `Data` and `SchemaData`. `Schema.append()` decides whether a field goes into `fields` or `array_fields`, while `SchemaData.append_data()` does the same for regular and array values. These methods are tiny because the registry does the actual XML work. The important implementation detail is the boolean behavior: many of these classes define `__bool__()` to suppress empty elements, so blank metadata objects often disappear from serialized output instead of producing empty XML tags.

## Basic Usage

```python
from fastkml import Data, ExtendedData, Placemark
from pygeoif import Point

placemark = Placemark(
    name="Substation",
    geometry=Point(7.1, 50.7, 0),
    extended_data=ExtendedData(
        elements=[
            Data(name="asset_id", value="SS-14"),
            Data(name="owner", value="Grid Ops"),
        ]
    ),
)

print(placemark.extended_data.elements[0].name)
```

## Advanced Usage

```python
from fastkml import (
    Document,
    ExtendedData,
    Placemark,
    Schema,
    SchemaData,
    SimpleData,
    SimpleField,
)
from fastkml.enums import DataType
from fastkml.gx import SimpleArrayData, SimpleArrayField
from pygeoif import Point

schema = Schema(
    id="asset-schema",
    name="Asset",
    fields=[
        SimpleField(name="voltage", type_=DataType.int_),
        SimpleField(name="status", type_=DataType.string),
    ],
    array_fields=[
        SimpleArrayField(name="reading", type_=DataType.float_),
    ],
)

placemark = Placemark(
    name="Transformer",
    geometry=Point(11.57, 48.14, 0),
    extended_data=ExtendedData(
        elements=[
            SchemaData(
                schema_url="#asset-schema",
                data=[
                    SimpleData(name="voltage", value="110"),
                    SimpleData(name="status", value="active"),
                ],
                array_data=[
                    SimpleArrayData(name="reading", data=["10.3", "10.7", "10.5"]),
                ],
            )
        ]
    ),
)

doc = Document(id="assets", schemata=[schema], features=[placemark])
print(doc.schemata[0].id)
```

<Callout type="warn">`Schema` requires an `id`, and `SchemaData.schema_url` needs to reference that `id` with a fragment such as `#asset-schema`. If those do not line up, viewers may accept the KML but your typed data will be effectively detached from its schema.</Callout>

<Accordions>
<Accordion title="Untyped Data versus SchemaData">
Use `Data` when you just need a couple of simple fields and you do not care about formal typing. It is shorter to write, easier to inspect, and enough for many viewer-only workflows. Use `SchemaData` when you need explicit field declarations, array values, or a contract that other systems can rely on. The extra ceremony is worthwhile when the KML file is part of a data pipeline rather than just a display artifact.
</Accordion>
<Accordion title="Why gx array fields are separate classes">
The KML base schema does not provide native array field declarations, so the Google `gx` extension models them separately with `SimpleArrayField` and `SimpleArrayData`. fastkml keeps those in `fastkml.gx.data` rather than merging them into the base classes because the namespace, XML shape, and viewer support are different. That separation makes the XML output correct and keeps the object model honest about what is standard KML and what is an extension. The trade-off is that mixed metadata documents need imports from both `fastkml` and `fastkml.gx`.
</Accordion>
</Accordions>
