Usage Guide
===========

You can find more examples in the included ``tests/`` directory.

Build a KML from Scratch
------------------------

Example how to build a simple KML file from the Python interpreter.

.. code-block:: pycon

    # Import the library
    >>> from fastkml import kml
    >>> from pygeoif.geometry import Polygon

    # Create the root KML object
    >>> k = kml.KML()
    >>> ns = "{http://www.opengis.net/kml/2.2}"

    # Create a KML Document and add it to the KML root object
    >>> d = kml.Document(ns=ns, id="docid", name="doc name", description="doc description")
    >>> k.append(d)

    # Create a KML Folder and add it to the Document
    >>> f = kml.Folder(ns=ns, id="fid", name="f name", description="f description")
    >>> d.append(f)

    # Create a KML Folder and nest it in the first Folder
    >>> nf = kml.Folder(
    ...     ns=ns, id="nested-fid", name="nested f name", description="nested f description"
    ... )
    >>> f.append(nf)

    # Create a second KML Folder within the Document
    >>> f2 = kml.Folder(ns=ns, id="id2", name="name2", description="description2")
    >>> d.append(f2)

    # Create a Placemark with a simple polygon geometry and add it to the
    # second folder of the Document
    >>> polygon = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
    >>> p = kml.Placemark(
    ...     ns=ns, id="id", name="name", description="description", geometry=polygon
    ... )
    >>> f2.append(p)

    # Print out the KML Object as a string
    >>> print(k.to_string(prettyprint=True))
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document id="docid">
        <name>doc name</name>
        <description>doc description</description>
        <Folder id="fid">
          <name>f name</name>
          <description>f description</description>
          <Folder id="nested-fid">
            <name>nested f name</name>
            <description>nested f description</description>
          </Folder>
        </Folder>
        <Folder id="id2">
          <name>name2</name>
          <description>description2</description>
          <Placemark id="id">
            <name>name</name>
            <description>description</description>
            <Polygon>
              <outerBoundaryIs>
                <LinearRing>
                  <coordinates>0.000000,0.000000,0.000000 1.000000,1.000000,0.000000 1.000000,0.000000,1.000000 0.000000,0.000000,0.000000</coordinates>
                </LinearRing>
              </outerBoundaryIs>
            </Polygon>
          </Placemark>
        </Folder>
      </Document>
    </kml>
    <BLANKLINE>



Read a KML File/String
----------------------

You can create a KML object by reading a KML file as a string

.. code-block:: pycon

    # Start by importing the kml module
    >>> from fastkml import kml

    # Setup the string which contains the KML file we want to read
    >>> doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
    ... <Document>
    ...   <name>Document.kml</name>
    ...   <open>1</open>
    ...   <Style id="exampleStyleDocument">
    ...     <LabelStyle>
    ...       <color>ff0000cc</color>
    ...     </LabelStyle>
    ...   </Style>
    ...   <Placemark>
    ...     <name>Document Feature 1</name>
    ...     <styleUrl>#exampleStyleDocument</styleUrl>
    ...     <Point>
    ...       <coordinates>-122.371,37.816,0</coordinates>
    ...     </Point>
    ...   </Placemark>
    ...   <Placemark>
    ...     <name>Document Feature 2</name>
    ...     <styleUrl>#exampleStyleDocument</styleUrl>
    ...     <Point>
    ...       <coordinates>-122.370,37.817,0</coordinates>
    ...     </Point>
    ...   </Placemark>
    ... </Document>
    ... </kml>"""

    # Read in the KML string
    >>> k = kml.KML.class_from_string(doc)

    # Next we perform some simple sanity checks

    # Check that the number of features is correct
    # This corresponds to the single ``Document``
    >>> len(k.features)
    1

    # (The two Placemarks of the Document)
    >>> k.features[0].features  # doctest: +ELLIPSIS
    [fastkml.features.Placemark...
    >>> len(k.features[0].features)
    2

    # Check specifics of the first Placemark in the Document
    >>> k.features[0].features[0]  # doctest: +ELLIPSIS
    fastkml.features.Placemark(...
    >>> k.features[0].features[0].description
    >>> k.features[0].features[0].name
    'Document Feature 1'

    # Check specifics of the second Placemark in the Document
    >>> k.features[0].features[1].name
    'Document Feature 2'
    >>> k.features[0].features[1].name = "ANOTHER NAME"

    # Verify that we can print back out the KML object as a string
    >>> print(k.to_string(prettyprint=True))
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document>
        <name>Document.kml</name>
        <open>1</open>
        <Style id="exampleStyleDocument">
          <LabelStyle>
            <color>ff0000cc</color>
          </LabelStyle>
        </Style>
        <Placemark>
          <name>Document Feature 1</name>
          <styleUrl>#exampleStyleDocument</styleUrl>
          <Point>
            <coordinates>-122.371000,37.816000,0.000000</coordinates>
          </Point>
        </Placemark>
        <Placemark>
          <name>ANOTHER NAME</name>
          <styleUrl>#exampleStyleDocument</styleUrl>
          <Point>
            <coordinates>-122.370000,37.817000,0.000000</coordinates>
          </Point>
        </Placemark>
      </Document>
    </kml>
    <BLANKLINE>
