# -*- coding: utf-8 -*-
# Copyright (C) 2012  Christian Ledermann
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""
Import the geometries from shapely if it is installed or otherwise from Pygeoif
"""

try:
    from shapely.geometry import Point, LineString, Polygon
    from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
    from shapely.geometry.polygon import LinearRing
    # from shapely.geometry import GeometryCollection
    # Sean Gillies:
    # I deliberately omitted a geometry collection constructor because
    # there was almost no support in GEOS for operations on them. You
    # couldn't buffer a collection, for example, or find its difference
    # to another geometry. I've seen some signs of this changing in GEOS,
    # but until it does I don't think there's any point to the class.
    # It wouldn't be much more than a list of geometries.
    from pygeoif.geometry import GeometryCollection
    from shapely.geometry import asShape

except ImportError:
    from pygeoif.geometry import Point, LineString, Polygon
    from pygeoif.geometry import MultiPoint, MultiLineString, MultiPolygon
    from pygeoif.geometry import LinearRing
    from pygeoif.geometry import GeometryCollection
    from pygeoif.geometry import as_shape as asShape

import re
import fastkml.config as config

from .config import etree

from .base import _BaseObject

import logging
logger = logging.getLogger('fastkml.geometry')


class Geometry(_BaseObject):
    """

    """
    __name__ = None
    geometry = None
    extrude = False
    tessellate = False
    altitude_mode = None

    def __init__(
        self, ns=None, id=None, geometry=None, extrude=False,
        tessellate=False, altitude_mode=None
    ):
        """
        geometry: a geometry that implements the __geo_interface__ convention

        extrude: boolean --> Specifies whether to connect the feature to
            the ground with a line. To extrude a Feature, the value for
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
            if isinstance(
                geometry,
                (
                    Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    LinearRing, GeometryCollection
                )
            ):
                self.geometry = geometry
            else:
                self.geometry = asShape(geometry)

# write kml

    def _set_altitude_mode(self, element):
        if self.altitude_mode:
            # XXX add 'relativeToSeaFloor', 'clampToSeaFloor',
            assert(self.altitude_mode in [
                'clampToGround',
                'relativeToGround', 'absolute'
            ])
            if self.altitude_mode != 'clampToGround':
                am_element = etree.SubElement(
                    element, "%saltitudeMode" % self.ns
                )
                am_element.text = self.altitude_mode

    def _set_extrude(self, element):
        if self.extrude and self.altitude_mode in [
            'relativeToGround',
            # 'relativeToSeaFloor',
            'absolute'
        ]:
            et_element = etree.SubElement(element, "%sextrude" % self.ns)
            et_element.text = '1'

    def _etree_coordinates(self, coordinates):
        # clampToGround = (
        #     (self.altitude_mode == 'clampToGround')
        #     or (self.altitude_mode is None)
        # )
        element = etree.Element("%scoordinates" % self.ns)
        if len(coordinates[0]) == 2:
            if config.FORCE3D:  # and not clampToGround:
                tuples = ('%f,%f,0.000000' % tuple(c) for c in coordinates)
            else:
                tuples = ('%f,%f' % tuple(c) for c in coordinates)
        elif len(coordinates[0]) == 3:
            # if clampToGround:
                # if the altitude is ignored anyway, we may as well
                # ignore the z-value
            #    tuples = ('%f,%f' % tuple(c[:2]) for c in coordinates)
            # else:
            tuples = ('%f,%f,%f' % tuple(c) for c in coordinates)
        else:
            raise ValueError("Invalid dimensions")
        element.text = ' '.join(tuples)
        return element

    def _etree_point(self, point):
        element = etree.Element("%sPoint" % self.ns)
        self._set_extrude(element)
        self._set_altitude_mode(element)
        coords = list(point.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_linestring(self, linestring):
        element = etree.Element("%sLineString" % self.ns)
        self._set_extrude(element)
        self._set_altitude_mode(element)
        if self.tessellate and self.altitude_mode in [
            'clampToGround',
            'clampToSeaFloor'
        ]:
            ts_element = etree.SubElement(element, "%stessellate" % self.ns)
            ts_element.text = '1'
        coords = list(linestring.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_linearring(self, linearring):
        element = etree.Element("%sLinearRing" % self.ns)
        self._set_extrude(element)
        self._set_altitude_mode(element)
        # tesseleation is ignored by polygon and tesselation together with
        # LinearRing without a polygon very rare Edgecase -> ignore for now
        # if self.tessellate and self.altitude_mode in ['clampToGround',
        #        'clampToSeaFloor']:
        #    element.set('tessellate', '1')
        coords = list(linearring.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_polygon(self, polygon):
        element = etree.Element("%sPolygon" % self.ns)
        self._set_extrude(element)
        self._set_altitude_mode(element)
        outer_boundary = etree.SubElement(
            element, "%souterBoundaryIs" % self.ns
        )
        outer_boundary.append(self._etree_linearring(polygon.exterior))
        for ib in polygon.interiors:
            inner_boundary = etree.SubElement(
                element, "%sinnerBoundaryIs" % self.ns
            )
            inner_boundary.append(self._etree_linearring(ib))
        return element

    def _etree_multipoint(self, points):
        element = etree.Element("%sMultiGeometry" % self.ns)
        for point in points.geoms:
            element.append(self._etree_point(point))
        return element

    def _etree_multilinestring(self, linestrings):
        element = etree.Element("%sMultiGeometry" % self.ns)
        for linestring in linestrings.geoms:
            element.append(self._etree_linestring(linestring))
        return element

    def _etree_multipolygon(self, polygons):
        element = etree.Element("%sMultiGeometry" % self.ns)
        for polygon in polygons.geoms:
            element.append(self._etree_polygon(polygon))
        return element

    def _etree_collection(self, features):
        element = etree.Element("%sMultiGeometry" % self.ns)
        for feature in features.geoms:
            if feature.geom_type == "Point":
                element.append(self._etree_point(feature))
            elif feature.geom_type == "LinearRing":
                element.append(self._etree_linearring(feature))
            elif feature.geom_type == "LineString":
                element.append(self._etree_linestring(feature))
            elif feature.geom_type == "Polygon":
                element.append(self._etree_polygon(feature))
            else:
                raise ValueError("Illegal geometry type.")
        return element

    def etree_element(self):
        if isinstance(self.geometry, Point):
            return self._etree_point(self.geometry)
        elif isinstance(self.geometry, LinearRing):
            return self._etree_linearring(self.geometry)
        elif isinstance(self.geometry, LineString):
            return self._etree_linestring(self.geometry)
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

# read kml

    def _get_geometry_spec(self, element):
        extrude = element.find('%sextrude' % self.ns)
        if extrude is not None:
            try:
                et = bool(int(extrude.text.strip()))
            except ValueError:
                et = False
            self.extrude = et
        else:
            self.extrude = False
        tessellate = element.find('%stessellate' % self.ns)
        if tessellate is not None:
            try:
                te = bool(int(tessellate.text.strip()))
            except ValueError:
                te = False
            self.tessellate = te
        else:
            self.tessellate = False
        altitude_mode = element.find('%saltitudeMode' % self.ns)
        if altitude_mode is not None:
            am = altitude_mode.text.strip()
            if am in [
                'clampToGround',
                # 'relativeToSeaFloor', 'clampToSeaFloor',
                'relativeToGround', 'absolute'
            ]:
                self.altitude_mode = am
            else:
                self.altitude_mode = None
        else:
            self.altitude_mode = None

    def _get_coordinates(self, element):
        coordinates = element.find('%scoordinates' % self.ns)
        if coordinates is not None:
            # https://developers.google.com/kml/documentation/kmlreference#coordinates
            # Coordinates can be any number of tuples separated by a
            # space (potentially any number of whitespace characters).
            # Values in tuples should be separated by commas with no
            # spaces. Clean up badly formatted tuples by stripping
            # space following commas.
            latlons = re.sub(r', +', ',', coordinates.text.strip()).split()
            coords = []
            for latlon in latlons:
                coords.append([float(c) for c in latlon.split(',')])
            return coords

    def _get_linear_ring(self, element):
        # LinearRing in polygon
        lr = element.find('%sLinearRing' % self.ns)
        if lr is not None:
            coords = self._get_coordinates(lr)
            return LinearRing(coords)

    def _get_geometry(self, element):
        # Point, LineString,
        # Polygon, LinearRing
        if element.tag == ('%sPoint' % self.ns):
            coords = self._get_coordinates(element)
            self._get_geometry_spec(element)
            return Point(coords[0])
        if element.tag == ('%sLineString' % self.ns):
            coords = self._get_coordinates(element)
            self._get_geometry_spec(element)
            return LineString(coords)
        if element.tag == ('%sPolygon' % self.ns):
            self._get_geometry_spec(element)
            outer_boundary = element.find('%souterBoundaryIs' % self.ns)
            ob = self._get_linear_ring(outer_boundary)
            inner_boundaries = element.findall('%sinnerBoundaryIs' % self.ns)
            ibs = []
            for inner_boundary in inner_boundaries:
                ibs.append(self._get_linear_ring(inner_boundary))
            return Polygon(ob, ibs)
        if element.tag == ('%sLinearRing' % self.ns):
            coords = self._get_coordinates(element)
            self._get_geometry_spec(element)
            return LinearRing(coords)

    def _get_multigeometry(self, element):
        # MultiGeometry
        geoms = []
        if element.tag == ('%sMultiGeometry' % self.ns):
            points = element.findall('%sPoint' % self.ns)
            if points:
                for point in points:
                    self._get_geometry_spec(point)
                    geoms.append(Point(self._get_coordinates(point)[0]))
            linestrings = element.findall('%sLineString' % self.ns)
            if linestrings:
                for ls in linestrings:
                    self._get_geometry_spec(ls)
                    geoms.append(LineString(self._get_coordinates(ls)))
            polygons = element.findall('%sPolygon' % self.ns)
            if polygons:
                for polygon in polygons:
                    self._get_geometry_spec(polygon)
                    outer_boundary = polygon.find(
                        '%souterBoundaryIs' % self.ns
                    )
                    ob = self._get_linear_ring(outer_boundary)
                    inner_boundaries = polygon.findall(
                        '%sinnerBoundaryIs' % self.ns
                    )
                    ibs = []
                    for inner_boundary in inner_boundaries:
                        ibs.append(self._get_linear_ring(inner_boundary))
                    geoms.append(Polygon(ob, ibs))
            linearings = element.findall('%sLinearRing' % self.ns)
            if linearings:
                for lr in linearings:
                    self._get_geometry_spec(lr)
                    geoms.append(LinearRing(self._get_coordinates(lr)))
        if len(geoms) > 0:
            geom_types = []
            for geom in geoms:
                geom_types.append(geom.geom_type)
            geom_types = list(set(geom_types))
            if len(geom_types) > 1:
                return GeometryCollection(geoms)
            if geom_types[0] == 'Point':
                return MultiPoint(geoms)
            elif geom_types[0] == 'LineString':
                return MultiLineString(geoms)
            elif geom_types[0] == 'Polygon':
                return MultiPolygon(geoms)
            elif geom_types[0] == 'LinearRing':
                return GeometryCollection(geoms)

    def from_element(self, element):
        geom = self._get_geometry(element)
        if geom is not None:
            self.geometry = geom
        else:
            mgeom = self._get_multigeometry(element)
            if mgeom is not None:
                self.geometry = mgeom
            else:
                logger.warn('No geometries found')
