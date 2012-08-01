# -*- coding: utf-8 -*-
#    Copyright (C) 2012  Christian Ledermann
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""
Import the geometries from shapely if it is installed
or otherwise from Pygeoif

"""
try:
    from shapely.geometry import Point, LineString, Polygon
    from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
    from shapely.geometry.polygon import LinearRing

except ImportError:
    from pygeoif.geometry import Point, LineString, Polygon
    from pygeoif.geometry import MultiPoint, MultiLineString, MultiPolygon
    from pygeoif.geometry import LinearRing
