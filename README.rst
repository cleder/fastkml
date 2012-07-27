Introduction
============

fastkml is a library to read, write and manipulate kml files. The aims
are to keep it simple and fast (using lxml if available). Fast refers to
the time you spend to write and read KML files as well as the time you
spend to get aquainted to the library or to create KML objects. It provides
a subset of KML and is aimed at documents that can be read from multiple
clients such as openlayers and google maps rather than to give you all
functionality that KML on google earth provides.

Geometries are handled as pygeoif or shapely (if installed) objects.



Limitations
===========

Geometries are limited to the geometry and multigeometry types shapely
provides (Point, LineString, Polygon, MultiPoint, MultiLineString,
MultiPolygon and LinearRing). While KML allows for more abstract
MultiGeometries consisting of a combination of Points, LineStrings
and LinearRings, this is not supported in fastkml.
This is a restriction that I can live with and you will rarely find KML
files that implement more complex geometries.

Usage
=====

You can find more examples in the included tests.py file, here is a
quick overview:


Build a KML from scratch:
--------------------------

Example how to build a simple KML file

    >>> from fastkml import kml
    >>> from shapely.geometry import Point, LineString, Polygon
    >>> k = kml.KML()
    >>> ns = '{http://www.opengis.net/kml/2.2}'
    >>> d = kml.Document(ns, 'docid', 'doc name', 'doc description')
    >>> f = kml.Folder(ns, 'fid', 'f name', 'f description')
    >>> k.append(d)
    >>> d.append(f)
    >>> nf = kml.Folder(ns, 'nested-fid', 'nested f name', 'nested f description')
    >>> f.append(nf)
    >>> f2 = kml.Folder(ns, 'id2', 'name2', 'description2')
    >>> d.append(f2)
    >>> p = kml.Placemark(ns, 'id', 'name', 'description')
    >>> p.geometry =  Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
    >>> f2.append(p)
    >>> print k.to_string(prettyprint=True)
    '<ns0:kml xmlns:ns0="http://www.opengis.net/kml/2.2">
      <ns0:Document id="docid">
        <ns0:name>doc name</ns0:name>
        <ns0:description>doc description</ns0:description>
        <ns0:visibility>1</ns0:visibility>
        <ns0:open>0</ns0:open>
        <ns0:Folder id="fid">
          <ns0:name>f name</ns0:name>
          <ns0:description>f description</ns0:description>
          <ns0:visibility>1</ns0:visibility>
          <ns0:open>0</ns0:open>
          <ns0:Folder id="nested-fid">
            <ns0:name>nested f name</ns0:name>
            <ns0:description>nested f description</ns0:description>
            <ns0:visibility>1</ns0:visibility>
            <ns0:open>0</ns0:open>
          </ns0:Folder>
        </ns0:Folder>
        <ns0:Folder id="id2">
          <ns0:name>name2</ns0:name>
          <ns0:description>description2</ns0:description>
          <ns0:visibility>1</ns0:visibility>
          <ns0:open>0</ns0:open>
          <ns0:Placemark id="id">
            <ns0:name>name</ns0:name>
            <ns0:description>description</ns0:description>
            <ns0:visibility>1</ns0:visibility>
            <ns0:open>0</ns0:open>
            <ns0:Polygon>
              <ns0:outerBoundaryIs>
                <ns0:LinearRing>
                  <ns0:coordinates>0.000000,0.000000,0.000000
                  1.000000,1.000000,0.000000
                  1.000000,0.000000,1.000000
                  0.000000,0.000000,0.000000
                  </ns0:coordinates>
                </ns0:LinearRing>
             </ns0:outerBoundaryIs>
            </ns0:Polygon>
          </ns0:Placemark>
        </ns0:Folder>
      </ns0:Document>
    </ns0:kml>'



Read a KML file
----------------

You can create a KML object by reading a KML file

    >>> from fastkml import kml
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
    >>> k = kml.KML()
    >>> k.from_string(doc)
    >>> len(k.features())
    1
    >>> len(k.features()[0].features())
    2
    >>> k.features()[0].features()[1]
    <fastkml.kml.Placemark object at 0x876a16c>
    >>> k.features()[0].features()[1].description
    >>> k.features()[0].features()[1].name
    'Document Feature 2'
    >>> k.features()[0].features()[1].name = "ANOTHER NAME"
    >>> print k.to_string(prettyprint=True)
    <ns0:kml xmlns:ns0="http://www.opengis.net/kml/2.2">
      <ns0:Document>
        <ns0:name>Document.kml</ns0:name>
        <ns0:visibility>1</ns0:visibility>
        <ns0:open>1</ns0:open>
        <ns0:Style id="exampleStyleDocument">
          <ns0:LabelStyle>
            <ns0:color>ff0000cc</ns0:color>
            <ns0:scale>1.0</ns0:scale>
          </ns0:LabelStyle>
        </ns0:Style>
        <ns0:Placemark>
          <ns0:name>Document Feature 1</ns0:name>
          <ns0:visibility>1</ns0:visibility>
          <ns0:open>0</ns0:open>
          <ns0:Point>
            <ns0:coordinates>-122.371000,37.816000,0.000000</ns0:coordinates>
          </ns0:Point>
        </ns0:Placemark>
        <ns0:Placemark>
          <ns0:name>ANOTHER NAME</ns0:name>
          <ns0:visibility>1</ns0:visibility>
          <ns0:open>0</ns0:open>
          <ns0:Point>
            <ns0:coordinates>-122.370000,37.817000,0.000000</ns0:coordinates>
          </ns0:Point>
        </ns0:Placemark>
      </ns0:Document>
    </ns0:kml>





