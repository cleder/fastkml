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
from fastkml.base import _BaseObject
from fastkml.base import _XMLObject
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity
from fastkml.helpers import enum_subelement
from fastkml.helpers import float_subelement
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.mixins import TimeMixin
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.types import Element

logger = logging.getLogger(__name__)


class _AbstractView(TimeMixin, _BaseObject):
    """
    This is an abstract element and cannot be used directly in a KML file.
    This element is extended by the <Camera> and <LookAt> elements.
    """

    longitude: Optional[float]
    # Longitude of the virtual camera (eye point). Angular distance in degrees,
    # relative to the Prime Meridian. Values west of the Meridian range from
    # −180 to 0 degrees. Values east of the Meridian range from 0 to 180 degrees.

    latitude: Optional[float]
    # Latitude of the virtual camera. Degrees north or south of the Equator
    # (0 degrees). Values range from −90 degrees to 90 degrees.

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
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.heading = heading
        self.tilt = tilt
        self.altitude_mode = altitude_mode
        self.times = time_primitive

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="longitude",
            node_name="longitude",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="latitude",
            node_name="latitude",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="altitude",
            node_name="altitude",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="heading",
            node_name="heading",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="tilt",
            node_name="tilt",
            precision=precision,
        )
        enum_subelement(
            self,
            element=element,
            attr_name="altitude_mode",
            node_name="altitudeMode",
        )
        xml_subelement(
            self,
            element=element,
            attr_name="times",
            precision=precision,
            verbosity=verbosity,
        )
        return element

    # TODO: <gx:ViewerOptions>
    # TODO: <gx:horizFov>

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
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="longitude",
                kwarg="longitude",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="latitude",
                kwarg="latitude",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="altitude",
                kwarg="altitude",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="heading",
                kwarg="heading",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="tilt",
                kwarg="tilt",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_enum_kwarg(
                element=element,
                ns=ns,
                node_name="altitudeMode",
                kwarg="altitude_mode",
                enum_class=AltitudeMode,
                strict=strict,
            ),
        )
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="time_primitive",
                obj_class=TimeSpan,
                strict=strict,
            ),
        )
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="time_primitive",
                obj_class=TimeStamp,
                strict=strict,
            ),
        )

        return kwargs


class Camera(_AbstractView):
    """
    Defines the virtual camera that views the scene. This element defines
    the position of the camera relative to the Earth's surface as well
    as the viewing direction of the camera. The camera position is defined
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
    # −180 to +180 degrees.

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
    ) -> None:
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
        )
        self.roll = roll

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="roll",
            node_name="roll",
            precision=precision,
        )
        return element

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
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="roll",
                kwarg="roll",
                strict=strict,
            ),
        )
        return kwargs


class LookAt(_AbstractView):
    range: Optional[float]
    # Distance in meters from the point specified by <longitude>, <latitude>,
    # and <altitude> to the LookAt position. (See diagram below.)

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
    ) -> None:
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
        )
        self.range = range

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="range",
            node_name="range",
            precision=precision,
        )
        return element

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
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="range",
                kwarg="range",
                strict=strict,
            ),
        )
        return kwargs


class LatLonAltBox(_XMLObject):
    """
    A bounding box defined by geographic coordinates and altitudes.

    https://developers.google.com/kml/documentation/kmlreference#latlonaltbox
    """

    _default_ns = config.KMLNS

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
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.min_altitude = min_altitude
        self.max_altitude = max_altitude
        self.altitude_mode = altitude_mode

    def __bool__(self) -> bool:
        return all(
            (
                self.north is not None,
                self.south is not None,
                self.east is not None,
                self.west is not None,
            ),
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="north",
            node_name="north",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="south",
            node_name="south",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="east",
            node_name="east",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="west",
            node_name="west",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="min_altitude",
            node_name="minAltitude",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="max_altitude",
            node_name="maxAltitude",
            precision=precision,
        )
        enum_subelement(
            self,
            element=element,
            attr_name="altitude_mode",
            node_name="altitudeMode",
        )

        return element

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
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="north",
                kwarg="north",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="south",
                kwarg="south",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="east",
                kwarg="east",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="west",
                kwarg="west",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="minAltitude",
                kwarg="min_altitude",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="maxAltitude",
                kwarg="max_altitude",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_enum_kwarg(
                element=element,
                ns=ns,
                node_name="altitudeMode",
                kwarg="altitude_mode",
                enum_class=AltitudeMode,
                strict=strict,
            ),
        )

        return kwargs


class Lod(_XMLObject):
    """
    Lod is an abbreviation for Level of Detail.
    <Lod> describes the size of the projected region on the screen that is required in
    order for the region to be considered "active."
    Also specifies the size of the pixel ramp used for fading in
    (from transparent to opaque) and fading out (from opaque to transparent).

    https://developers.google.com/kml/documentation/kmlreference#elements-specific-to-region
    """

    _default_ns = config.KMLNS

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
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.min_lod_pixels = min_lod_pixels
        self.max_lod_pixels = max_lod_pixels
        self.min_fade_extent = min_fade_extent
        self.max_fade_extent = max_fade_extent

    def __bool__(self) -> bool:
        return self.min_lod_pixels is not None

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        float_subelement(
            self,
            element=element,
            attr_name="min_lod_pixels",
            node_name="minLodPixels",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="max_lod_pixels",
            node_name="maxLodPixels",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="min_fade_extent",
            node_name="minFadeExtent",
            precision=precision,
        )
        float_subelement(
            self,
            element=element,
            attr_name="max_fade_extent",
            node_name="maxFadeExtent",
            precision=precision,
        )

        return element

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
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="minLodPixels",
                kwarg="min_lod_pixels",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="maxLodPixels",
                kwarg="max_lod_pixels",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="minFadeExtent",
                kwarg="min_fade_extent",
                strict=strict,
            ),
        )
        kwargs.update(
            subelement_float_kwarg(
                element=element,
                ns=ns,
                node_name="maxFadeExtent",
                kwarg="max_fade_extent",
                strict=strict,
            ),
        )

        return kwargs


class Region(_BaseObject):
    """
    A <Region> contains a bounding box (<LatLonAltBox>) that describes an area of
    interest defined by geographic coordinates and altitudes.

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
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.lat_lon_alt_box = lat_lon_alt_box
        self.lod = lod

    def __bool__(self) -> bool:
        return bool(self.lat_lon_alt_box)

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        xml_subelement(
            self,
            element=element,
            attr_name="lat_lon_alt_box",
            precision=precision,
            verbosity=verbosity,
        )
        xml_subelement(
            self,
            element=element,
            attr_name="lod",
            precision=precision,
            verbosity=verbosity,
        )

        return element

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
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="lat_lon_alt_box",
                obj_class=LatLonAltBox,
                strict=strict,
            ),
        )
        kwargs.update(
            xml_subelement_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                kwarg="lod",
                obj_class=Lod,
                strict=strict,
            ),
        )

        return kwargs


__all__ = [
    "Camera",
    "LookAt",
    "Region",
]
