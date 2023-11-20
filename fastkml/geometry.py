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

import pygeoif.geometry as geo
from pygeoif.types import PointType

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity
from fastkml.exceptions import KMLParseError
from fastkml.exceptions import KMLWriteError
from fastkml.types import Element

__all__ = [
    "AnyGeometryType",
    "GeometryType",
    "LineString",
    "LinearRing",
    "MultiGeometry",
    "MultiGeometryType",
    "Point",
    "Polygon",
    "create_multigeometry",
]

logger = logging.getLogger(__name__)

GeometryType = Union[geo.Polygon, geo.LineString, geo.LinearRing, geo.Point]
MultiGeometryType = Union[
    geo.MultiPoint,
    geo.MultiLineString,
    geo.MultiPolygon,
    geo.GeometryCollection,
]
AnyGeometryType = Union[GeometryType, MultiGeometryType]


class _Geometry(_BaseObject):
    """
    Baseclass with common methods for all geometry objects.

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
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: Optional[AnyGeometryType] = None,
    ) -> None:
        """

        Args:
        ----
            ns: Namespace of the object
            id: Id of the object
            target_id: Target id of the object
            extrude: Specifies whether to connect the feature to the ground with a line.
            tessellate: Specifies whether to allow the LineString to follow the terrain.
            altitude_mode: Specifies how altitude components in the <coordinates>
                           element are interpreted.
        """
        super().__init__(ns=ns, id=id, name_spaces=name_spaces, target_id=target_id)
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
            f"altitude_mode={self.altitude_mode} "
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
        if not coordinates:
            return element
        if len(coordinates[0]) == 2:
            tuples = (f"{c[0]:f},{c[1]:f}" for c in coordinates)
        elif len(coordinates[0]) == 3:
            tuples = (f"{c[0]:f},{c[1]:f},{c[2]:f}" for c in coordinates)
        else:
            msg = f"Invalid dimensions in coordinates '{coordinates}'"
            raise KMLWriteError(msg)
        element.text = " ".join(tuples)
        return element

    def _set_altitude_mode(self, element: Element) -> None:
        if self.altitude_mode:
            am_element = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}altitudeMode",
            )
            am_element.text = self.altitude_mode.value

    def _set_extrude(self, element: Element) -> None:
        if self.extrude is not None:
            et_element = cast(
                Element,
                config.etree.SubElement(  # type: ignore[attr-defined]
                    element,
                    f"{self.ns}extrude",
                ),
            )
            et_element.text = str(int(self.extrude))

    def _set_tessellate(self, element: Element) -> None:
        if self.tessellate is not None:
            t_element = cast(
                Element,
                config.etree.SubElement(  # type: ignore[attr-defined]
                    element,
                    f"{self.ns}tessellate",
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
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
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
                ns=ns,
                element=element,
                strict=strict,
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
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs.update(cls._get_geometry_kwargs(ns=ns, element=element, strict=strict))
        kwargs.update(
            {"geometry": cls._get_geometry(ns=ns, element=element, strict=strict)},
        )
        return kwargs


class Point(_Geometry):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
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
            name_spaces=name_spaces,
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
            ).decode(
                "UTF-8",
            )
            msg = f"Invalid coordinates in {error}"
            raise KMLParseError(msg) from e


class LineString(_Geometry):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: geo.LineString,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
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
            ).decode(
                "UTF-8",
            )
            msg = f"Invalid coordinates in {error}"
            raise KMLParseError(msg) from e


class LinearRing(LineString):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: geo.LinearRing,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
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
            ).decode(
                "UTF-8",
            )
            msg = f"Invalid coordinates in {error}"
            raise KMLParseError(msg) from e


class Polygon(_Geometry):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: geo.Polygon,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
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
                precision=precision,
                verbosity=verbosity,
            ),
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
                    precision=precision,
                    verbosity=verbosity,
                ),
            )
        return element

    @classmethod
    def _get_geometry(cls, *, ns: str, element: Element, strict: bool) -> geo.Polygon:
        outer_boundary = element.find(f"{ns}outerBoundaryIs")
        if outer_boundary is None:
            error = config.etree.tostring(  # type: ignore[attr-defined]
                element,
                encoding="UTF-8",
            ).decode(
                "UTF-8",
            )
            msg = f"Missing outerBoundaryIs in {error}"
            raise KMLParseError(msg)
        outer_ring = outer_boundary.find(f"{ns}LinearRing")
        if outer_ring is None:
            error = config.etree.tostring(  # type: ignore[attr-defined]
                element,
                encoding="UTF-8",
            ).decode(
                "UTF-8",
            )
            msg = f"Missing LinearRing in {error}"
            raise KMLParseError(msg)
        exterior = LinearRing._get_geometry(ns=ns, element=outer_ring, strict=strict)
        interiors = []
        for inner_boundary in element.findall(f"{ns}innerBoundaryIs"):
            inner_ring = inner_boundary.find(f"{ns}LinearRing")
            if inner_ring is None:
                error = config.etree.tostring(  # type: ignore[attr-defined]
                    element,
                    encoding="UTF-8",
                ).decode(
                    "UTF-8",
                )
                msg = f"Missing LinearRing in {error}"
                raise KMLParseError(msg)
            interiors.append(
                LinearRing._get_geometry(ns=ns, element=inner_ring, strict=strict),
            )
        return geo.Polygon.from_linear_rings(exterior, *interiors)


def create_multigeometry(
    geometries: Sequence[AnyGeometryType],
) -> Optional[MultiGeometryType]:
    """
    Create a MultiGeometry from a sequence of geometries.

    Args:
    ----
        geometries: Sequence of geometries.

    Returns:
    -------
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
                return constructor(
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
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: MultiGeometryType,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
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
        _map_to_kml = {mg: self.__class__ for mg in self.multi_geometries}
        _map_to_kml.update(self.map_to_kml)
        if self.geometry is None:
            return element
        assert isinstance(self.geometry, self.multi_geometries)
        for geometry in self.geometry.geoms:
            geometry_class = _map_to_kml[type(geometry)]
            element.append(
                geometry_class(
                    ns=self.ns,
                    extrude=None,
                    tessellate=None,
                    altitude_mode=None,
                    geometry=geometry,
                ).etree_element(precision=precision, verbosity=verbosity),
            )
        return element

    @classmethod
    def _get_geometry(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> Optional[MultiGeometryType]:
        geometries = []
        allowed_geometries = (cls, *tuple(cls.map_to_kml.values()))
        for g in allowed_geometries:
            for e in element.findall(f"{ns}{g.__name__}"):
                geometry = g._get_geometry(  # type: ignore[attr-defined]
                    ns=ns,
                    element=e,
                    strict=strict,
                )
                if geometry is not None:
                    geometries.append(geometry)
        return create_multigeometry(geometries)
