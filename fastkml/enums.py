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
"""
Enums for the fastkml package.

This module contains the enums used in the fastkml package.

https://developers.google.com/kml/documentation/kmlreference#kml-fields

"""
import logging
from enum import Enum
from enum import unique

logger = logging.getLogger(__name__)


class RelaxedEnum(Enum):
    """
    Enum with relaxed string value matching.

    This class provides an enum with relaxed value matching, allowing case-insensitive
    comparison of enum values. If a value is not found in the enum, it will attempt to
    find a case-insensitive match. If no match is found, a `ValueError` is raised.

    Usage:
        To use this enum, simply subclass `RelaxedEnum` and define your enum values.

    Example:
    -------
        class MyEnum(RelaxedEnum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        my_value = MyEnum("VALUE1")  # Case-insensitive match
        print(my_value)  # Output: MyEnum.VALUE1

    The subclass must define all values as strings.

    """

    @classmethod
    def _missing_(cls, value: object) -> "RelaxedEnum":
        assert isinstance(value, str)  # noqa: S101
        value = value.lower()
        for member in cls:
            assert isinstance(member.value, str)  # noqa: S101
            if member.value.lower() == value.lower():
                logger.warning(
                    "%s: Found case-insensitive match for %s in %r",
                    cls.__name__,
                    value,
                    member.value,
                )
                return member
        msg = (
            f"Unknown value '{value}' for {cls.__name__}. "
            f"Known values are {', '.join(member.value for member in cls)}."
        )
        raise ValueError(msg)


@unique
class Verbosity(Enum):
    """Enum to represent the different verbosity levels."""

    quiet = 0
    normal = 1
    verbose = 2


@unique
class DateTimeResolution(RelaxedEnum):
    """Enum to represent the different date time resolutions."""

    datetime = "dateTime"
    date = "date"
    year_month = "gYearMonth"
    year = "gYear"


@unique
class AltitudeMode(RelaxedEnum):
    """
    Enum to represent the different altitude modes.

    Specifies how altitude components in the <coordinates> element are interpreted.
    Possible values are
        - clampToGround - (default) Indicates to ignore an altitude specification
          (for example, in the <coordinates> tag).
        - relativeToGround - Sets the altitude of the element relative to the actual
          ground elevation of a particular location.
          For example, if the ground elevation of a location is exactly at sea level
          and the altitude for a point is set to 9 meters,
          then the elevation for the icon of a point placemark elevation is 9 meters
          with this mode.
          However, if the same coordinate is set over a location where the ground
          elevation is 10 meters above sea level, then the elevation of the coordinate
          is 19 meters.
          A typical use of this mode is for placing telephone poles or a ski lift.
        - absolute - Sets the altitude of the coordinate relative to sea level,
          regardless of the actual elevation of the terrain beneath the element.
          For example, if you set the altitude of a coordinate to 10 meters with an
          absolute altitude mode, the icon of a point placemark will appear to be at
          ground level if the terrain beneath is also 10 meters above sea level.
          If the terrain is 3 meters above sea level, the placemark will appear elevated
          above the terrain by 7 meters.
          A typical use of this mode is for aircraft placement.
        - relativeToSeaFloor - Interprets the altitude as a value in meters above the
          sea floor.
          If the point is above land rather than sea, the altitude will be interpreted
          as being above the ground.
        - clampToSeaFloor - The altitude specification is ignored, and the point will be
          positioned on the sea floor.
          If the point is on land rather than at sea, the point will be positioned on
          the ground.

    The Values relativeToSeaFloor and clampToSeaFloor are not part of the KML definition
    but of the  <gx:altitudeMode> a KML extension in the Google extension namespace,
    allowing altitudes relative to the sea floor.
    """

    clamp_to_ground = "clampToGround"
    relative_to_ground = "relativeToGround"
    absolute = "absolute"
    clamp_to_sea_floor = "clampToSeaFloor"
    relative_to_sea_floor = "relativeToSeaFloor"


@unique
class DataType(RelaxedEnum):
    """Data type for SimpleField in extended data."""

    string = "string"
    int_ = "int"
    uint = "uint"
    short = "short"
    ushort = "ushort"
    float_ = "float"
    double = "double"
    bool_ = "bool"


@unique
class RefreshMode(RelaxedEnum):
    """
    Enum to represent the different refresh modes.

    Specifies how the link is refreshed when the "camera" changes.
    """

    on_change = "onChange"
    on_interval = "onInterval"
    on_expire = "onExpire"


@unique
class ViewRefreshMode(RelaxedEnum):
    """
    Enum to represent the different view refresh modes.

    Specifies how the link is refreshed when the "camera" changes.
    """

    never = "never"
    on_stop = "onStop"
    on_request = "onRequest"
    on_region = "onRegion"


@unique
class ColorMode(RelaxedEnum):
    """
    Enum to represent the different color modes.

    Specifies how the color is applied to the geometry.
    """

    normal = "normal"
    random = "random"


@unique
class DisplayMode(RelaxedEnum):
    """
    DisplayMode for BalloonStyle.

    If <displayMode> is default, Google Earth uses the information supplied in <text>
    to create a balloon .
    If <displayMode> is hide, Google Earth does not display the balloon.
    In Google Earth, clicking the List View icon for a Placemark whose balloon's
    <displayMode> is hide causes Google Earth to fly to the Placemark.
    """

    default = "default"
    hide = "hide"


@unique
class Shape(RelaxedEnum):
    """
    Shape for PhotoOverlay.

    The PhotoOverlay is projected onto the <shape>.
    The <shape> can be one of the following:
      - rectangle (default) - for an ordinary photo
      - cylinder - for panoramas, which can be either partial or full cylinders
      - sphere - for spherical panoramas
    """

    rectangle = "rectangle"
    cylinder = "cylinder"
    sphere = "sphere"


@unique
class GridOrigin(RelaxedEnum):
    """
    GridOrigin for GroundOverlay.

    Specifies where to begin numbering the tiles in each layer of the pyramid.
    A value of lowerLeft specifies that row 1, column 1 of each layer is in
    the bottom left corner of the grid.
    """

    lower_left = "lowerLeft"
    upper_left = "upperLeft"


@unique
class Units(RelaxedEnum):
    """
    Units for ScreenOverlay and Hotspot.

    Specifies how the <x>, <y> values are interpreted.
    """

    fraction = "fraction"
    pixels = "pixels"
    inset_pixels = "insetPixels"


@unique
class PairKey(RelaxedEnum):
    """Key for Pair."""

    normal = "normal"
    highlight = "highlight"
