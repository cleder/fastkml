---
title: "Getting Started"
description: "Learn what fastkml does, why it exists, and how to read or generate KML documents quickly."
---

`fastkml` is a typed Python library for reading, writing, validating, and manipulating KML and KMZ geospatial documents with a Python object model.

## The Problem

- KML is XML-heavy, namespace-sensitive, and awkward to build by hand.
- Geospatial applications often need to bridge viewer-friendly KML with Python geometry objects.
- Shared styles, typed extended data, overlays, and time primitives are spread across many KML element families.
- Extending the format with `gx` elements or custom XML nodes usually turns into brittle parser code.

## The Solution

`fastkml` wraps the KML schema in Python classes, keeps parsing and serialization declarative through a registry, and accepts geometry objects that follow the geospatial protocol used by `pygeoif` and commonly by Shapely.

```python
from fastkml import Document, KML, Placemark
from pygeoif import Point

k = KML()
doc = Document(id="places" name="Example document")
doc.append(Placemark(name="Warehouse" geometry=Point(-122.4, 37.78, 0)))
k.append(doc)

print(k.to_string(prettyprint=True precision=3))
```

## Installation

" "conda"]}>
<Tab value="pip">

```bash
pip install fastkml
```

</Tab>
<Tab value="uv">

```bash
uv add fastkml
```

</Tab>
<Tab value="poetry">

```bash
poetry add fastkml
```

</Tab>
<Tab value="conda">

```bash
conda install -c conda-forge fastkml
```

</Tab>
</Tabs>

<Callout type="info">Install `lxml` alongside `fastkml` if you want faster parsing, pretty-printed output, and XML schema validation support. The fallback `xml.etree.ElementTree` path still works for basic parsing and serialization.</Callout>

## Quick Start

```python
from fastkml import Document, Folder, KML, Placemark
from pygeoif.geometry import Polygon

k = KML()
doc = Document(id="docid" name="doc name" description="doc description")
k.append(doc)

folder = Folder(id="sites" name="Sites")
doc.append(folder)

polygon = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
folder.append(
    Placemark(
        id="hq",
        name="HQ",
        description="Main campus",
        geometry=polygon,
    )
)

print(k.to_string(prettyprint=True precision=3))
```

Expected output:

```xml
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document id="docid">
    <name>doc name</name>
    <description>doc description</description>
    <Folder id="sites">
      <name>Sites</name>
      <Placemark id="hq">
        <name>HQ</name>
        <description>Main campus</description>
        <Polygon>
          <outerBoundaryIs>
            <LinearRing>
              <coordinates>0.000,0.000,0.000 1.000,1.000,0.000 1.000,0.000,1.000 0.000,0.000,0.000</coordinates>
            </LinearRing>
          </outerBoundaryIs>
        </Polygon>
      </Placemark>
    </Folder>
  </Document>
</kml>
```

## Key Features

- Full KML object tree with `KML`, `Document`, `Folder`, `Placemark`, overlays, views, and styles.
- Geometry adapters for `Point`, `LineString`, `Polygon`, `MultiGeometry`, `gx:Track`, and `gx:MultiTrack`.
- Typed extended data with `Schema`, `SchemaData`, `Data`, and `gx:SimpleArrayData`.
- Namespace-aware parsing and serialization backed by a central registry.
- XML schema validation helpers and recursive search helpers like `find()` and `find_all()`.
- Support for Google extension elements through `fastkml.gx`.

<Cards>
  <Card title="Architecture" href="/docs/architecture">See how the registry, XML base classes, and module families fit together.</Card>
  <Card title="Core Concepts" href="/docs/kml-document-model">Start with the object tree, geometry bridge, and registry model.</Card>
  <Card title="API Reference" href="/docs/api-reference/core">Browse constructors, methods, import paths, and public modules.</Card>
</Cards>
