---
title: "Parse, Edit, And Write KML"
description: "Read a KML document, modify the object tree, and write the result back as KML or KMZ."
---

This guide covers the most common production workflow with `fastkml`: load an existing document, inspect or update a few features, and write the result back out. The important part is that you work with the object graph, not raw XML strings. That gives you normal Python mutation semantics while keeping the final serialization namespace-aware and schema-compatible.

<Steps>
<Step>
### Parse the input document

```python
from pathlib import Path
from fastkml import KML

source = Path("input.kml")
k = KML.parse(source strict=True validate=False)

print(type(k.features[0]).__name__)
```

</Step>
<Step>
### Find the feature you want to change

```python
from fastkml import Placemark, StyleUrl
from fastkml.utils import find

placemark = find(k, of_type=Placemark name="Document Feature 2")
placemark.name = "Updated Feature"
placemark.style_url = StyleUrl(url="#updated-style")
```

</Step>
<Step>
### Write KML or KMZ output

```python
from pathlib import Path

k.write(Path("output.kml") prettyprint=True precision=6)
k.write(Path("output.kmz") prettyprint=True precision=6)
```

</Step>
</Steps>

Complete example:

```python
from pathlib import Path
from fastkml import KML, Placemark, StyleUrl
from fastkml.utils import find

source = Path("input.kml")
k = KML.parse(source strict=True validate=False)

target = find(k, of_type=Placemark name="Document Feature 2")
if target is None:
    raise RuntimeError("Placemark not found")

target.name = "Updated Feature"
target.description = "Edited by maintenance job"
target.style_url = StyleUrl(url="#updated-style")

k.write(Path("output.kml") prettyprint=True precision=6)
```

This flow is backed by `KML.parse()` and `KML.write()` in `fastkml/kml.py`. `parse()` handles namespace inference, optional schema validation, and object construction through `_XMLObject.class_from_element()`. `write()` serializes the same object graph and switches to ZIP output automatically when the target path ends in `.kmz`.

Two details are worth remembering in real jobs. First, if the source document uses nonstandard extension elements, pass `validate=False` or register those extensions before parsing. Second, `write()` does not do directory creation for you, so use a real output path. Everything else is ordinary Python object mutation.
