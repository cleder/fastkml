# Copyright (C) 2023  Christian Ledermann
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
"""KML Views."""
import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.enums import AltitudeMode
from fastkml.helpers import enum_subelement
from fastkml.helpers import float_subelement
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.kml_base import _BaseObject
from fastkml.mixins import TimeMixin
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp

logger = logging.getLogger(__name__)


class _AbstractView(TimeMixin, _BaseObject):
    """
    Abstract element that cannot be used directly in a KML file.

    This element is extended by the <Camera> and <LookAt> elements.
    """

    longitude: Optional[float]
    # Longitude of the virtual camera (eye point). Angular distance in degrees,
    # relative to the Prime Meridian. Values west of the Meridian range from
    # -180 to 0 degrees. Values east of the Meridian range from 0 to 180 degrees.

    latitude: Optional[float]
    # Latitude of the virtual camera. Degrees north or south of the Equator
    # (0 degrees). Values range from -90 degrees to 90 degrees.

    altitude: Optional[float]
    # Distance of the camera from the earth's surface, in meters. Interpreted
    # according to the Camera's <altitudeMode> or <gx:altitudeMode>.

    heading: Optional[float]
    # Direction (azimuth) of the camera, in degrees. Default=0 (true North).
    # (See diagram.) Values range from 0 to 360 degrees.

    tilt: Optional[float]
    # Rotation, in degrees, of the camera around the X axis. A value of 0
    # indicates that the view is aimed straight down toward the earth (the
    # most common case). A value for 90 for <tilt> indicates that the view
    # is aimed toward the horizon. Values greater than 90 indicate that the
    # view is pointed up into the sky. Values for <tilt> are clamped at +180
    # degrees.

    altitude_mode: Optional[AltitudeMode]
    # Specifies how the <altitude> specified for the Camera is interpreted.
    # Possible values are as follows:
    #   relativeToGround -
    #       (default) Interprets the <altitude> as a value in meters above the
    #       ground. If the point is over water, the <altitude> will be
    #       interpreted as a value in meters above sea level. See
    #       <gx:altitudeMode> below to specify points relative to the sea floor.
    #   clampToGround -
    #       For a camera, this setting also places the camera relativeToGround,
    #       since putting the camera exactly at terrain height would mean that
    #       the eye would intersect the terrain (and the view would be blocked).
    #   absolute -
    #       Interprets the <altitude> as a value in meters above sea level.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        altitude: Optional[float] = None,
        heading: Optional[float] = None,
        tilt: Optional[float] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        time_primitive: Union[TimeSpan, TimeStamp, None] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new View object.

        Parameters
        ----------
        ns : Optional[str]
            The namespace for the view.
        name_spaces : Optional[Dict[str, str]]
            The dictionary of namespace prefixes and URIs.
        id : Optional[str]
            The ID of the view.
        target_id : Optional[str]
            The ID of the target view.
        longitude : Optional[float]
            The longitude coordinate of the view.
        latitude : Optional[float]
            The latitude coordinate of the view.
        altitude : Optional[float]
            The altitude coordinate of the view.
        heading : Optional[float]
            The heading angle of the view.
        tilt : Optional[float]
            The tilt angle of the view.
        altitude_mode : Optional[AltitudeMode]
            The altitude mode of the view.
        time_primitive : Union[TimeSpan, TimeStamp, None]
            The time primitive associated with the view.
        kwargs : Any
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
            **kwargs,
        )
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.heading = heading
        self.tilt = tilt
        self.altitude_mode = altitude_mode
        self.times = time_primitive

    def __repr__(self) -> str:
        """Create a string (c)representation for _AbstractView."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"longitude={self.longitude!r}, "
            f"latitude={self.latitude!r}, "
            f"altitude={self.altitude!r}, "
            f"heading={self.heading!r}, "
            f"tilt={self.tilt!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"time_primitive={self.times!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    _AbstractView,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="longitude",
        node_name="longitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    _AbstractView,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="latitude",
        node_name="latitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    _AbstractView,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="altitude",
        node_name="altitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    _AbstractView,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="heading",
        node_name="heading",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    _AbstractView,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="tilt",
        node_name="tilt",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    _AbstractView,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        classes=(AltitudeMode,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)
registry.register(
    _AbstractView,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="time_primitive",
        node_name="TimeStamp",
        classes=(TimeSpan, TimeStamp),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


class Camera(_AbstractView):
    """
    Defines the virtual camera that views the scene.

    This element defines the position of the camera relative to the Earth's surface
    as well as the viewing direction of the camera. The camera position is defined
    by <longitude>, <latitude>, <altitude>, and either <altitudeMode> or
    <gx:altitudeMode>. The viewing direction of the camera is defined by
    <heading>, <tilt>, and <roll>. <Camera> can be a child element of any
    Feature or of <NetworkLinkControl>. A parent element cannot contain both a
    <Camera> and a <LookAt> at the same time.

    <Camera> provides full six-degrees-of-freedom control over the view,
    so you can position the Camera in space and then rotate it around the
    X, Y, and Z axes. Most importantly, you can tilt the camera view so that
    you're looking above the horizon into the sky.

    <Camera> can also contain a TimePrimitive (<gx:TimeSpan> or <gx:TimeStamp>).
    Time values in Camera affect historical imagery, sunlight, and the display of
    time-stamped features. For more information, read Time with AbstractViews in
    the Time and Animation chapter of the Developer's Guide.
    """

    roll: Optional[float]
    # Rotation, in degrees, of the camera around the Z axis. Values range from
    # -180 to +180 degrees.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        altitude: Optional[float] = None,
        heading: Optional[float] = None,
        tilt: Optional[float] = None,
        roll: Optional[float] = None,
        altitude_mode: AltitudeMode = AltitudeMode.relative_to_ground,
        time_primitive: Union[TimeSpan, TimeStamp, None] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new View object.

        Args:
        ----
            ns (Optional[str]): The namespace for the view.
            name_spaces (Optional[Dict[str, str]]): The dictionary of namespaces.
            id (Optional[str]): The ID of the view.
            target_id (Optional[str]): The target ID of the view.
            longitude (Optional[float]): The longitude of the view.
            latitude (Optional[float]): The latitude of the view.
            altitude (Optional[float]): The altitude of the view.
            heading (Optional[float]): The heading of the view.
            tilt (Optional[float]): The tilt of the view.
            roll (Optional[float]): The roll of the view.
            altitude_mode (AltitudeMode): The altitude mode of the view.
            time_primitive (Union[TimeSpan, TimeStamp, None]): The time primitive of the
                view.
            **kwargs (Any): Additional keyword arguments.

        Returns:
        -------
            None

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            heading=heading,
            tilt=tilt,
            altitude_mode=altitude_mode,
            time_primitive=time_primitive,
            **kwargs,
        )
        self.roll = roll

    def __repr__(self) -> str:
        """Create a string (c)representation for Camera."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"longitude={self.longitude!r}, "
            f"latitude={self.latitude!r}, "
            f"altitude={self.altitude!r}, "
            f"heading={self.heading!r}, "
            f"tilt={self.tilt!r}, "
            f"roll={self.roll!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"time_primitive={self.times!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    Camera,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="roll",
        node_name="roll",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)


class LookAt(_AbstractView):
    """
    Defines a virtual camera that is associated with any element derived from Feature.

    The LookAt element positions the "camera" in relation to the object that is being
    viewed. In Google Earth, the view "flies to" this LookAt viewpoint when the user
    double-clicks an item in the Places panel or double-clicks an icon in the 3D viewer.

    https://developers.google.com/kml/documentation/kmlreference#lookat
    """

    range: Optional[float]
    # Distance in meters from the point specified by <longitude>, <latitude>,
    # and <altitude> to the LookAt position.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        altitude: Optional[float] = None,
        heading: Optional[float] = None,
        tilt: Optional[float] = None,
        range: Optional[float] = None,
        altitude_mode: AltitudeMode = AltitudeMode.relative_to_ground,
        time_primitive: Union[TimeSpan, TimeStamp, None] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the class.

        Args:
        ----
            ns (Optional[str]): The namespace for the element.
            name_spaces (Optional[Dict[str, str]]): The dictionary of namespaces.
            id (Optional[str]): The ID of the element.
            target_id (Optional[str]): The target ID of the element.
            longitude (Optional[float]): The longitude value.
            latitude (Optional[float]): The latitude value.
            altitude (Optional[float]): The altitude value.
            heading (Optional[float]): The heading value.
            tilt (Optional[float]): The tilt value.
            range (Optional[float]): The range value.
            altitude_mode (AltitudeMode): The altitude mode. Defaults to
                AltitudeMode.relative_to_ground.
            time_primitive (Union[TimeSpan, TimeStamp, None]): The time primitive.
            **kwargs (Any): Additional keyword arguments.

        Returns:
        -------
            None

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            heading=heading,
            tilt=tilt,
            altitude_mode=altitude_mode,
            time_primitive=time_primitive,
            **kwargs,
        )
        self.range = range

    def __repr__(self) -> str:
        """Create a string (c)representation for LookAt."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"longitude={self.longitude!r}, "
            f"latitude={self.latitude!r}, "
            f"altitude={self.altitude!r}, "
            f"heading={self.heading!r}, "
            f"tilt={self.tilt!r}, "
            f"range={self.range!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"time_primitive={self.times!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    LookAt,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="range",
        node_name="range",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)


class LatLonAltBox(_XMLObject):
    """
    A bounding box defined by geographic coordinates and altitudes.

    https://developers.google.com/kml/documentation/kmlreference#latlonaltbox
    """

    _default_nsid = config.KML

    north: Optional[float]
    south: Optional[float]
    east: Optional[float]
    west: Optional[float]
    min_altitude: Optional[float]
    max_altitude: Optional[float]
    altitude_mode: Optional[AltitudeMode]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        north: Optional[float] = None,
        south: Optional[float] = None,
        east: Optional[float] = None,
        west: Optional[float] = None,
        min_altitude: Optional[float] = None,
        max_altitude: Optional[float] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new View object.

        Args:
        ----
            ns (Optional[str]): The namespace for the view.
            name_spaces (Optional[Dict[str, str]]): A dictionary of namespace prefixes
                and URIs.
            north (Optional[float]): The northern latitude of the view.
            south (Optional[float]): The southern latitude of the view.
            east (Optional[float]): The eastern longitude of the view.
            west (Optional[float]): The western longitude of the view.
            min_altitude (Optional[float]): The minimum altitude of the view.
            max_altitude (Optional[float]): The maximum altitude of the view.
            altitude_mode (Optional[AltitudeMode]): The altitude mode of the view.
            **kwargs (Any): Additional keyword arguments.

        Returns:
        -------
            None

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.min_altitude = min_altitude
        self.max_altitude = max_altitude
        self.altitude_mode = altitude_mode

    def __repr__(self) -> str:
        """Create a string (c)representation for LatLonAltBox."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"north={self.north!r}, "
            f"south={self.south!r}, "
            f"east={self.east!r}, "
            f"west={self.west!r}, "
            f"min_altitude={self.min_altitude!r}, "
            f"max_altitude={self.max_altitude!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if all the attributes (north, south, east, west) are not None.

        Returns
        -------
            bool: True if all attributes are not None, False otherwise.

        """
        return all(
            (
                self.north is not None,
                self.south is not None,
                self.east is not None,
                self.west is not None,
            ),
        )


registry.register(
    LatLonAltBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="north",
        node_name="north",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonAltBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="south",
        node_name="south",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonAltBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="east",
        node_name="east",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonAltBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="west",
        node_name="west",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonAltBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="min_altitude",
        node_name="minAltitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonAltBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="max_altitude",
        node_name="maxAltitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonAltBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        classes=(AltitudeMode,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)


class Lod(_XMLObject):
    """
    Lod is an abbreviation for Level of Detail.

    <Lod> describes the size of the projected region on the screen that is required in
    order for the region to be considered "active."
    Also specifies the size of the pixel ramp used for fading in
    (from transparent to opaque) and fading out (from opaque to transparent).

    https://developers.google.com/kml/documentation/kmlreference#elements-specific-to-region
    """

    _default_nsid = config.KML

    min_lod_pixels: Optional[float]
    max_lod_pixels: Optional[float]
    min_fade_extent: Optional[float]
    max_fade_extent: Optional[float]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        min_lod_pixels: Optional[float] = None,
        max_lod_pixels: Optional[float] = None,
        min_fade_extent: Optional[float] = None,
        max_fade_extent: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the View class.

        Args:
        ----
            ns (Optional[str]): The namespace for the view.
            name_spaces (Optional[Dict[str, str]]): The dictionary of namespace prefixes
                and URIs.
            min_lod_pixels (Optional[float]): The minimum level of detail in pixels.
            max_lod_pixels (Optional[float]): The maximum level of detail in pixels.
            min_fade_extent (Optional[float]): The minimum fade extent in pixels.
            max_fade_extent (Optional[float]): The maximum fade extent in pixels.
            **kwargs (Any): Additional keyword arguments.

        Returns:
        -------
            None

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.min_lod_pixels = min_lod_pixels
        self.max_lod_pixels = max_lod_pixels
        self.min_fade_extent = min_fade_extent
        self.max_fade_extent = max_fade_extent

    def __repr__(self) -> str:
        """Create a string (c)representation for Lod."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"min_lod_pixels={self.min_lod_pixels!r}, "
            f"max_lod_pixels={self.max_lod_pixels!r}, "
            f"min_fade_extent={self.min_fade_extent!r}, "
            f"max_fade_extent={self.max_fade_extent!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the object is considered True or False.

        Returns
        -------
            bool: True if the `min_lod_pixels` attribute is not None, False otherwise.

        """
        return self.min_lod_pixels is not None


registry.register(
    Lod,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="min_lod_pixels",
        node_name="minLodPixels",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    Lod,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="max_lod_pixels",
        node_name="maxLodPixels",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    Lod,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="min_fade_extent",
        node_name="minFadeExtent",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    Lod,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="max_fade_extent",
        node_name="maxFadeExtent",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)


class Region(_BaseObject):
    """
    A region contains a bounding box that describes an area of interest.

    In addition, a Region contains an LOD (level of detail) extent (<Lod>),
    which is a pair of projected coordinate bounding boxes that describe
    the area that should be loaded in the viewport corresponding to a given
    level of detail.

    https://developers.google.com/kml/documentation/kmlreference#region
    """

    lat_lon_alt_box: Optional[LatLonAltBox]
    lod: Optional[Lod]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        lat_lon_alt_box: Optional[LatLonAltBox] = None,
        lod: Optional[Lod] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the View class.

        Args:
        ----
        ns : Optional[str]
            The namespace of the view.
        name_spaces : Optional[Dict[str, str]]
            The dictionary of namespace prefixes and URIs.
        id : Optional[str]
            The ID of the view.
        target_id : Optional[str]
            The target ID of the view.
        lat_lon_alt_box : Optional[LatLonAltBox]
            The latitude, longitude, and altitude box of the view.
        lod : Optional[Lod]
            The level of detail of the view.
        **kwargs : Any
            Additional keyword arguments.

        Returns:
        -------
        None

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.lat_lon_alt_box = lat_lon_alt_box
        self.lod = lod

    def __repr__(self) -> str:
        """Create a string (c)representation for Region."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"lat_lon_alt_box={self.lat_lon_alt_box!r}, "
            f"lod={self.lod!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the object is considered True or False.

        Returns
        -------
            bool: True if the `lat_lon_alt_box` attribute is not empty, False otherwise.

        """
        return bool(self.lat_lon_alt_box)


registry.register(
    Region,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="lat_lon_alt_box",
        node_name="LatLonAltBox",
        classes=(LatLonAltBox,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Region,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="lod",
        node_name="Lod",
        classes=(Lod,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


__all__ = [
    "Camera",
    "LookAt",
    "Region",
]
