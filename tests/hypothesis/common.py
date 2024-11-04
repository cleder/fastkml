# Copyright (C) 2024  Christian Ledermann
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
"""Common functionality for property based tests."""
import datetime
import logging

from dateutil.tz import tzfile
from dateutil.tz import tzutc
from pygeoif import GeometryCollection
from pygeoif import MultiLineString
from pygeoif import MultiPoint
from pygeoif import MultiPolygon
from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon

import fastkml
from fastkml.base import _XMLObject
from fastkml.enums import AltitudeMode
from fastkml.enums import DateTimeResolution
from fastkml.enums import RefreshMode
from fastkml.enums import Verbosity
from fastkml.enums import ViewRefreshMode
from fastkml.gx import Angle
from fastkml.gx import TrackItem
from fastkml.validator import validate

logger = logging.getLogger(__name__)

eval_locals = {
    "Point": Point,
    "Polygon": Polygon,
    "LineString": LineString,
    "LinearRing": LinearRing,
    "MultiPoint": MultiPoint,
    "MultiLineString": MultiLineString,
    "MultiPolygon": MultiPolygon,
    "GeometryCollection": GeometryCollection,
    "AltitudeMode": AltitudeMode,
    "fastkml": fastkml,
    "ViewRefreshMode": ViewRefreshMode,
    "RefreshMode": RefreshMode,
    "TrackItem": TrackItem,
    "Angle": Angle,
    "datetime": datetime,
    "DateTimeResolution": DateTimeResolution,
    "tzutc": tzutc,
    "tzfile": tzfile,
}


def assert_repr_roundtrip(obj: _XMLObject) -> None:
    """Test that repr(obj) can be eval'd back to obj."""
    try:
        assert obj == eval(repr(obj), {}, eval_locals)  # noqa: S307
    except FileNotFoundError:
        # The timezone file may not be available on all systems.
        logger.exception("Failed to eval repr(obj).")


def assert_str_roundtrip(obj: _XMLObject) -> None:
    """
    Test that an XML object can be serialized and deserialized without changes.

    Uses default verbosity settings and validates the resulting XML structure.
    """
    new_object = type(obj).from_string(obj.to_string())

    assert obj.to_string() == new_object.to_string()
    assert obj == new_object
    assert validate(element=new_object.etree_element())


def assert_str_roundtrip_terse(obj: _XMLObject) -> None:
    new_object = type(obj).from_string(
        obj.to_string(verbosity=Verbosity.terse),
    )

    assert obj.to_string(verbosity=Verbosity.verbose) == new_object.to_string(
        verbosity=Verbosity.verbose,
    )
    assert validate(element=new_object.etree_element())


def assert_str_roundtrip_verbose(obj: _XMLObject) -> None:
    new_object = type(obj).from_string(
        obj.to_string(verbosity=Verbosity.verbose),
    )

    assert obj.to_string(verbosity=Verbosity.terse) == new_object.to_string(
        verbosity=Verbosity.terse,
    )
    assert validate(element=new_object.etree_element())
