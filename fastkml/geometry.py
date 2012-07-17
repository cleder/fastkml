# -*- coding: utf-8 -*-
"""
This should be rewritten to implement a more general and less
Shapely dependent way to represent geometries

https://gist.github.com/2217756

I wonder if the "geojson" package fits
the purpose or it's rather better to implement to protocol from scratch.

"""
from shapely.geometry import Point, LineString, Polygon
from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
from shapely.geometry.polygon import LinearRing

