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

import contextlib
import logging
import re
from functools import partial
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union
from typing import cast
from typing import no_type_check

import pygeoif.geometry as geo
from pygeoif.factories import shape
from pygeoif.types import PointType

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity
from fastkml.exceptions import KMLParseError
from fastkml.exceptions import KMLWriteError
from fastkml.types import Element

logger = logging.getLogger(__name__)

GeometryType = Union[geo.Polygon, geo.LineString, geo.LinearRing, geo.Point]
MultiGeometryType = Union[
    geo.MultiPoint, geo.MultiLineString, geo.MultiPolygon, geo.GeometryCollection
]
AnyGeometryType = Union[GeometryType, MultiGeometryType]


class Geometry(_BaseObject):
    """Deprecated: to be replaced by the subclasses of _Geometry."""

    geometry = None
    extrude = False
    tessellate = False
    altitude_mode = Optional[AltitudeMode]

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        geometry: Optional[Any] = None,
        extrude: bool = False,
        tessellate: bool = False,
        altitude_mode: Optional[AltitudeMode] = None,
    ) -> None:
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

        https://developers.google.com/kml/documentation/kmlreference#geometry
        """
        super().__init__(ns=ns, id=id, target_id=target_id)
        self.extrude = extrude
        self.tessellate = tessellate
        self.altitude_mode = altitude_mode  # type: ignore[assignment]
        if geometry:
            if isinstance(
                geometry,
                (
                    geo.Point,
                    geo.LineString,
                    geo.Polygon,
                    geo.MultiPoint,
                    geo.MultiLineString,
                    geo.MultiPolygon,
                    geo.LinearRing,
                    geo.GeometryCollection,
                ),
            ):
                self.geometry = geometry
            else:
                self.geometry = shape(geometry)

    # write kml

    def _set_altitude_mode(self, element: Element) -> None:
        if self.altitude_mode:
            # assert self.altitude_mode in [
            #     "clampToGround",
            #     "relativeToGround",
            #     "absolute",
            # ]
            # if self.altitude_mode != "clampToGround":
            am_element = config.etree.SubElement(  # type: ignore[attr-defined]
                element, f"{self.ns}altitudeMode"
            )
            am_element.text = self.altitude_mode.value  # type: ignore[attr-defined]

    def _set_extrude(self, element: Element) -> None:
        if self.extrude and self.altitude_mode in [  # type: ignore[comparison-overlap]
            AltitudeMode.relative_to_ground,
            AltitudeMode.relative_to_sea_floor,
            AltitudeMode.absolute,
        ]:
            et_element = cast(
                Element,
                config.etree.SubElement(  # type: ignore[attr-defined]
                    element, f"{self.ns}extrude"
                ),
            )
            et_element.text = "1"

    def _etree_coordinates(
        self,
        coordinates: Sequence[PointType],
    ) -> Element:
        element = cast(
            Element,
            config.etree.Element(f"{self.ns}coordinates"),  # type: ignore[attr-defined]
        )
        if len(coordinates[0]) == 2:
            tuples = (f"{c[0]:f},{c[1]:f}" for c in coordinates)
        elif len(coordinates[0]) == 3:
            tuples = (
                f"{c[0]:f},{c[1]:f},{c[2]:f}" for c in coordinates  # type: ignore[misc]
            )
        else:
            raise ValueError("Invalid dimensions")
        element.text = " ".join(tuples)
        return element

    def _etree_point(self, point: geo.Point) -> Element:
        element = self._extrude_and_altitude_mode("Point")
        coords = list(point.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_linestring(self, linestring: geo.LineString) -> Element:
        element = self._extrude_and_altitude_mode("LineString")
        if (
            self.tessellate
            and self.altitude_mode
            in [  # type: ignore[comparison-overlap]
                "clampToGround",
                "clampToSeaFloor",
            ]
        ):
            ts_element = config.etree.SubElement(  # type: ignore[attr-defined]
                element, f"{self.ns}tessellate"
            )
            ts_element.text = "1"
        coords = list(linestring.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_linearring(self, linearring: geo.LinearRing) -> Element:
        element = self._extrude_and_altitude_mode("LinearRing")
        coords = list(linearring.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_polygon(self, polygon: geo.Polygon) -> Element:
        element = self._extrude_and_altitude_mode("Polygon")
        outer_boundary = cast(
            Element,
            config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}outerBoundaryIs",
            ),
        )
        outer_boundary.append(self._etree_linearring(polygon.exterior))
        for ib in polygon.interiors:
            inner_boundary = cast(
                Element,
                config.etree.SubElement(  # type: ignore[attr-defined]
                    element,
                    f"{self.ns}innerBoundaryIs",
                ),
            )
            inner_boundary.append(self._etree_linearring(ib))
        return element

    def _extrude_and_altitude_mode(self, kml_geometry: str) -> Element:
        result = cast(
            Element,
            config.etree.Element(  # type: ignore[attr-defined]
                f"{self.ns}{kml_geometry}"
            ),
        )
        self._set_extrude(result)
        self._set_altitude_mode(result)
        return result

    def _etree_multipoint(self, points: geo.MultiPoint) -> Element:
        element = cast(
            Element,
            config.etree.Element(  # type: ignore[attr-defined]
                f"{self.ns}MultiGeometry"
            ),
        )
        for point in points.geoms:
            element.append(self._etree_point(point))
        return element

    def _etree_multilinestring(self, linestrings: geo.MultiLineString) -> Element:
        element = cast(
            Element,
            config.etree.Element(  # type: ignore[attr-defined]
                f"{self.ns}MultiGeometry"
            ),
        )
        for linestring in linestrings.geoms:
            element.append(self._etree_linestring(linestring))
        return element

    def _etree_multipolygon(self, polygons: geo.MultiPolygon) -> Element:
        element = cast(
            Element,
            config.etree.Element(  # type: ignore[attr-defined]
                f"{self.ns}MultiGeometry"
            ),
        )
        for polygon in polygons.geoms:
            element.append(self._etree_polygon(polygon))
        return element

    def _etree_collection(self, features: geo.GeometryCollection) -> Element:
        element = cast(
            Element,
            config.etree.Element(  # type: ignore[attr-defined]
                f"{self.ns}MultiGeometry"
            ),
        )
        for feature in features.geoms:
            if feature.geom_type == "Point":
                element.append(self._etree_point(cast(geo.Point, feature)))
            elif feature.geom_type == "LinearRing":
                element.append(self._etree_linearring(cast(geo.LinearRing, feature)))
            elif feature.geom_type == "LineString":
                element.append(self._etree_linestring(cast(geo.LineString, feature)))
            elif feature.geom_type == "Polygon":
                element.append(self._etree_polygon(cast(geo.Polygon, feature)))
            else:
                raise ValueError("Illegal geometry type.")
        return element

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        if isinstance(self.geometry, geo.Point):
            return self._etree_point(self.geometry)
        elif isinstance(self.geometry, geo.LinearRing):
            return self._etree_linearring(self.geometry)
        elif isinstance(self.geometry, geo.LineString):
            return self._etree_linestring(self.geometry)
        elif isinstance(self.geometry, geo.Polygon):
            return self._etree_polygon(self.geometry)
        elif isinstance(self.geometry, geo.MultiPoint):
            return self._etree_multipoint(self.geometry)
        elif isinstance(self.geometry, geo.MultiLineString):
            return self._etree_multilinestring(self.geometry)
        elif isinstance(self.geometry, geo.MultiPolygon):
            return self._etree_multipolygon(self.geometry)
        elif isinstance(self.geometry, geo.GeometryCollection):
            return self._etree_collection(self.geometry)
        else:
            raise ValueError("Illegal geometry type.")

    # read kml

    def _get_geometry_spec(self, element: Element) -> None:
        extrude = element.find(f"{self.ns}extrude")
        if extrude is not None:
            try:
                et = bool(int(extrude.text.strip()))
            except ValueError:
                et = False
            self.extrude = et
        else:
            self.extrude = False
        tessellate = element.find(f"{self.ns}tessellate")
        if tessellate is not None:
            try:
                te = bool(int(tessellate.text.strip()))
            except ValueError:
                te = False
            self.tessellate = te
        else:
            self.tessellate = False
        altitude_mode = element.find(f"{self.ns}altitudeMode")
        if altitude_mode is not None:
            am = altitude_mode.text.strip()
            try:
                self.altitude_mode = AltitudeMode(am)  # type: ignore[assignment]
            except ValueError:
                self.altitude_mode = None  # type: ignore[assignment]
        else:
            self.altitude_mode = None  # type: ignore[assignment]

    @no_type_check
    def _get_coordinates(
        self, element: Element, strict: bool = False
    ) -> List[PointType]:
        coordinates = element.find(f"{self.ns}coordinates")
        if coordinates is not None:
            # https://developers.google.com/kml/documentation/kmlreference#coordinates
            # Coordinates can be any number of tuples separated by a
            # space (potentially any number of whitespace characters).
            # Values in tuples should be separated by commas with no
            # spaces. Clean up badly formatted tuples by stripping
            # space following commas.
            latlons = re.sub(r", +", ",", coordinates.text.strip()).split()
            return [
                cast(PointType, tuple(float(c) for c in latlon.split(",")))
                for latlon in latlons
            ]

    def _get_linear_ring(self, element: Element) -> Optional[geo.LinearRing]:
        # LinearRing in polygon
        lr = element.find(f"{self.ns}LinearRing")
        if lr is not None:
            coords = self._get_coordinates(lr)
            return geo.LinearRing(coords)
        return None

    @no_type_check
    def _get_geometry(self, element: Element) -> Optional[GeometryType]:
        # Point, LineString,
        # Polygon, LinearRing
        if element.tag == f"{self.ns}Point":
            coords = self._get_coordinates(element)
            self._get_geometry_spec(element)
            return geo.Point.from_coordinates(coords)
        if element.tag == f"{self.ns}LineString":
            coords = self._get_coordinates(element)
            self._get_geometry_spec(element)
            return geo.LineString(coords)
        if element.tag == f"{self.ns}Polygon":
            self._get_geometry_spec(element)
            outer_boundary = element.find(f"{self.ns}outerBoundaryIs")
            ob = self._get_linear_ring(outer_boundary)
            if not ob:
                return None
            inner_boundaries = element.findall(f"{self.ns}innerBoundaryIs")
            ibs = [
                self._get_linear_ring(inner_boundary)
                for inner_boundary in inner_boundaries
            ]
            return geo.Polygon.from_linear_rings(ob, *[b for b in ibs if b])
        if element.tag == f"{self.ns}LinearRing":
            coords = self._get_coordinates(element)
            self._get_geometry_spec(element)
            return geo.LinearRing(coords)
        return None

    @no_type_check
    def _get_multigeometry(self, element: Element) -> Optional[MultiGeometryType]:
        # MultiGeometry
        geoms: List[Union[AnyGeometryType, None]] = []
        if element.tag == f"{self.ns}MultiGeometry":
            multigeometries = element.findall(f"{self.ns}MultiGeometry")
            for multigeometry in multigeometries:
                geom = Geometry(ns=self.ns)
                geom.from_element(multigeometry)
                geoms.append(geom.geometry)
            points = element.findall(f"{self.ns}Point")
            for point in points:
                self._get_geometry_spec(point)
                geoms.append(geo.Point.from_coordinates(self._get_coordinates(point)))
            linestrings = element.findall(f"{self.ns}LineString")
            for ls in linestrings:
                self._get_geometry_spec(ls)
                geoms.append(geo.LineString(self._get_coordinates(ls)))
            polygons = element.findall(f"{self.ns}Polygon")
            for polygon in polygons:
                self._get_geometry_spec(polygon)
                outer_boundary = polygon.find(f"{self.ns}outerBoundaryIs")
                ob = self._get_linear_ring(outer_boundary)
                if not ob:
                    continue
                inner_boundaries = polygon.findall(f"{self.ns}innerBoundaryIs")
                inner_bs = [
                    self._get_linear_ring(inner_boundary)
                    for inner_boundary in inner_boundaries
                ]
                ibs: List[geo.LinearRing] = [ib for ib in inner_bs if ib]
                geoms.append(geo.Polygon.from_linear_rings(ob, *ibs))
            linearings = element.findall(f"{self.ns}LinearRing")
            if linearings:
                for lr in linearings:
                    self._get_geometry_spec(lr)
                    geoms.append(geo.LinearRing(self._get_coordinates(lr)))
        clean_geoms: List[AnyGeometryType] = [g for g in geoms if g]
        if clean_geoms:
            geom_types = {geom.geom_type for geom in clean_geoms}
            if len(geom_types) > 1:
                return geo.GeometryCollection(
                    clean_geoms,
                )
            if "Point" in geom_types:
                return geo.MultiPoint.from_points(
                    *clean_geoms,
                )
            elif "LineString" in geom_types:
                return geo.MultiLineString.from_linestrings(
                    *clean_geoms,
                )
            elif "Polygon" in geom_types:
                return geo.MultiPolygon.from_polygons(
                    *clean_geoms,
                )
            elif "LinearRing" in geom_types:
                return geo.GeometryCollection(
                    clean_geoms,
                )
        return None

    def from_element(self, element: Element) -> None:
        geom = self._get_geometry(element)
        if geom is not None:
            self.geometry = geom
        else:
            mgeom = self._get_multigeometry(element)
            if mgeom is not None:
                self.geometry = mgeom
            else:
                logger.warning("No geometries found")


class _Geometry(_BaseObject):
    """Baseclass with common methods for all geometry objects.

    Attributes: extrude: boolean --> Specifies whether to connect the feature to
                                     the ground with a line.
                tessellate: boolean -->  Specifies whether to allow the LineString
                                         to follow the terrain.
                altitudeMode: --> Specifies how altitude components in the <coordinates>
                                  element are interpreted.

    """

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: Optional[AnyGeometryType] = None,
    ) -> None:
        """

        Args:
            ns: Namespace of the object
            id: Id of the object
            target_id: Target id of the object
            extrude: Specifies whether to connect the feature to the ground with a line.
            tessellate: Specifies whether to allow the LineString to follow the terrain.
            altitude_mode: Specifies how altitude components in the <coordinates>
                           element are interpreted.
        """
        super().__init__(ns=ns, id=id, target_id=target_id)
        self._extrude = extrude
        self._tessellate = tessellate
        self._altitude_mode = altitude_mode
        self.geometry = geometry

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode!r} "
            f"geometry={self.geometry!r}"
            f")"
        )

    @property
    def extrude(self) -> Optional[bool]:
        return self._extrude

    @extrude.setter
    def extrude(self, extrude: bool) -> None:
        self._extrude = extrude

    @property
    def tessellate(self) -> Optional[bool]:
        return self._tessellate

    @tessellate.setter
    def tessellate(self, tessellate: bool) -> None:
        self._tessellate = tessellate

    @property
    def altitude_mode(self) -> Optional[AltitudeMode]:
        return self._altitude_mode

    @altitude_mode.setter
    def altitude_mode(self, altitude_mode: Optional[AltitudeMode]) -> None:
        self._altitude_mode = altitude_mode

    def _etree_coordinates(
        self,
        coordinates: Sequence[PointType],
    ) -> Element:
        element = cast(
            Element,
            config.etree.Element(f"{self.ns}coordinates"),  # type: ignore[attr-defined]
        )
        if len(coordinates[0]) == 2:
            tuples = (f"{c[0]:f},{c[1]:f}" for c in coordinates)
        elif len(coordinates[0]) == 3:
            tuples = (
                f"{c[0]:f},{c[1]:f},{c[2]:f}" for c in coordinates  # type: ignore[misc]
            )
        else:
            raise KMLWriteError(f"Invalid dimensions in coordinates '{coordinates}'")
        element.text = " ".join(tuples)
        return element

    def _set_altitude_mode(self, element: Element) -> None:
        if self.altitude_mode:
            am_element = config.etree.SubElement(  # type: ignore[attr-defined]
                element, f"{self.ns}altitudeMode"
            )
            am_element.text = self.altitude_mode.value

    def _set_extrude(self, element: Element) -> None:
        if self.extrude is not None:
            et_element = cast(
                Element,
                config.etree.SubElement(  # type: ignore[attr-defined]
                    element, f"{self.ns}extrude"
                ),
            )
            et_element.text = str(int(self.extrude))

    def _set_tessellate(self, element: Element) -> None:
        if self.tessellate is not None:
            t_element = cast(
                Element,
                config.etree.SubElement(  # type: ignore[attr-defined]
                    element, f"{self.ns}tessellate"
                ),
            )
            t_element.text = str(int(self.tessellate))

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        self.__name__ = self.__class__.__name__
        element = super().etree_element(precision=precision, verbosity=verbosity)
        self._set_extrude(element)
        self._set_altitude_mode(element)
        self._set_tessellate(element)
        return element

    @classmethod
    def _get_coordinates(
        cls, *, ns: str, element: Element, strict: bool
    ) -> List[PointType]:
        """
        Get coordinates from element.

        Coordinates can be any number of tuples separated by a space (potentially any
        number of whitespace characters).
        Values in tuples should be separated by commas with no spaces.

        https://developers.google.com/kml/documentation/kmlreference#coordinates
        """
        coordinates = element.find(f"{ns}coordinates")
        if coordinates is not None:
            # Clean up badly formatted tuples by stripping
            # space following commas.
            try:
                latlons = re.sub(r", +", ",", coordinates.text.strip()).split()
            except AttributeError:
                return []
            return [
                cast(PointType, tuple(float(c) for c in latlon.split(",")))
                for latlon in latlons
            ]
        return []

    @classmethod
    def _get_extrude(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> Optional[bool]:
        extrude = element.find(f"{ns}extrude")
        if extrude is None:
            return None
        with contextlib.suppress(ValueError, AttributeError):
            return bool(int(extrude.text.strip()))
        return None

    @classmethod
    def _get_tessellate(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> Optional[bool]:
        tessellate = element.find(f"{ns}tessellate")
        if tessellate is None:
            return None
        with contextlib.suppress(ValueError):
            return bool(int(tessellate.text.strip()))
        return None

    @classmethod
    def _get_altitude_mode(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> Optional[AltitudeMode]:
        altitude_mode = element.find(f"{ns}altitudeMode")
        if altitude_mode is None:
            return None
        with contextlib.suppress(ValueError):
            return AltitudeMode(altitude_mode.text.strip())
        return None

    @classmethod
    def _get_geometry_kwargs(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        return {
            "extrude": cls._get_extrude(ns=ns, element=element, strict=strict),
            "tessellate": cls._get_tessellate(ns=ns, element=element, strict=strict),
            "altitude_mode": cls._get_altitude_mode(
                ns=ns, element=element, strict=strict
            ),
        }

    @classmethod
    def _get_geometry(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> Optional[AnyGeometryType]:
        return None

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(ns=ns, element=element, strict=strict)
        kwargs.update(cls._get_geometry_kwargs(ns=ns, element=element, strict=strict))
        kwargs.update(
            {"geometry": cls._get_geometry(ns=ns, element=element, strict=strict)}
        )
        return kwargs


class Point(_Geometry):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: geo.Point,
    ) -> None:
        super().__init__(
            ns=ns,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        self.__name__ = self.__class__.__name__
        element = super().etree_element(precision=precision, verbosity=verbosity)
        assert isinstance(self.geometry, geo.Point)
        coords = self.geometry.coords
        element.append(self._etree_coordinates(coords))
        return element

    @classmethod
    def _get_geometry(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> geo.Point:
        coords = cls._get_coordinates(ns=ns, element=element, strict=strict)
        try:
            return geo.Point.from_coordinates(coords)
        except (IndexError, TypeError) as e:
            error = config.etree.tostring(  # type: ignore[attr-defined]
                element,
                encoding="UTF-8",
            ).decode("UTF-8")
            raise KMLParseError(f"Invalid coordinates in {error}") from e


class LineString(_Geometry):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: geo.LineString,
    ) -> None:
        super().__init__(
            ns=ns,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        self.__name__ = self.__class__.__name__
        element = super().etree_element(precision=precision, verbosity=verbosity)
        assert isinstance(self.geometry, geo.LineString)
        coords = self.geometry.coords
        element.append(self._etree_coordinates(coords))
        return element

    @classmethod
    def _get_geometry(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> geo.LineString:
        coords = cls._get_coordinates(ns=ns, element=element, strict=strict)
        try:
            return geo.LineString.from_coordinates(coords)
        except (IndexError, TypeError) as e:
            error = config.etree.tostring(  # type: ignore[attr-defined]
                element,
                encoding="UTF-8",
            ).decode("UTF-8")
            raise KMLParseError(f"Invalid coordinates in {error}") from e


class LinearRing(LineString):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: geo.LinearRing,
    ) -> None:
        super().__init__(
            ns=ns,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

    @classmethod
    def _get_geometry(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> geo.LinearRing:
        coords = cls._get_coordinates(ns=ns, element=element, strict=strict)
        try:
            return cast(geo.LinearRing, geo.LinearRing.from_coordinates(coords))
        except (IndexError, TypeError) as e:
            error = config.etree.tostring(  # type: ignore[attr-defined]
                element,
                encoding="UTF-8",
            ).decode("UTF-8")
            raise KMLParseError(f"Invalid coordinates in {error}") from e


class Polygon(_Geometry):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: geo.Polygon,
    ) -> None:
        super().__init__(
            ns=ns,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        self.__name__ = self.__class__.__name__
        element = super().etree_element(precision=precision, verbosity=verbosity)
        assert isinstance(self.geometry, geo.Polygon)
        linear_ring = partial(LinearRing, ns=self.ns, extrude=None, tessellate=None)
        outer_boundary = cast(
            Element,
            config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}outerBoundaryIs",
            ),
        )
        outer_boundary.append(
            linear_ring(geometry=self.geometry.exterior).etree_element(
                precision=precision, verbosity=verbosity
            )
        )
        for interior in self.geometry.interiors:
            inner_boundary = cast(
                Element,
                config.etree.SubElement(  # type: ignore[attr-defined]
                    element,
                    f"{self.ns}innerBoundaryIs",
                ),
            )
            inner_boundary.append(
                linear_ring(geometry=interior).etree_element(
                    precision=precision, verbosity=verbosity
                )
            )
        return element

    @classmethod
    def _get_geometry(cls, *, ns: str, element: Element, strict: bool) -> geo.Polygon:
        outer_boundary = element.find(f"{ns}outerBoundaryIs")
        if outer_boundary is None:
            error = config.etree.tostring(  # type: ignore[attr-defined]
                element,
                encoding="UTF-8",
            ).decode("UTF-8")
            raise KMLParseError(f"Missing outerBoundaryIs in {error}")
        outer_ring = outer_boundary.find(f"{ns}LinearRing")
        if outer_ring is None:
            error = config.etree.tostring(  # type: ignore[attr-defined]
                element,
                encoding="UTF-8",
            ).decode("UTF-8")
            raise KMLParseError(f"Missing LinearRing in {error}")
        exterior = LinearRing._get_geometry(ns=ns, element=outer_ring, strict=strict)
        interiors = []
        for inner_boundary in element.findall(f"{ns}innerBoundaryIs"):
            inner_ring = inner_boundary.find(f"{ns}LinearRing")
            if inner_ring is None:
                error = config.etree.tostring(  # type: ignore[attr-defined]
                    element,
                    encoding="UTF-8",
                ).decode("UTF-8")
                raise KMLParseError(f"Missing LinearRing in {error}")
            interiors.append(
                LinearRing._get_geometry(ns=ns, element=inner_ring, strict=strict)
            )
        return geo.Polygon.from_linear_rings(exterior, *interiors)


def create_multigeometry(
    geometries: Sequence[AnyGeometryType],
) -> Optional[MultiGeometryType]:
    """Create a MultiGeometry from a sequence of geometries.

    Args:
        geometries: Sequence of geometries.

    Returns:
        MultiGeometry

    """
    geom_types = {geom.geom_type for geom in geometries}
    if not geom_types:
        return None
    if len(geom_types) == 1:
        geom_type = geom_types.pop()
        map_to_geometries = {
            geo.Point.__name__: geo.MultiPoint.from_points,
            geo.LineString.__name__: geo.MultiLineString.from_linestrings,
            geo.Polygon.__name__: geo.MultiPolygon.from_polygons,
        }
        for geometry_name, constructor in map_to_geometries.items():
            if geom_type == geometry_name:
                return constructor(  # type: ignore[operator, no-any-return]
                    *geometries,
                )

    return geo.GeometryCollection(geometries)


class MultiGeometry(_Geometry):
    map_to_kml = {
        geo.Point: Point,
        geo.LineString: LineString,
        geo.Polygon: Polygon,
        geo.LinearRing: LinearRing,
    }
    multi_geometries = (
        geo.MultiPoint,
        geo.MultiLineString,
        geo.MultiPolygon,
        geo.GeometryCollection,
    )

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: MultiGeometryType,
    ) -> None:
        super().__init__(
            ns=ns,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        self.__name__ = self.__class__.__name__
        element = super().etree_element(precision=precision, verbosity=verbosity)
        assert isinstance(self.geometry, geo._MultiGeometry)
        _map_to_kml = {mg: self.__class__ for mg in self.multi_geometries}
        _map_to_kml.update(self.map_to_kml)

        for geometry in self.geometry.geoms:
            geometry_class = _map_to_kml[type(geometry)]
            element.append(
                geometry_class(
                    ns=self.ns,
                    extrude=None,
                    tessellate=None,
                    altitude_mode=None,
                    geometry=geometry,  # type: ignore[arg-type]
                ).etree_element(precision=precision, verbosity=verbosity)
            )
        return element

    @classmethod
    def _get_geometry(
        cls, *, ns: str, element: Element, strict: bool
    ) -> Optional[MultiGeometryType]:
        geometries = []
        allowed_geometries = (cls,) + tuple(cls.map_to_kml.values())
        for g in allowed_geometries:
            for e in element.findall(f"{ns}{g.__name__}"):
                geometry = g._get_geometry(ns=ns, element=e, strict=strict)
                if geometry is not None:
                    geometries.append(geometry)
        return create_multigeometry(geometries)
