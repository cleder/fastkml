Introduction
============

fastkml is a library to read, write and manipulate kml files. The aims
are to keep it simple and fast (using lxml if available). Fast refers to
the time you spend to write and read KML files as well as the time you
spend to get aquainted to the library or to create KML objects. It provides
a subset of KML and is aimed at documents that can be read from multiple
clients such as openlayers and google maps rather than to give you all
functionality that KML on google earth provides.

Geometries are handled as shapely objects. This is a restriction that I
can live with and you will seldom find KML files that implement more
complex geometries.


Limitations
===========

Geometries are limited to the geometry and multigeometry types shapely
provides (Point, LineString, Polygon, MultiPoint, MultiLineString,
MultiPolygon and LinearRing). While KML allows for more abstract
MultiGeometries consisting of a combination of Points, LineStrings
and LinearRings, this is not supported in fastkml
