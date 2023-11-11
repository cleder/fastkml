import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import SupportsFloat
from typing import Union
from typing import cast

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity
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

    _longitude: Optional[float] = None
    # Longitude of the virtual camera (eye point). Angular distance in degrees,
    # relative to the Prime Meridian. Values west of the Meridian range from
    # −180 to 0 degrees. Values east of the Meridian range from 0 to 180 degrees.

    _latitude: Optional[float] = None
    # Latitude of the virtual camera. Degrees north or south of the Equator
    # (0 degrees). Values range from −90 degrees to 90 degrees.

    _altitude: Optional[float] = None
    # Distance of the camera from the earth's surface, in meters. Interpreted
    # according to the Camera's <altitudeMode> or <gx:altitudeMode>.

    _heading: Optional[float] = None
    # Direction (azimuth) of the camera, in degrees. Default=0 (true North).
    # (See diagram.) Values range from 0 to 360 degrees.

    _tilt: Optional[float] = None
    # Rotation, in degrees, of the camera around the X axis. A value of 0
    # indicates that the view is aimed straight down toward the earth (the
    # most common case). A value for 90 for <tilt> indicates that the view
    # is aimed toward the horizon. Values greater than 90 indicate that the
    # view is pointed up into the sky. Values for <tilt> are clamped at +180
    # degrees.

    _altitude_mode: AltitudeMode
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
        altitude_mode: AltitudeMode = AltitudeMode.relative_to_ground,
        time_primitive: Union[TimeSpan, TimeStamp, None] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self._longitude = longitude
        self._latitude = latitude
        self._altitude = altitude
        self._heading = heading
        self._tilt = tilt
        self._altitude_mode = altitude_mode
        if isinstance(time_primitive, TimeSpan):
            self._timespan = time_primitive
        elif isinstance(time_primitive, TimeStamp):
            self._timestamp = time_primitive

    @property
    def longitude(self) -> Optional[float]:
        return self._longitude

    @longitude.setter
    def longitude(self, value: Optional[SupportsFloat]) -> None:
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._longitude = float(value)
        elif value is None:
            self._longitude = None
        else:
            raise ValueError

    @property
    def latitude(self) -> Optional[float]:
        return self._latitude

    @latitude.setter
    def latitude(self, value: Optional[SupportsFloat]) -> None:
        if isinstance(value, (str, int, float)) and (-90 <= float(value) <= 90):
            self._latitude = float(value)
        elif value is None:
            self._latitude = None
        else:
            raise ValueError

    @property
    def altitude(self) -> Optional[float]:
        return self._altitude

    @altitude.setter
    def altitude(self, value: Optional[SupportsFloat]) -> None:
        if isinstance(value, (str, int, float)):
            self._altitude = float(value)
        elif value is None:
            self._altitude = None
        else:
            raise ValueError

    @property
    def heading(self) -> Optional[float]:
        return self._heading

    @heading.setter
    def heading(self, value: Optional[SupportsFloat]) -> None:
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._heading = float(value)
        elif value is None:
            self._heading = None
        else:
            raise ValueError

    @property
    def tilt(self) -> Optional[float]:
        return self._tilt

    @tilt.setter
    def tilt(self, value: Optional[SupportsFloat]) -> None:
        if isinstance(value, (str, int, float)) and (0 <= float(value) <= 180):
            self._tilt = float(value)
        elif value is None:
            self._tilt = None
        else:
            raise ValueError

    @property
    def altitude_mode(self) -> AltitudeMode:
        return self._altitude_mode

    @altitude_mode.setter
    def altitude_mode(self, mode: AltitudeMode) -> None:
        self._altitude_mode = mode

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.longitude:
            longitude = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}longitude",
            )
            longitude.text = str(self.longitude)
        if self.latitude:
            latitude = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}latitude",
            )
            latitude.text = str(self.latitude)
        if self.altitude:
            altitude = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}altitude",
            )
            altitude.text = str(self.altitude)
        if self.heading:
            heading = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}heading",
            )
            heading.text = str(self.heading)
        if self.tilt:
            tilt = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}tilt",
            )
            tilt.text = str(self.tilt)
        if self.altitude_mode in (
            AltitudeMode.clamp_to_ground,
            AltitudeMode.relative_to_ground,
            AltitudeMode.absolute,
        ):
            altitude_mode = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}altitudeMode",
            )
        elif self.altitude_mode in (
            AltitudeMode.clamp_to_sea_floor,
            AltitudeMode.relative_to_sea_floor,
        ):
            altitude_mode = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.name_spaces['gx']}altitudeMode",
            )
        altitude_mode.text = self.altitude_mode.value
        if (self._timespan is not None) and (self._timestamp is not None):
            msg = "Either Timestamp or Timespan can be defined, not both"
            raise ValueError(msg)
        if self._timespan is not None:
            element.append(self._timespan.etree_element())
        elif self._timestamp is not None:
            element.append(self._timestamp.etree_element())
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
        longitude = element.find(f"{ns}longitude")
        if longitude is not None:
            kwargs["longitude"] = float(longitude.text)
        latitude = element.find(f"{ns}latitude")
        if latitude is not None:
            kwargs["latitude"] = float(latitude.text)
        altitude = element.find(f"{ns}altitude")
        if altitude is not None:
            kwargs["altitude"] = float(altitude.text)
        heading = element.find(f"{ns}heading")
        if heading is not None:
            kwargs["heading"] = float(heading.text)
        tilt = element.find(f"{ns}tilt")
        if tilt is not None:
            kwargs["tilt"] = float(tilt.text)
        altitude_mode = element.find(f"{ns}altitudeMode")
        if altitude_mode is None:
            altitude_mode = element.find(f"{kwargs['name_spaces']['gx']}altitudeMode")
        if altitude_mode is not None:
            kwargs["altitude_mode"] = AltitudeMode(altitude_mode.text)
        timespan = element.find(f"{ns}TimeSpan")
        if timespan is not None:
            kwargs["time_primitive"] = cast(
                TimeSpan,
                TimeSpan.class_from_element(
                    ns=ns,
                    name_spaces=name_spaces,
                    element=timespan,
                    strict=strict,
                ),
            )
        timestamp = element.find(f"{ns}TimeStamp")
        if timestamp is not None:
            kwargs["time_primitive"] = cast(
                TimeStamp,
                TimeStamp.class_from_element(
                    ns=ns,
                    name_spaces=name_spaces,
                    element=timestamp,
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

    __name__ = "Camera"

    _roll: Optional[float] = None
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
        self._roll = roll

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.roll:
            roll = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}roll",
            )
            roll.text = str(self.roll)
        return element

    @property
    def roll(self) -> Optional[float]:
        return self._roll

    @roll.setter
    def roll(self, value: float) -> None:
        self._roll = value

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
        roll = element.find(f"{ns}roll")
        if roll is not None:
            kwargs["roll"] = float(roll.text)
        return kwargs


class LookAt(_AbstractView):
    __name__ = "LookAt"

    _range: Optional[float] = None
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
        self._range = range

    @property
    def range(self) -> Optional[float]:
        return self._range

    @range.setter
    def range(self, value: float) -> None:
        self._range = value

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.range:
            range_var = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}range",
            )
            range_var.text = str(self._range)
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
        range_var = element.find(f"{ns}range")
        if range_var is not None:
            kwargs["range"] = float(range_var.text)
        return kwargs


__all__ = [
    "Camera",
    "LookAt",
]
