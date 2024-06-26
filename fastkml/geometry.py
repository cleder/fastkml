# Copyright (C) 2012 - 2024 Christian Ledermann
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

import logging
import re
from typing import Any
from typing import Dict
from typing import Final
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union
from typing import cast

import pygeoif.geometry as geo
from pygeoif.exceptions import DimensionError
from pygeoif.factories import shape
from pygeoif.types import GeoCollectionType
from pygeoif.types import GeoType
from pygeoif.types import LineType
from typing_extensions import Self

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity
from fastkml.exceptions import GeometryError
from fastkml.exceptions import KMLParseError
from fastkml.exceptions import KMLWriteError
from fastkml.helpers import bool_subelement
from fastkml.helpers import enum_subelement
from fastkml.helpers import subelement_bool_kwarg
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.kml_base import _BaseObject
from fastkml.registry import RegistryItem
from fastkml.registry import known_types
from fastkml.registry import registry
from fastkml.types import Element

__all__ = [
    "AnyGeometryType",
    "Coordinates",
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

MsgMutualExclusive: Final = "Geometry and kml coordinates are mutually exclusive"


def handle_invalid_geometry_error(
    *,
    error: Exception,
    element: Element,
    strict: bool,
) -> None:
    error_in_xml = config.etree.tostring(
        element,
        encoding="UTF-8",
    ).decode(
        "UTF-8",
    )
    msg = f"Invalid coordinates in '{error_in_xml}' caused by '{error}'"
    logger.error(msg)
    if strict:
        raise KMLParseError(msg) from error


def coordinates_subelement(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj (_XMLObject): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the subelement to create.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.

    Returns:
    -------
        None

    """
    if getattr(obj, attr_name, None):
        p = precision if precision is not None else 6
        coords = getattr(obj, attr_name)
        if len(coords[0]) == 2:
            tuples = (f"{c[0]:.{p}f},{c[1]:.{p}f}" for c in coords)
        elif len(coords[0]) == 3:
            tuples = (f"{c[0]:.{p}f},{c[1]:.{p}f},{c[2]:.{p}f}" for c in coords)
        else:
            msg = f"Invalid dimensions in coordinates '{coords}'"
            raise KMLWriteError(msg)
        element.text = " ".join(tuples)


def subelement_coordinates_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, LineType]:
    """
    Extracts coordinates from a subelement and returns them as a dictionary.

    Args:
    ----
        element (Element): The XML element containing the coordinates.
        ns (str): The namespace of the XML element.
        name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to URIs.
        node_name (str): The name of the XML node containing the coordinates.
        kwarg (str): The name of the keyword argument to store the coordinates.
        classes (Tuple[known_types, ...]): A tuple of known types for validation.
        strict (bool): A flag indicating whether to raise an error for invalid geometry.

    Returns:
    -------
        Dict[str, LineType]: A dictionary containing the extracted coordinates.

    Raises:
    ------
        ValueError: If the coordinates are not in the expected format.

    """
    try:
        latlons = re.sub(r", +", ",", element.text.strip()).split()
    except AttributeError:
        return {}
    try:
        return {
            kwarg: [  # type: ignore[dict-item]
                tuple(float(c) for c in latlon.split(",")) for latlon in latlons
            ],
        }
    except ValueError as error:
        handle_invalid_geometry_error(
            error=error,
            element=element,
            strict=strict,
        )
        return {}


class Coordinates(_XMLObject):
    """
    Represents a set of coordinates in decimal degrees.

    Attributes
    ----------
        coords (LineType): A list of tuples representing the coordinates.
            Each coord consists of floating point values for
            longitude, latitude, and altitude.
            The altitude component is optional.
            Coordinates are expressed in decimal degrees only.

    """

    _default_ns = config.KMLNS
    coords: LineType

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        coords: Optional[LineType] = None,
        **kwargs: Any,
    ):
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.coords = coords or []

    def __repr__(self) -> str:
        """Create a string (c)representation for Coordinates."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"coords={self.coords!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.coords)

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return cls.__name__.lower()


registry.register(
    Coordinates,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(LineType,),  # type: ignore[arg-type]
        attr_name="coords",
        node_name="coordinates",
        get_kwarg=subelement_coordinates_kwarg,
        set_element=coordinates_subelement,
    ),
)


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

    extrude: Optional[bool]
    tessellate: Optional[bool]
    altitude_mode: Optional[AltitudeMode]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = None,
        tessellate: Optional[bool] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        **kwargs: Any,
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
        super().__init__(
            ns=ns,
            id=id,
            name_spaces=name_spaces,
            target_id=target_id,
            **kwargs,
        )
        self.extrude = extrude
        self.tessellate = tessellate
        self.altitude_mode = altitude_mode

    def __repr__(self) -> str:
        """Create a string (c)representation for _Geometry."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )


registry.register(
    _Geometry,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(bool,),
        attr_name="extrude",
        node_name="extrude",
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)
registry.register(
    _Geometry,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(bool,),
        attr_name="tessellate",
        node_name="tessellate",
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)
registry.register(
    _Geometry,
    item=RegistryItem(
        ns_ids=("kml", "gx"),
        classes=(AltitudeMode,),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)


class Point(_Geometry):
    """
    A geographic location defined by longitude, latitude, and (optional) altitude.

    When a Point is contained by a Placemark, the point itself determines the position
    of the Placemark's name and icon.
    When a Point is extruded, it is connected to the ground with a line.
    This "tether" uses the current LineStyle.

    https://developers.google.com/kml/documentation/kmlreference#point
    """

    kml_coordinates: Optional[Coordinates]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = None,
        tessellate: Optional[bool] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: Optional[geo.Point] = None,
        kml_coordinates: Optional[Coordinates] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a Point object.

        Args:
        ----
            ns (Optional[str]): The namespace for the element.
            name_spaces (Optional[Dict[str, str]]): The namespace dictionary for the
            element.
            id (Optional[str]): The ID of the element.
            target_id (Optional[str]): The target ID of the element.
            extrude (Optional[bool]): Whether to extrude the geometry.
            tessellate (Optional[bool]): Whether to tessellate the geometry.
            altitude_mode (Optional[AltitudeMode]): The altitude mode of the geometry.
            geometry (Optional[geo.Point]): The geometry object.
            kml_coordinates (Optional[Coordinates]): The KML coordinates of the point.
            **kwargs (Any): Additional keyword arguments.

        Raises:
        ------
            GeometryError: If both `geometry` and `kml_coordinates` are provided.

        """
        if geometry is not None and kml_coordinates is not None:
            raise GeometryError(MsgMutualExclusive)
        if kml_coordinates is None:
            kml_coordinates = (
                Coordinates(coords=geometry.coords)  # type: ignore[arg-type]
                if geometry
                else None
            )
        self.kml_coordinates = kml_coordinates
        super().__init__(
            ns=ns,
            id=id,
            name_spaces=name_spaces,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            **kwargs,
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the Point object.

        Returns
        -------
            str: The string representation of the Point object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"kml_coordinates={self.kml_coordinates!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the Point object has a valid geometry.

        Returns
        -------
            bool: True if the Point object has a valid geometry, False otherwise.

        """
        return bool(self.geometry)

    @property
    def geometry(self) -> Optional[geo.Point]:
        """
        Get the geometry object of the Point.

        Returns
        -------
            Optional[geo.Point]: The geometry object of the Point,
            or None if it doesn't exist.

        """
        if not self.kml_coordinates:
            return None
        try:
            return geo.Point.from_coordinates(self.kml_coordinates.coords)
        except (DimensionError, TypeError):
            return None


registry.register(
    Point,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(Coordinates,),
        attr_name="kml_coordinates",
        node_name="coordinates",
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


class LineString(_Geometry):
    """
    Defines a connected set of line segments.

    Use <LineStyle> to specify the color, color mode, and width of the line.
    When a LineString is extruded, the line is extended to the ground, forming a polygon
    that looks somewhat like a wall or fence.
    For extruded LineStrings, the line itself uses the current LineStyle, and the
    extrusion uses the current PolyStyle.
    See the KML Tutorial for examples of LineStrings (or paths).

    https://developers.google.com/kml/documentation/kmlreference#linestring
    """

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = None,
        tessellate: Optional[bool] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: Optional[geo.LineString] = None,
        kml_coordinates: Optional[Coordinates] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a LineString object.

        Args:
        ----
            ns (Optional[str]): The namespace of the element.
            name_spaces (Optional[Dict[str, str]]): The namespaces used in the element.
            id (Optional[str]): The ID of the element.
            target_id (Optional[str]): The target ID of the element.
            extrude (Optional[bool]): Whether to extrude the geometry.
            tessellate (Optional[bool]): Whether to tessellate the geometry.
            altitude_mode (Optional[AltitudeMode]): The altitude mode of the geometry.
            geometry (Optional[geo.LineString]): The LineString geometry.
            kml_coordinates (Optional[Coordinates]): The KML coordinates of the geometry.
            **kwargs (Any): Additional keyword arguments.

        Raises:
        ------
            ValueError: If both `geometry` and `kml_coordinates` are provided.

        """
        if geometry is not None and kml_coordinates is not None:
            raise GeometryError(MsgMutualExclusive)
        if kml_coordinates is None:
            kml_coordinates = Coordinates(coords=geometry.coords) if geometry else None
        self.kml_coordinates = kml_coordinates
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            **kwargs,
        )

    def __repr__(self) -> str:
        """Create a string (c)representation for LineString."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"geometry={self.geometry!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the LineString object is non-empty.

        Returns
        -------
            bool: True if the LineString object is non-empty, False otherwise.

        """
        return bool(self.geometry)

    @property
    def geometry(self) -> Optional[geo.LineString]:
        """
        Get the LineString geometry.

        Returns
        -------
            Optional[geo.LineString]: The LineString geometry, or None if it doesn't
            exist.

        """
        if not self.kml_coordinates:
            return None
        try:
            return geo.LineString.from_coordinates(self.kml_coordinates.coords)
        except DimensionError:
            return None


registry.register(
    LineString,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(Coordinates,),
        attr_name="kml_coordinates",
        node_name="coordinates",
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


class LinearRing(LineString):
    """
    Defines a closed line string, typically the outer boundary of a Polygon.

    Optionally, a LinearRing can also be used as the inner boundary of a Polygon to
    create holes in the Polygon.
    A Polygon can contain multiple <LinearRing> elements used as inner boundaries.

    https://developers.google.com/kml/documentation/kmlreference#linearring
    """

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = None,
        tessellate: Optional[bool] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: Optional[geo.LinearRing] = None,
        kml_coordinates: Optional[Coordinates] = None,
        **kwargs: Any,
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
            kml_coordinates=kml_coordinates,
            **kwargs,
        )

    def __repr__(self) -> str:
        """Create a string (c)representation for LinearRing."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"geometry={self.geometry!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[geo.LinearRing]:
        """
        Get the geometry of the LinearRing.

        Returns
        -------
            Optional[geo.LinearRing]: The geometry of the LinearRing,
            or None if kml_coordinates is not set or if there is a DimensionError.

        """
        if not self.kml_coordinates:
            return None
        try:
            return cast(
                geo.LinearRing,
                geo.LinearRing.from_coordinates(self.kml_coordinates.coords),
            )
        except DimensionError:
            return None


class OuterBoundaryIs(_XMLObject):
    """
    Represents the outer boundary of a polygon in KML.

    Attributes
    ----------
        kml_geometry (Optional[LinearRing]): The KML geometry representing the outer
        boundary.

    """

    _default_ns = config.KMLNS
    kml_geometry: Optional[LinearRing]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        geometry: Optional[geo.LinearRing] = None,
        kml_geometry: Optional[LinearRing] = None,
        **kwargs: Any,
    ) -> None:
        if geometry is not None and kml_geometry is not None:
            raise GeometryError(MsgMutualExclusive)
        if kml_geometry is None:
            kml_geometry = (
                LinearRing(ns=ns, name_spaces=name_spaces, geometry=geometry)
                if geometry
                else None
            )
        self.kml_geometry = kml_geometry
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )

    def __bool__(self) -> bool:
        return bool(self.geometry)

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return "outerBoundaryIs"

    @property
    def geometry(self) -> Optional[geo.LinearRing]:
        return self.kml_geometry.geometry if self.kml_geometry else None


registry.register(
    OuterBoundaryIs,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(LinearRing,),
        attr_name="kml_geometry",
        node_name="LinearRing",
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


class InnerBoundaryIs(_XMLObject):
    """Represents the inner boundary of a polygon in KML."""

    _default_ns = config.KMLNS
    kml_geometries: List[LinearRing]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        geometries: Optional[Iterable[geo.LinearRing]] = None,
        kml_geometries: Optional[Iterable[LinearRing]] = None,
        **kwargs: Any,
    ) -> None:
        if geometries is not None and kml_geometries is not None:
            raise GeometryError(MsgMutualExclusive)
        if kml_geometries is None:
            kml_geometries = (
                [
                    LinearRing(ns=ns, name_spaces=name_spaces, geometry=lr)
                    for lr in geometries
                ]
                if geometries
                else None
            )
        self.kml_geometries = list(kml_geometries) if kml_geometries else []
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )

    def __bool__(self) -> bool:
        """
        Returns True if any of the inner boundary geometries exist, False otherwise.
        """
        return any(b.geometry for b in self.kml_geometries)

    @classmethod
    def get_tag_name(cls) -> str:
        """
        Returns the tag name of the element.
        """
        return "innerBoundaryIs"

    @property
    def geometries(self) -> Optional[Iterable[geo.LinearRing]]:
        """
        Returns the list of LinearRing objects representing the inner boundary.
        If no inner boundary geometries exist, returns None.
        """
        if not self.kml_geometries:
            return None
        return [lr.geometry for lr in self.kml_geometries if lr.geometry]


registry.register(
    InnerBoundaryIs,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(LinearRing,),
        attr_name="kml_geometries",
        node_name="LinearRing",
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


class Polygon(_Geometry):
    """
    A Polygon is defined by an outer boundary and 0 or more inner boundaries.

    The boundaries, in turn, are defined by LinearRings.
    When a Polygon is extruded, its boundaries are connected to the ground to form
    additional polygons, which gives the appearance of a building or a box.
    Extruded Polygons use <PolyStyle> for their color, color mode, and fill.

    The <coordinates> for polygons must be specified in counterclockwise order.

    The outer boundary is represented by the `outer_boundary_is` attribute,
    which is an instance of the `OuterBoundaryIs` class.
    The inner boundaries are represented by the `inner_boundary_is` attribute,
    which is an instance of the `InnerBoundaryIs` class.

    The `geometry` property returns a `geo.Polygon` object representing the
    geometry of the Polygon.

    Example usage:
    ```
    polygon = Polygon(outer_boundary_is=outer_boundary, inner_boundary_is=inner_boundary)
    print(polygon.geometry)
    ```

    https://developers.google.com/kml/documentation/kmlreference#polygon
    """

    outer_boundary_is: Optional[OuterBoundaryIs]
    inner_boundary_is: Optional[InnerBoundaryIs]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = None,
        tessellate: Optional[bool] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        outer_boundary_is: Optional[OuterBoundaryIs] = None,
        inner_boundary_is: Optional[InnerBoundaryIs] = None,
        geometry: Optional[geo.Polygon] = None,
        **kwargs: Any,
    ) -> None:
        if outer_boundary_is is not None and geometry is not None:
            raise GeometryError(MsgMutualExclusive)
        if geometry is not None:
            outer_boundary_is = OuterBoundaryIs(geometry=geometry.exterior)
            inner_boundary_is = InnerBoundaryIs(geometries=geometry.interiors)
        self.outer_boundary_is = outer_boundary_is
        self.inner_boundary_is = inner_boundary_is
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            **kwargs,
        )

    def __bool__(self) -> bool:
        return bool(self.outer_boundary_is)

    @property
    def geometry(self) -> Optional[geo.Polygon]:
        if not self.outer_boundary_is:
            return None
        if not self.inner_boundary_is:
            return geo.Polygon.from_linear_rings(
                cast(geo.LinearRing, self.outer_boundary_is.geometry),
            )
        return geo.Polygon.from_linear_rings(  # type: ignore[misc]
            cast(geo.LinearRing, self.outer_boundary_is.geometry),
            *self.inner_boundary_is.geometries,
        )

    def __repr__(self) -> str:
        """Create a string (c)representation for Polygon."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"geometry={self.geometry!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )


registry.register(
    Polygon,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(OuterBoundaryIs,),
        attr_name="outer_boundary_is",
        node_name="outerBoundaryIs",
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Polygon,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(InnerBoundaryIs,),
        attr_name="inner_boundary_is",
        node_name="innerBoundaryIs",
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


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
                return constructor(  # type: ignore[operator, no-any-return]
                    *geometries,
                )

    return geo.GeometryCollection(geometries)


def create_kml_geometry(
    geometry: Union[GeoType, GeoCollectionType],
    *,
    ns: Optional[str] = None,
    name_spaces: Optional[Dict[str, str]] = None,
    id: Optional[str] = None,
    target_id: Optional[str] = None,
    extrude: Optional[bool] = None,
    tessellate: Optional[bool] = None,
    altitude_mode: Optional[AltitudeMode] = None,
) -> _Geometry:
    """
    Create a KML geometry from a geometry object.

    Args:
    ----
        geometry: Geometry object.
        ns: Namespace of the object
        id: Id of the object
        target_id: Target id of the object
        extrude: Specifies whether to connect the feature to the ground with a line.
        tessellate: Specifies whether to allow the LineString to follow the terrain.
        altitude_mode: Specifies how altitude components in the <coordinates>
                       element are interpreted.

    Returns:
    -------
        KML geometry object.

    """
    _map_to_kml = {
        geo.Point: Point,
        geo.Polygon: Polygon,
        geo.LinearRing: LinearRing,
        geo.LineString: LineString,
        geo.MultiPoint: MultiGeometry,
        geo.MultiLineString: MultiGeometry,
        geo.MultiPolygon: MultiGeometry,
        geo.GeometryCollection: MultiGeometry,
    }
    geom = shape(geometry)
    for geometry_class, kml_class in _map_to_kml.items():
        if isinstance(geom, geometry_class):
            return cast(
                _Geometry,
                kml_class(
                    ns=ns,
                    name_spaces=name_spaces,
                    id=id,
                    target_id=target_id,
                    extrude=extrude,
                    tessellate=tessellate,
                    altitude_mode=altitude_mode,
                    geometry=geom,
                ),
            )
    # this should be unreachable, but mypy doesn't know that
    msg = f"Unsupported geometry type {type(geometry)}"  # pragma: no cover
    raise KMLWriteError(msg)  # pragma: no cover


class MultiGeometry(_Geometry):
    """
    A container for zero or more geometry primitives associated with the same feature.
    """

    kml_geometries: List[Union[Point, LineString, Polygon, LinearRing, Self]]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = None,
        tessellate: Optional[bool] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        kml_geometries: Optional[
            Iterable[Union[Point, LineString, Polygon, LinearRing, Self]]
        ] = None,
        geometry: Optional[MultiGeometryType] = None,
        **kwargs: Any,
    ) -> None:
        if kml_geometries is not None and geometry is not None:
            raise GeometryError(MsgMutualExclusive)
        if geometry is not None:
            kml_geometries = [
                create_kml_geometry(  # type: ignore[misc]
                    geometry=geom,
                    ns=ns,
                    name_spaces=name_spaces,
                    extrude=extrude,
                    tessellate=tessellate,
                    altitude_mode=altitude_mode,
                )
                for geom in geometry.geoms
            ]
        self.kml_geometries = list(kml_geometries) if kml_geometries else []
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            **kwargs,
        )

    def __bool__(self) -> bool:
        """
        Returns True if the MultiGeometry has a geometry, False otherwise.
        """
        return bool(self.geometry)

    def __repr__(self) -> str:
        """
        Returns a string representation of the MultiGeometry.
        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"geometry={self.geometry!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[MultiGeometryType]:
        """
        Returns the geometry of the MultiGeometry.
        """
        return create_multigeometry(
            [geom.geometry for geom in self.kml_geometries if geom.geometry],
        )


registry.register(
    MultiGeometry,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(Point, LineString, Polygon, LinearRing, MultiGeometry),
        attr_name="kml_geometries",
        node_name="(Point|LineString|Polygon|LinearRing|MultiGeometry)",
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)
