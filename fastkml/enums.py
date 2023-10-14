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
from enum import Enum
from enum import unique


@unique
class Verbosity(Enum):
    """Enum to represent the different verbosity levels."""

    quiet = 0
    normal = 1
    verbose = 2


@unique
class DateTimeResolution(Enum):
    """Enum to represent the different date time resolutions."""

    datetime = "dateTime"
    date = "date"
    year_month = "gYearMonth"
    year = "gYear"


@unique
class AltitudeMode(Enum):
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
