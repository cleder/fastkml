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
"""
Classes and functions for working with geometries in KML files.

The classes in this module represent different types of geometries, such as points,
lines, polygons, and multi-geometries.
These geometries can be used to define the shape and location of features in KML files.

The module also provides functions for handling coordinates and extracting them from XML
elements.

"""

import logging
import re
from typing import Any
from typing import Dict
from typing import Final
from typing import Iterable
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
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
from fastkml.registry import registry
from fastkml.types import Element

__all__ = [
    "Coordinates",
    "InnerBoundaryIs",
    "LineString",
    "LinearRing",
    "MultiGeometry",
    "OuterBoundaryIs",
    "Point",
    "Polygon",
    "create_kml_geometry",
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

xml_attrs = {"ns", "name_spaces", "id", "target_id"}


def handle_invalid_geometry_error(
    *,
    error: Exception,
    element: Element,
    strict: bool,
) -> None:
    """
    Handle an invalid geometry error.

    Args:
    ----
        error (Exception): The exception that occurred.
        element (Element): The XML element that caused the error.
        strict (bool): Flag indicating whether to raise an exception or not.

    Returns:
    -------
        None

    Raises:
    ------
        KMLParseError: If `strict` is True, raise a KMLParseError.

    """
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
    node_name: str,  # noqa: ARG001
    precision: Optional[int],
    verbosity: Optional[Verbosity],  # noqa: ARG001
    default: Any,  # noqa: ARG001
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
        default (Any): The default value of the attribute (unused).

    Returns:
    -------
        None

    """
    if getattr(obj, attr_name, None):
        coords = getattr(obj, attr_name)
        if not coords or len(coords[0]) not in (2, 3):
            msg = f"Invalid dimensions in coordinates '{coords}'"
            raise KMLWriteError(msg)
        if precision is None:
            tuples = (",".join(str(c) for c in coord) for coord in coords)
        else:
            tuples = (",".join(f"{c:.{precision}f}" for c in coord) for coord in coords)
        element.text = " ".join(tuples)


def subelement_coordinates_kwarg(
    *,
    element: Element,
    ns: str,  # noqa: ARG001
    name_spaces: Dict[str, str],  # noqa: ARG001
    node_name: str,  # noqa: ARG001
    kwarg: str,
    classes: Tuple[Type[object], ...],  # noqa: ARG001
    strict: bool,
) -> Dict[str, LineType]:
    """
    Extract coordinates from a subelement and returns them as a dictionary.

    Args:
    ----
        element (Element): The XML element containing the coordinates.
        ns (str): The namespace of the XML element.
        name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to URIs.
        node_name (str): The name of the XML node containing the coordinates.
        kwarg (str): The name of the keyword argument to store the coordinates.
        classes (Tuple[Type[object], ...]): A tuple of known types for validation.
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

    _default_nsid = config.KML
    coords: LineType

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        coords: Optional[LineType] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a Geometry object.

        Parameters
        ----------
        ns : str, optional
            The namespace for the element.
        name_spaces : dict, optional
            A dictionary of namespace prefixes and URIs.
        coords : LineType, optional
            The coordinates of the geometry.
        **kwargs : dict
            Additional keyword arguments.

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.coords = coords or []

    def __repr__(self) -> str:
        """Create a string (c)representation for Coordinates."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"coords={self.coords!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the geometry has any coordinates.

        Returns
        -------
        bool
            True if the geometry has coordinates, False otherwise.

        """
        return bool(self.coords)

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return cls.__name__.lower()


registry.register(
    Coordinates,
    item=RegistryItem(
        ns_ids=("kml", ""),
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

    altitude_mode: Optional[AltitudeMode]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a _Geometry object.

        Args:
        ----
            ns: Namespace of the object.
            name_spaces: Name spaces of the object.
            id: Id of the object.
            target_id: Target id of the object.
            extrude: Specifies whether to connect the feature to the ground with a line.
            tessellate: Specifies whether to allow the LineString to follow the terrain.
            altitude_mode: Specifies how altitude components in the <coordinates>
                           element are interpreted.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(
            ns=ns,
            id=id,
            name_spaces=name_spaces,
            target_id=target_id,
            **kwargs,
        )
        self.altitude_mode = altitude_mode


class Point(_Geometry):
    """
    A geographic location defined by longitude, latitude, and (optional) altitude.

    When a Point is contained by a Placemark, the point itself determines the position
    of the Placemark's name and icon.
    When a Point is extruded, it is connected to the ground with a line.
    This "tether" uses the current LineStyle.

    https://developers.google.com/kml/documentation/kmlreference#point
    """

    extrude: Optional[bool]
    kml_coordinates: Optional[Coordinates]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = None,
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
        if kml_coordinates is None and geometry:
            kml_coordinates = (
                Coordinates(coords=geometry.coords)  # type: ignore[arg-type]
                if geometry
                else None
            )
        self.kml_coordinates = kml_coordinates
        self.extrude = extrude
        kwargs.pop("tessellate", None)
        super().__init__(
            ns=ns,
            id=id,
            name_spaces=name_spaces,
            target_id=target_id,
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
            f"altitude_mode={self.altitude_mode}, "
            f"kml_coordinates={self.kml_coordinates!r}, "
            f"**{self._get_splat()!r},"
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

    def __eq__(self, other: object) -> bool:
        """Check if the Point objects are equal."""
        if isinstance(other, Point):
            return all(
                getattr(self, attr) == getattr(other, attr)
                for attr in (
                    "extrude",
                    "altitude_mode",
                    "geometry",
                    *xml_attrs,
                    *self._get_splat(),
                )
            )
        return super().__eq__(other)

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
        ns_ids=("kml", ""),
        classes=(bool,),
        attr_name="extrude",
        node_name="extrude",
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
        default=False,
    ),
)
registry.register(
    Point,
    item=RegistryItem(
        ns_ids=("kml", "gx", ""),
        classes=(AltitudeMode,),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
        default=AltitudeMode.clamp_to_ground,
    ),
)
registry.register(
    Point,
    item=RegistryItem(
        ns_ids=("kml", ""),
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

    extrude: Optional[bool]
    tessellate: Optional[bool]
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
            kml_coordinates (Optional[Coordinates]): The coordinates of the geometry.
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
        self.extrude = extrude
        self.tessellate = tessellate
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
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
            f"**{self._get_splat()!r},"
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

    def __eq__(self, other: object) -> bool:
        """Check if the LineString objects is equal."""
        if isinstance(other, LineString):
            return all(
                getattr(self, attr) == getattr(other, attr)
                for attr in (
                    "extrude",
                    "tessellate",
                    "geometry",
                    *xml_attrs,
                    *self._get_splat(),
                )
            )
        return super().__eq__(other)

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
        ns_ids=("kml", ""),
        classes=(bool,),
        attr_name="extrude",
        node_name="extrude",
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
        default=False,
    ),
)
registry.register(
    LineString,
    item=RegistryItem(
        ns_ids=("kml", ""),
        classes=(bool,),
        attr_name="tessellate",
        node_name="tessellate",
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
        default=False,
    ),
)
registry.register(
    LineString,
    item=RegistryItem(
        ns_ids=("kml", "gx", ""),
        classes=(AltitudeMode,),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
        default=AltitudeMode.clamp_to_ground,
    ),
)
registry.register(
    LineString,
    item=RegistryItem(
        ns_ids=("kml", ""),
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
        """
        Initialize a Geometry object.

        Parameters
        ----------
        ns : str, optional
            The namespace for the element.
        name_spaces : dict[str, str], optional
            A dictionary of namespace prefixes and URIs.
        id : str, optional
            The ID of the element.
        target_id : str, optional
            The target ID of the element.
        extrude : bool, optional
            Whether to extrude the geometry.
        tessellate : bool, optional
            Whether to tessellate the geometry.
        altitude_mode : AltitudeMode, optional
            The altitude mode of the geometry.
        geometry : geo.LinearRing, optional
            The geometry object.
        kml_coordinates : Coordinates, optional
            The KML coordinates.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        None

        """
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


class BoundaryIs(_XMLObject):
    """
    Represents the inner or outer boundary of a polygon in KML.

    Attributes
    ----------
    kml_geometry : Optional[LinearRing]
        The KML geometry representing the outer boundary.

    """

    _default_nsid = config.KML
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
        """
        Initialize a Boundary object.

        Parameters
        ----------
        ns : str, optional
            The namespace for the KML element.
        name_spaces : dict, optional
            A dictionary of namespace prefixes and URIs.
        geometry : fastkml.geometry.LinearRing, optional
            The geometry object.
        kml_geometry : fastkml.geometry.LinearRing, optional
            The KML geometry object.
        **kwargs : Any
            Additional keyword arguments.

        Raises
        ------
        GeometryError
            If both `geometry` and `kml_geometry` are provided.

        Notes
        -----
        If `kml_geometry` is not provided, it will be created based on the `geometry`
        parameter.

        """
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
        """
        Check if the OuterBoundaryIs object is valid.

        Returns
        -------
        bool
            True if the object has a valid geometry, False otherwise.

        """
        return bool(self.geometry)

    def __repr__(self) -> str:
        """Create a string (c)representation for OuterBoundaryIs."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"kml_geometry={self.kml_geometry!r}, "
            f"**{self._get_splat()},"
            ")"
        )

    @property
    def geometry(self) -> Optional[geo.LinearRing]:
        """
        Get the geometry of the OuterBoundaryIs object.

        Returns
        -------
        Optional[geo.LinearRing]
            The geometry object representing the outer boundary.

        """
        return self.kml_geometry.geometry if self.kml_geometry else None


class OuterBoundaryIs(BoundaryIs):
    """Represents the outer boundary of a polygon in KML."""

    @classmethod
    def get_tag_name(cls) -> str:
        """
        Get the tag name for the OuterBoundaryIs object.

        Returns
        -------
        str
            The tag name.

        """
        return "outerBoundaryIs"


class InnerBoundaryIs(BoundaryIs):
    """Represents the inner boundary of a polygon in KML."""

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name of the element."""
        return "innerBoundaryIs"


registry.register(
    BoundaryIs,
    item=RegistryItem(
        ns_ids=("kml", ""),
        classes=(LinearRing,),
        attr_name="kml_geometry",
        node_name="LinearRing",
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
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

    Example usage::

        polygon = Polygon(outer_boundary_is=outer_boundary,
            inner_boundary_is=inner_boundary)
        print(polygon.geometry)


    https://developers.google.com/kml/documentation/kmlreference#polygon
    """

    extrude: Optional[bool]
    tessellate: Optional[bool]
    outer_boundary: Optional[OuterBoundaryIs]
    inner_boundaries: List[InnerBoundaryIs]

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
        outer_boundary: Optional[OuterBoundaryIs] = None,
        inner_boundaries: Optional[Iterable[InnerBoundaryIs]] = None,
        geometry: Optional[geo.Polygon] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a Geometry object.

        Parameters
        ----------
        ns : Optional[str]
            The namespace of the element.
        name_spaces : Optional[Dict[str, str]]
            The dictionary of namespace prefixes and URIs.
        id : Optional[str]
            The ID of the element.
        target_id : Optional[str]
            The target ID of the element.
        extrude : Optional[bool]
            The extrude flag of the element.
        tessellate : Optional[bool]
            The tessellate flag of the element.
        altitude_mode : Optional[AltitudeMode]
            The altitude mode of the element.
        outer_boundary : Optional[OuterBoundaryIs]
            The outer boundary of the element.
        inner_boundaries : Optional[Iterable[InnerBoundaryIs]]
            The inner boundaries of the element.
        geometry : Optional[geo.Polygon]
            The geometry object of the element.
        **kwargs : Any
            Additional keyword arguments.

        Raises
        ------
        GeometryError:
            If both outer_boundary_is and geometry are provided.

        Returns
        -------
        None

        """
        if outer_boundary is not None and geometry is not None:
            raise GeometryError(MsgMutualExclusive)
        if geometry is not None:
            outer_boundary = OuterBoundaryIs(geometry=geometry.exterior)
            inner_boundaries = [
                InnerBoundaryIs(geometry=interior) for interior in geometry.interiors
            ]
        self.outer_boundary = outer_boundary
        self.inner_boundaries = list(inner_boundaries) if inner_boundaries else []
        self.extrude = extrude
        self.tessellate = tessellate
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            altitude_mode=altitude_mode,
            **kwargs,
        )

    def __bool__(self) -> bool:
        """
        Return True if the outer boundary is defined, False otherwise.

        Returns
        -------
        bool
            True if the outer boundary is defined, False otherwise.

        """
        return bool(self.outer_boundary)

    @property
    def geometry(self) -> Optional[geo.Polygon]:
        """
        Get the geometry object representing the geometry of the Polygon.

        Returns
        -------
        Optional[geo.Polygon]
            The geometry object representing the geometry of the Polygon.

        """
        if not self.outer_boundary:
            return None
        if not self.inner_boundaries:
            return geo.Polygon.from_linear_rings(
                cast(geo.LinearRing, self.outer_boundary.geometry),
            )
        return geo.Polygon.from_linear_rings(
            cast(geo.LinearRing, self.outer_boundary.geometry),
            *[
                interior.geometry
                for interior in self.inner_boundaries
                if interior.geometry is not None
            ],
        )

    def __repr__(self) -> str:
        """
        Create a string representation for Polygon.

        Returns
        -------
        str
            The string representation for Polygon.

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
            f"**{self._get_splat()!r},"
            ")"
        )

    def __eq__(self, other: object) -> bool:
        """Check if the Polygon objects are equal."""
        if isinstance(other, Polygon):
            return all(
                getattr(self, attr) == getattr(other, attr)
                for attr in (
                    "extrude",
                    "tessellate",
                    "geometry",
                    *xml_attrs,
                    *self._get_splat(),
                )
            )
        return super().__eq__(other)


registry.register(
    Polygon,
    item=RegistryItem(
        ns_ids=("kml", ""),
        classes=(bool,),
        attr_name="extrude",
        node_name="extrude",
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
        default=False,
    ),
)
registry.register(
    Polygon,
    item=RegistryItem(
        ns_ids=("kml", ""),
        classes=(bool,),
        attr_name="tessellate",
        node_name="tessellate",
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
        default=False,
    ),
)
registry.register(
    Polygon,
    item=RegistryItem(
        ns_ids=("kml", "gx", ""),
        classes=(AltitudeMode,),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
        default=AltitudeMode.clamp_to_ground,
    ),
)
registry.register(
    Polygon,
    item=RegistryItem(
        ns_ids=("kml", ""),
        classes=(OuterBoundaryIs,),
        attr_name="outer_boundary",
        node_name="outerBoundaryIs",
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Polygon,
    item=RegistryItem(
        ns_ids=("kml", ""),
        classes=(InnerBoundaryIs,),
        attr_name="inner_boundaries",
        node_name="innerBoundaryIs",
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
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


class MultiGeometry(_BaseObject):
    """A container for zero or more geometry primitives."""

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
        """
        Initialize a Geometry object.

        Parameters
        ----------
        ns : str, optional
            The namespace for the KML element.
        name_spaces : dict, optional
            A dictionary of namespace prefixes and URIs.
        id : str, optional
            The ID of the KML element.
        target_id : str, optional
            The target ID of the KML element.
        kml_geometries : iterable of Point, LineString, Polygon, LinearRing,
            MultiGeometry
            A collection of KML geometries.
        geometry : MultiGeometryType, optional
            A multi-geometry object.
            Parameters for geometry and kml_geometries are mutually exclusive.
            When geometry is provided, kml_geometries will be created from it and
            you can specify additional parameters like extrude, tessellate, and
            altitude_mode which will be set on the individual geometries.
        extrude : bool, optional
            Specifies whether to extend the geometry to the ground.
            This is not set on the multi-geometry itself, but on the individual
            geometries.
        tessellate : bool, optional
            Specifies whether to allow the geometry to follow the terrain.
            This is not set on the multi-geometry itself, but on the individual
            geometries.
        altitude_mode : AltitudeMode, optional
            The altitude mode of the geometry. This is not set on the multi-geometry
            itself, but on the individual geometries.
        **kwargs : any
            Additional keyword arguments.

        Raises
        ------
        GeometryError
            If both `kml_geometries` and `geometry` are provided.

        Notes
        -----
        - If `geometry` is provided, it will be converted into a collection of KML
            geometries.

        """
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
            **kwargs,
        )

    def __bool__(self) -> bool:
        """Return True if the MultiGeometry has a geometry, False otherwise."""
        return bool(self.geometry)

    def __repr__(self) -> str:
        """Return a string representation of the MultiGeometry."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"kml_geometries={self.kml_geometries!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[MultiGeometryType]:
        """Return the geometry of the MultiGeometry."""
        return create_multigeometry(
            [geom.geometry for geom in self.kml_geometries if geom.geometry],
        )


registry.register(
    MultiGeometry,
    item=RegistryItem(
        ns_ids=("kml", ""),
        classes=(Point, LineString, Polygon, LinearRing, MultiGeometry),
        attr_name="kml_geometries",
        node_name="(Point|LineString|Polygon|LinearRing|MultiGeometry)",
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


KMLGeometryType = Union[Point, LineString, Polygon, LinearRing, MultiGeometry]


def _unknown_geometry_type(geometry: Union[GeoType, GeoCollectionType]) -> NoReturn:
    """
    Raise an error for an unknown geometry type.

    Args:
    ----
        geometry: The geometry object.

    Raises:
    ------
        KMLWriteError: If the geometry type is unknown.

    """
    msg = f"Unsupported geometry type {type(geometry)}"  # pragma: no cover
    raise KMLWriteError(msg)  # pragma: no cover


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
) -> KMLGeometryType:
    """
    Create a KML geometry from a geometry object.

    Args:
    ----
        geometry: Geometry object.
        ns: Namespace of the object
        name_spaces: Name spaces of the object
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
    _map_to_kml: Dict[
        Union[Type[GeoType], Type[GeoCollectionType]],
        Type[KMLGeometryType],
    ] = {
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
            return kml_class(
                ns=ns,
                name_spaces=name_spaces,
                id=id,
                target_id=target_id,
                extrude=extrude,
                tessellate=tessellate,
                altitude_mode=altitude_mode,
                geometry=geom,  # type: ignore[arg-type]
            )

    _unknown_geometry_type(geometry)  # pragma: no cover
