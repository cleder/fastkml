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
    from shapely.geometry import GeometryCollection
    from shapely.geometry import asShape

except ImportError:
    from pygeoif.geometry import Point, LineString, Polygon
    from pygeoif.geometry import MultiPoint, MultiLineString, MultiPolygon
    from pygeoif.geometry import LinearRing
    from pygeoif.geometry import GeometryCollection
    from pygeoif.geometry import as_shape as asShape

import config
from config import etree

from base import _BaseObject

class Geometry(_BaseObject):
    """

    """
    __name__ = None
    geometry = None
    extrude = False
    tessellate = False
    altitude_mode = None


    def __init__(self, ns=None, id=None, geometry=None, extrude=False,
                tessellate=False, altitude_mode=None):
        """
        geometry: a geometry that implements the __geo_interface__ convention

        extrude: boolean --> Specifies whether to connect the feature to
            the ground with a line. To extrude a Point, the value for
            'altitudeMode' must be either relativeToGround, relativeToSeaFloor,
            or absolute. The feature is extruded toward the center of the
            Earth's sphere.
        tessellate: boolean -->  Specifies whether to allow the LineString
            to follow the terrain. To enable tessellation, the altitude
            mode must be clampToGround or clampToSeaFloor. Very large
            LineStrings should enable tessellation so that they follow
            the curvature of the earth (otherwise, they may go underground
            and be hidden).
            This field is not used by Polygon or Point. To allow a Polygon
            to follow the terrain (that is, to enable tessellation) specify
            an altitude mode of clampToGround or clampToSeaFloor.
        altitudeMode: [clampToGround, relativeToGround, absolute] -->
            Specifies how altitude components in the <coordinates> element
            are interpreted. Possible values are
                clampToGround - (default) Indicates to ignore an altitude
                    specification.
                relativeToGround - Sets the altitude of the element relative
                    to the actual ground elevation of a particular location.
                    For example, if the ground elevation of a location is
                    exactly at sea level and the altitude for a point is
                    set to 9 meters, then the elevation for the icon of a
                    point placemark elevation is 9 meters with this mode.
                    However, if the same coordinate is set over a location
                    where the ground elevation is 10 meters above sea level,
                    then the elevation of the coordinate is 19 meters.
                    A typical use of this mode is for placing telephone
                    poles or a ski lift.
                absolute - Sets the altitude of the coordinate relative to
                    sea level, regardless of the actual elevation of the
                    terrain beneath the element. For example, if you set
                    the altitude of a coordinate to 10 meters with an
                    absolute altitude mode, the icon of a point placemark
                    will appear to be at ground level if the terrain beneath
                    is also 10 meters above sea level. If the terrain is
                    3 meters above sea level, the placemark will appear
                    elevated above the terrain by 7 meters. A typical use
                    of this mode is for aircraft placement.
        """
        super(Geometry, self).__init__(ns, id)
        self.extrude = extrude
        self.tessellate = tessellate
        self.altitude_mode = altitude_mode
        if geometry:
            if isinstance(geometry, (Point, LineString, Polygon,
                        MultiPoint, MultiLineString, MultiPolygon,
                        LinearRing, GeometryCollection)):
                self.geometry = geometry
            else:
                self.geometry = asShape(geometry)


    def _etree_coordinates(self, coordinates):
        clampToGround = (self.altitude_mode == 'clampToGround') or (self.altitude_mode == None)
        element = etree.Element("%scoordinates" %self.ns)
        if len(coordinates[0]) == 2:
            if config.FORCE3D and not clampToGround:
                tuples = ('%f,%f,0.000000' % tuple(c) for c in coordinates)
            else:
                tuples = ('%f,%f' % tuple(c) for c in coordinates)
        elif len(coordinates[0]) == 3:
            if clampToGround:
                # if the altitude is ignored anyway, we may as well
                # ignore the z-value
                tuples = ('%f,%f' % tuple(c[:2]) for c in coordinates)
            else:
                tuples = ('%f,%f,%f' % tuple(c) for c in coordinates)
        else:
            raise ValueError("Invalid dimensions")
        element.text = ' '.join(tuples)
        return element

    def _etree_point(self, point):
        element = etree.Element("%sPoint" %self.ns)
        coords = list(point.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_linestring(self, linestring):
        element = etree.Element("%sLineString" %self.ns)
        coords = list(linestring.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_linearring(self, linearring):
        element = etree.Element("%sLinearRing" %self.ns)
        coords = list(linearring.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_polygon(self, polygon):
        element = etree.Element("%sPolygon" %self.ns)
        outer_boundary = etree.SubElement(element, "%souterBoundaryIs" %self.ns)
        outer_boundary.append(self._etree_linearring(polygon.exterior))
        for ib in polygon.interiors:
            inner_boundary = etree.SubElement(element, "%sinnerBoundaryIs" %self.ns)
            inner_boundary.append(self._etree_linearring(ib))
        return element

    def _etree_multipoint(self, points):
        element = etree.Element("%sMultiGeometry" %self.ns)
        for point in points.geoms:
            element.append(self._etree_point(point))
        return element

    def _etree_multilinestring(self, linestrings):
        element = etree.Element("%sMultiGeometry" %self.ns)
        for linestring in linestrings.geoms:
            element.append(self._etree_linestring(linestring))
        return element

    def _etree_multipolygon(self, polygons):
        element = etree.Element("%sMultiGeometry" %self.ns)
        for polygon in polygons.geoms:
            element.append(self._etree_polygon(polygon))
        return element

    def _etree_collection(self, features):
        element = etree.Element("%sMultiGeometry" %self.ns)
        for feature in features.geoms:
            if isinstance(feature, Point):
                element.append(self._etree_point(feature))
            elif isinstance(feature, LineString):
                element.append(self._etree_linestring(feature))
            elif isinstance(feature, LinearRing):
                element.append(self._etree_linearring(feature))
            elif isinstance(feature, Polygon):
                element.append(self._etree_polygon(feature))
            else:
                raise ValueError("Illegal geometry type.")
        return element

    def etree_element(self):
        if isinstance(self.geometry, Point):
            return self._etree_point(self.geometry)
        elif isinstance(self.geometry, LineString):
            return self._etree_linestring(self.geometry)
        elif isinstance(self.geometry, LinearRing):
            return self._etree_linearring(self.geometry)
        elif isinstance(self.geometry, Polygon):
            return self._etree_polygon(self.geometry)
        elif isinstance(self.geometry, MultiPoint):
            return self._etree_multipoint(self.geometry)
        elif isinstance(self.geometry, MultiLineString):
            return self._etree_multilinestring(self.geometry)
        elif isinstance(self.geometry, MultiPolygon):
            return self._etree_multipolygon(self.geometry)
        elif isinstance(self.geometry, GeometryCollection):
            return self._etree_collection(self.geometry)
        else:
            raise ValueError("Illegal geometry type.")

