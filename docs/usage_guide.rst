Usage Guide
===========

You can find more examples in the included ``test_main.py`` file or in
collective.geo.fastkml_, here is a quick overview:

(The examples below are available as standalone scripts in the ``examples`` folder.)


Build a KML from Scratch
------------------------

Example how to build a simple KML file from the Python interpreter.

.. code-block:: python

    # Import the library
    >>> from fastkml import kml
    >>> from pygeoif.geometry import Polygon

    # Create the root KML object
    >>> k = kml.KML()
    >>> ns = '{http://www.opengis.net/kml/2.2}'

    # Create a KML Document and add it to the KML root object
    >>> d = kml.Document(ns, 'docid', 'doc name', 'doc description')
    >>> k.append(d)

    # Create a KML Folder and add it to the Document
    >>> f = kml.Folder(ns, 'fid', 'f name', 'f description')
    >>> d.append(f)

    # Create a KML Folder and nest it in the first Folder
    >>> nf = kml.Folder(ns, 'nested-fid', 'nested f name', 'nested f description')
    >>> f.append(nf)

    # Create a second KML Folder within the Document
    >>> f2 = kml.Folder(ns, 'id2', 'name2', 'description2')
    >>> d.append(f2)

    # Create a Placemark with a simple polygon geometry and add it to the
    # second folder of the Document
    >>> p = kml.Placemark(ns, 'id', 'name', 'description')
    >>> p.geometry =  Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
    >>> f2.append(p)

    # Print out the KML Object as a string
    >>> print k.to_string(prettyprint=True)
    '<kml:kml xmlns:ns0="http://www.opengis.net/kml/2.2">
      <kml:Document id="docid">
        <kml:name>doc name</kml:name>
        <kml:description>doc description</kml:description>
        <kml:visibility>1</kml:visibility>
        <kml:open>0</kml:open>
        <kml:Folder id="fid">
          <kml:name>f name</kml:name>
          <kml:description>f description</kml:description>
          <kml:visibility>1</kml:visibility>
          <kml:open>0</kml:open>
          <kml:Folder id="nested-fid">
            <kml:name>nested f name</kml:name>
            <kml:description>nested f description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:open>0</kml:open>
          </kml:Folder>
        </kml:Folder>
        <kml:Folder id="id2">
          <kml:name>name2</kml:name>
          <kml:description>description2</kml:description>
          <kml:visibility>1</kml:visibility>
          <kml:open>0</kml:open>
          <kml:Placemark id="id">
            <kml:name>name</kml:name>
            <kml:description>description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:open>0</kml:open>
            <kml:Polygon>
              <kml:outerBoundaryIs>
                <kml:LinearRing>
                  <kml:coordinates>
                    0.000000,0.000000,0.000000
                    1.000000,1.000000,0.000000
                    1.000000,0.000000,1.000000
                    0.000000,0.000000,0.000000
                  </kml:coordinates>
                </kml:LinearRing>
             </kml:outerBoundaryIs>
            </kml:Polygon>
          </kml:Placemark>
        </kml:Folder>
      </kml:Document>
    </kml:kml>'



Read a KML File/String
----------------------

You can create a KML object by reading a KML file as a string

.. code-block:: python

    # Start by importing the kml module
    >>> from fastkml import kml

    #Read file into string and convert to UTF-8 (Python3 style)
    >>> with open(kml_file, 'rt', encoding="utf-8") as myfile:
    ...     doc=myfile.read()

    # OR

    # Setup the string which contains the KML file we want to read
    >>> doc = """<?xml version="1.0" encoding="UTF-8"?>
    ... <kml xmlns="http://www.opengis.net/kml/2.2">
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

    # Create the KML object to store the parsed result
    >>> k = kml.KML()

    # Read in the KML string
    >>> k.from_string(doc)

    # Next we perform some simple sanity checks

    # Check that the number of features is correct
    # This corresponds to the single ``Document``
    >>> features = list(k.features())
    >>> len(features)
    1

    # Check that we can access the features as a generator
    # (The two Placemarks of the Document)
    >>> features[0].features()
    <generator object features at 0x2d7d870>
    >>> f2 = list(features[0].features())
    >>> len(f2)
    2

    # Check specifics of the first Placemark in the Document
    >>> f2[0]
    <fastkml.kml.Placemark object at 0x2d791d0>
    >>> f2[0].description
    >>> f2[0].name
    'Document Feature 1'

    # Check specifics of the second Placemark in the Document
    >>> f2[1].name
    'Document Feature 2'
    >>> f2[1].name = "ANOTHER NAME"

    # Verify that we can print back out the KML object as a string
    >>> print k.to_string(prettyprint=True)
    <kml:kml xmlns:ns0="http://www.opengis.net/kml/2.2">
      <kml:Document>
        <kml:name>Document.kml</kml:name>
        <kml:visibility>1</kml:visibility>
        <kml:open>1</kml:open>
        <kml:Style id="exampleStyleDocument">
          <kml:LabelStyle>
            <kml:color>ff0000cc</kml:color>
            <kml:scale>1.0</kml:scale>
          </kml:LabelStyle>
        </kml:Style>
        <kml:Placemark>
          <kml:name>Document Feature 1</kml:name>
          <kml:visibility>1</kml:visibility>
          <kml:open>0</kml:open>
          <kml:Point>
            <kml:coordinates>-122.371000,37.816000,0.000000</kml:coordinates>
          </kml:Point>
        </kml:Placemark>
        <kml:Placemark>
          <kml:name>ANOTHER NAME</kml:name>
          <kml:visibility>1</kml:visibility>
          <kml:open>0</kml:open>
          <kml:Point>
            <kml:coordinates>-122.370000,37.817000,0.000000</kml:coordinates>
          </kml:Point>
        </kml:Placemark>
      </kml:Document>
    </kml:kml>

.. _collective.geo.fastkml: https://pypi.python.org/pypi/collective.geo.fastkml
