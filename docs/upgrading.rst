Upgrading from older versions of FastKML
========================================

Q: I updated from 0.12 to 1.0.0 and now getting the following errors when using
``parse()``::

    File "src/lxml/etree.pyx", line 3701, in lxml.etree._Validator.assert_
    AssertionError: Element ...

A: Your KML does not validate against the XML Schema.
You can read it without validations by passing ``validate=False`` or ``strict=False``
to the parse method::

    from fastkml.kml import KML
    doc = KML.parse('path/to/your/file.kml', strict=False)
    # or
    doc = KML.parse('path/to/your/file.kml', validate=False)

With version 1.0, ``.from_string()`` is a class method that returns a new object.

In fastkml 0.x::

    postcode_kml = kml.KML()
    postcode_kml.from_string(kml_file.read())

Becomes in 1.0::

    postcode_kml = kml.KML.from_string(kml_file.read())
