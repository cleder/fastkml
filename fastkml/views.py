import logging
from typing import Optional

import fastkml.config as config
import fastkml.gx as gx
from fastkml.base import _BaseObject
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.types import Element

logger = logging.getLogger(__name__)


class _AbstractView(_BaseObject):
    """
    This is an abstract element and cannot be used directly in a KML file.
    This element is extended by the <Camera> and <LookAt> elements.
    """

    _gx_timespan = None
    _gx_timestamp = None

    def etree_element(self):
        element = super().etree_element()
        if (self._timespan is not None) and (self._timestamp is not None):
            raise ValueError("Either Timestamp or Timespan can be defined, not both")
        if self._timespan is not None:
            element.append(self._gx_timespan.etree_element())
        elif self._timestamp is not None:
            element.append(self._gx_timestamp.etree_element())
        return element

    @property
    def gx_timestamp(self):
        return self._gx_timestamp

    @gx_timestamp.setter
    def gx_timestamp(self, dt):
        self._gx_timestamp = None if dt is None else TimeStamp(timestamp=dt)
        if self._gx_timestamp is not None:
            logger.warning("Setting a TimeStamp, TimeSpan deleted")
            self._gx_timespan = None

    @property
    def begin(self):
        return self._gx_timespan.begin[0]

    @begin.setter
    def begin(self, dt) -> None:
        if self._gx_timespan is None:
            self._gx_timespan = TimeSpan(begin=dt)
        elif self._gx_timespan.begin is None:
            self._gx_timespan.begin = [dt, None]
        else:
            self._gx_timespan.begin[0] = dt
        if self._gx_timestamp is not None:
            logger.warning("Setting a TimeSpan, TimeStamp deleted")
            self._gx_timestamp = None

    @property
    def end(self):
        return self._gx_timespan.end[0]

    @end.setter
    def end(self, dt):
        if self._gx_timespan is None:
            self._gx_timespan = TimeSpan(end=dt)
        elif self._gx_timespan.end is None:
            self._gx_timespan.end = [dt, None]
        else:
            self._gx_timespan.end[0] = dt
        if self._gx_timestamp is not None:
            logger.warning("Setting a TimeSpan, TimeStamp deleted")
            self._gx_timestamp = None

    def from_element(self, element):
        super().from_element(element)
        gx_timespan = element.find(f"{gx.NS}TimeSpan")
        if gx_timespan is not None:
            self._gx_timespan = gx_timespan.text
        gx_timestamp = element.find(f"{gx.NS}TimeStamp")
        if gx_timestamp is not None:
            self._gx_timestamp = gx_timestamp.text

    # TODO: <gx:ViewerOptions>
    # TODO: <gx:horizFov>


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

    _longitude = None
    # Longitude of the virtual camera (eye point). Angular distance in degrees,
    # relative to the Prime Meridian. Values west of the Meridian range from
    # −180 to 0 degrees. Values east of the Meridian range from 0 to 180 degrees.

    _latitude = None
    # Latitude of the virtual camera. Degrees north or south of the Equator
    # (0 degrees). Values range from −90 degrees to 90 degrees.

    _altitude = None
    # Distance of the camera from the earth's surface, in meters. Interpreted
    # according to the Camera's <altitudeMode> or <gx:altitudeMode>.

    _heading = None
    # Direction (azimuth) of the camera, in degrees. Default=0 (true North).
    # (See diagram.) Values range from 0 to 360 degrees.

    _tilt = None
    # Rotation, in degrees, of the camera around the X axis. A value of 0
    # indicates that the view is aimed straight down toward the earth (the
    # most common case). A value for 90 for <tilt> indicates that the view
    # is aimed toward the horizon. Values greater than 90 indicate that the
    # view is pointed up into the sky. Values for <tilt> are clamped at +180
    # degrees.

    _roll = None
    # Rotation, in degrees, of the camera around the Z axis. Values range from
    # −180 to +180 degrees.

    _altitude_mode = "relativeToGround"
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
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        altitude: Optional[float] = None,
        heading: Optional[float] = None,
        tilt: Optional[float] = None,
        roll: Optional[float] = None,
        altitude_mode: str = "relativeToGround",
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        self._longitude = longitude
        self._latitude = latitude
        self._altitude = altitude
        self._heading = heading
        self._tilt = tilt
        self._roll = roll
        self._altitude_mode = altitude_mode

    @property
    def longitude(self) -> Optional[float]:
        return self._longitude

    @longitude.setter
    def longitude(self, value) -> None:
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._longitude = str(value)
        elif value is None:
            self._longitude = None
        else:
            raise ValueError

    @property
    def latitude(self) -> Optional[float]:
        return self._latitude

    @latitude.setter
    def latitude(self, value) -> None:
        if isinstance(value, (str, int, float)) and (-90 <= float(value) <= 90):
            self._latitude = str(value)
        elif value is None:
            self._latitude = None
        else:
            raise ValueError

    @property
    def altitude(self) -> Optional[float]:
        return self._altitude

    @altitude.setter
    def altitude(self, value) -> None:
        if isinstance(value, (str, int, float)):
            self._altitude = str(value)
        elif value is None:
            self._altitude = None
        else:
            raise ValueError

    @property
    def heading(self) -> Optional[float]:
        return self._heading

    @heading.setter
    def heading(self, value) -> None:
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._heading = str(value)
        elif value is None:
            self._heading = None
        else:
            raise ValueError

    @property
    def tilt(self) -> Optional[float]:
        return self._tilt

    @tilt.setter
    def tilt(self, value) -> None:
        if isinstance(value, (str, int, float)) and (0 <= float(value) <= 180):
            self._tilt = str(value)
        elif value is None:
            self._tilt = None
        else:
            raise ValueError

    @property
    def roll(self) -> Optional[float]:
        return self._roll

    @roll.setter
    def roll(self, value) -> None:
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._roll = str(value)
        elif value is None:
            self._roll = None
        else:
            raise ValueError

    @property
    def altitude_mode(self) -> str:
        return self._altitude_mode

    @altitude_mode.setter
    def altitude_mode(self, mode) -> None:
        if mode in ("relativeToGround", "clampToGround", "absolute"):
            self._altitude_mode = str(mode)
        else:
            self._altitude_mode = "relativeToGround"
            # raise ValueError(
            #     "altitude_mode must be one of " "relativeToGround,
            #     clampToGround, absolute")

    def from_element(self, element) -> None:
        super().from_element(element)
        longitude = element.find(f"{self.ns}longitude")
        if longitude is not None:
            self.longitude = longitude.text
        latitude = element.find(f"{self.ns}latitude")
        if latitude is not None:
            self.latitude = latitude.text
        altitude = element.find(f"{self.ns}altitude")
        if altitude is not None:
            self.altitude = altitude.text
        heading = element.find(f"{self.ns}heading")
        if heading is not None:
            self.heading = heading.text
        tilt = element.find(f"{self.ns}tilt")
        if tilt is not None:
            self.tilt = tilt.text
        roll = element.find(f"{self.ns}roll")
        if roll is not None:
            self.roll = roll.text
        altitude_mode = element.find(f"{self.ns}altitudeMode")
        if altitude_mode is not None:
            self.altitude_mode = altitude_mode.text
        else:
            altitude_mode = element.find(f"{gx.NS}altitudeMode")
            self.altitude_mode = altitude_mode.text

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.longitude:
            longitude = config.etree.SubElement(element, f"{self.ns}longitude")
            longitude.text = self.longitude
        if self.latitude:
            latitude = config.etree.SubElement(element, f"{self.ns}latitude")
            latitude.text = self.latitude
        if self.altitude:
            altitude = config.etree.SubElement(element, f"{self.ns}altitude")
            altitude.text = self.altitude
        if self.heading:
            heading = config.etree.SubElement(element, f"{self.ns}heading")
            heading.text = self.heading
        if self.tilt:
            tilt = config.etree.SubElement(element, f"{self.ns}tilt")
            tilt.text = self.tilt
        if self.roll:
            roll = config.etree.SubElement(element, f"{self.ns}roll")
            roll.text = self.roll
        if self.altitude_mode in ("clampedToGround", "relativeToGround", "absolute"):
            altitude_mode = config.etree.SubElement(element, f"{self.ns}altitudeMode")
        elif self.altitude_mode in ("clampedToSeaFloor", "relativeToSeaFloor"):
            altitude_mode = config.etree.SubElement(element, f"{gx.NS}altitudeMode")
        altitude_mode.text = self.altitude_mode
        return element


class LookAt(_AbstractView):

    _longitude = None
    # Longitude of the point the camera is looking at. Angular distance in
    # degrees, relative to the Prime Meridian. Values west of the Meridian
    # range from −180 to 0 degrees. Values east of the Meridian range from
    # 0 to 180 degrees.

    _latitude = None
    # Latitude of the point the camera is looking at. Degrees north or south
    # of the Equator (0 degrees). Values range from −90 degrees to 90 degrees.

    _altitude = None
    # Distance from the earth's surface, in meters. Interpreted according to
    # the LookAt's altitude mode.

    _heading = None
    # Direction (that is, North, South, East, West), in degrees. Default=0
    # (North). (See diagram below.) Values range from 0 to 360 degrees.

    _tilt = None
    # Angle between the direction of the LookAt position and the normal to the
    #  surface of the earth. (See diagram below.) Values range from 0 to 90
    # degrees. Values for <tilt> cannot be negative. A <tilt> value of 0
    # degrees indicates viewing from directly above. A <tilt> value of 90
    # degrees indicates viewing along the horizon.

    _range = None
    # Distance in meters from the point specified by <longitude>, <latitude>,
    # and <altitude> to the LookAt position. (See diagram below.)

    _altitude_mode = None
    # Specifies how the <altitude> specified for the LookAt point is
    # interpreted. Possible values are as follows:
    #   clampToGround -
    #       (default) Indicates to ignore the <altitude> specification and
    #       place the LookAt position on the ground.
    #   relativeToGround -
    #       Interprets the <altitude> as a value in meters above the ground.
    #   absolute -
    #       Interprets the <altitude> as a value in meters above sea level.

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._longitude = str(value)
        elif value is None:
            self._longitude = None
        else:
            raise ValueError

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if isinstance(value, (str, int, float)) and (-90 <= float(value) <= 90):
            self._latitude = str(value)
        elif value is None:
            self._latitude = None
        else:
            raise ValueError

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        if isinstance(value, (str, int, float)):
            self._altitude = str(value)
        elif value is None:
            self._altitude = None
        else:
            raise ValueError

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        if isinstance(value, (str, int, float)):
            self._heading = str(value)
        elif value is None:
            self._heading = None
        else:
            raise ValueError

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        if isinstance(value, (str, int, float)) and (0 <= float(value) <= 90):
            self._tilt = str(value)
        elif value is None:
            self._tilt = None
        else:
            raise ValueError

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, value):
        if isinstance(value, (str, int, float)):
            self._range = str(value)
        elif value is None:
            self._range = None
        else:
            raise ValueError

    @property
    def altitude_mode(self):
        return self._altitude_mode

    @altitude_mode.setter
    def altitude_mode(self, mode):
        if mode in (
            "relativeToGround",
            "clampToGround",
            "absolute",
            "relativeToSeaFloor",
            "clampToSeaFloor",
        ):
            self._altitude_mode = str(mode)
        else:
            self._altitude_mode = "relativeToGround"
            # raise ValueError(
            #     "altitude_mode must be one of "
            #     + "relativeToGround, clampToGround, absolute,
            #     + relativeToSeaFloor, clampToSeaFloor"
            # )

    def from_element(self, element):
        super().from_element(element)
        longitude = element.find(f"{self.ns}longitude")
        if longitude is not None:
            self.longitude = longitude.text
        latitude = element.find(f"{self.ns}latitude")
        if latitude is not None:
            self.latitude = latitude.text
        altitude = element.find(f"{self.ns}altitude")
        if altitude is not None:
            self.altitude = altitude.text
        heading = element.find(f"{self.ns}heading")
        if heading is not None:
            self.heading = heading.text
        tilt = element.find(f"{self.ns}tilt")
        if tilt is not None:
            self.tilt = tilt.text
        range_var = element.find(f"{self.ns}range")
        if range_var is not None:
            self.range = range_var.text
        altitude_mode = element.find(f"{self.ns}altitudeMode")
        if altitude_mode is not None:
            self.altitude_mode = altitude_mode.text
        else:
            altitude_mode = element.find(f"{gx.NS}altitudeMode")
            self.altitude_mode = altitude_mode.text

    def etree_element(self):
        element = super().etree_element()
        if self.longitude:
            longitude = config.etree.SubElement(element, f"{self.ns}longitude")
            longitude.text = self._longitude
        if self.latitude:
            latitude = config.etree.SubElement(element, f"{self.ns}latitude")
            latitude.text = self.latitude
        if self.altitude:
            altitude = config.etree.SubElement(element, f"{self.ns}altitude")
            altitude.text = self._altitude
        if self.heading:
            heading = config.etree.SubElement(element, f"{self.ns}heading")
            heading.text = self._heading
        if self.tilt:
            tilt = config.etree.SubElement(element, f"{self.ns}tilt")
            tilt.text = self._tilt
        if self.range:
            range_var = config.etree.SubElement(element, f"{self.ns}range")
            range_var.text = self._range
        if self.altitude_mode in ("clampedToGround", "relativeToGround", "absolute"):
            altitude_mode = config.etree.SubElement(element, f"{self.ns}altitudeMode")
        elif self.altitude_mode in ("clampedToSeaFloor", "relativeToSeaFloor"):
            altitude_mode = config.etree.SubElement(element, f"{gx.NS}altitudeMode")
        altitude_mode.text = self.altitude_mode
        return element
