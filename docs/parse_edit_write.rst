Parse, Edit, and Write KML
===========================

This guide covers the most common production workflow with ``fastkml``: load an existing
document, inspect or update a few features, and write the result back out. The important
part is that you work with the object graph, not raw XML strings. That gives you normal
Python mutation semantics while keeping the final serialization namespace-aware and
schema-compatible.

1. Parse the input document

.. code-block:: pycon

    >>> from pathlib import Path
    >>> from fastkml import KML

    >>> source = Path("docs/Document-clean.kml")
    >>> k = KML.parse(source, strict=True, validate=False)

    >>> print(type(k.features[0]).__name__)
    Document

2. Find the feature you want to change

.. code-block:: pycon

    >>> from fastkml import Placemark, StyleUrl
    >>> from fastkml.utils import find

    >>> placemark = find(k, of_type=Placemark, name="Vancouver Film Studios")
    >>> placemark.name = "Updated Feature"
    >>> placemark.style_url = StyleUrl(url="#updated-style")

3. Write KML or KMZ output

.. code-block:: pycon

    >>> import tempfile
    >>> from pathlib import Path

    >>> with tempfile.TemporaryDirectory() as tmp_dir:
    ...     kml_path = Path(tmp_dir) / "output.kml"
    ...     kmz_path = Path(tmp_dir) / "output.kmz"
    ...     k.write(kml_path, prettyprint=True, precision=6)
    ...     k.write(kmz_path, prettyprint=True, precision=6)
    ...     print(kml_path.exists())
    ...     print(kmz_path.exists())
    ...
    True
    True

This flow is backed by ``KML.parse()`` and ``KML.write()`` in ``fastkml/kml.py``.
``parse()`` handles namespace inference, optional schema validation, and object construction
through ``_XMLObject.class_from_element()``. ``write()`` serializes the same object graph
and switches to ZIP output automatically when the target path ends in ``.kmz``.

Two details are worth remembering in real jobs. First, if the source document uses
nonstandard extension elements, pass ``validate=False`` or register those extensions before
parsing (see the "Extending FastKML" section of :doc:`working_with_kml`). Second, ``write()``
does not do directory creation for you, so use a real output path. Everything else is
ordinary Python object mutation.
