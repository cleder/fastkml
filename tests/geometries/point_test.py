# Copyright (C) 2021 - 2023  Christian Ledermann
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

"""Test the geometry classes."""
from typing import cast

import pygeoif.geometry as geo
import pytest

from fastkml.exceptions import KMLParseError
from fastkml.exceptions import KMLWriteError
from fastkml.geometry import Point
from tests.base import Lxml
from tests.base import StdLibrary


class TestPoint(StdLibrary):
    """Test the Point class."""

    def test_init(self) -> None:
        """Test the init method."""
        p = geo.Point(1, 2)

        point = Point(geometry=p)

        assert point.geometry == p
        assert point.altitude_mode is None
        assert point.extrude is False

    def test_to_string(self) -> None:
        """Test the to_string method."""
        p = geo.Point(1, 2)

        point = Point(geometry=p)

        assert "Point" in point.to_string()
        assert "coordinates>1.000000,2.000000</" in point.to_string()

    def test_to_string_empty_geometry(self) -> None:
        """Test the to_string method."""
        point = Point(geometry=geo.Point(None, None))  # type: ignore[arg-type]

        with pytest.raises(
            KMLWriteError,
            match=r"Invalid dimensions in coordinates '\(\(\),\)'",
        ):
            point.to_string()

    def test_from_string(self) -> None:
        """Test the from_string method."""
        point = cast(
            Point,
            Point.class_from_string(
                '<Point xmlns="http://www.opengis.net/kml/2.2">'
                "<coordinates>1.000000,2.000000</coordinates>"
                "</Point>",
            ),
        )

        assert point.geometry == geo.Point(1, 2)
        assert point.altitude_mode is None
        assert point.extrude is None
        assert point.tessellate is None

    def test_empty_from_string(self) -> None:
        """Test the from_string method."""
        with pytest.raises(KMLParseError, match=r"Invalid coordinates in <Point\s*/>"):
            Point.class_from_string(
                "<Point/>",
                ns="",
            )

    def test_from_string_empty_coordinates(self) -> None:
        with pytest.raises(
            KMLParseError,
            match=r"Invalid coordinates in <Point\s*><coordinates\s*/></Point>",
        ):
            Point.class_from_string(
                "<Point><coordinates/></Point>",
                ns="",
            )

    def test_from_string_invalid_coordinates(self) -> None:
        with pytest.raises(
            KMLParseError,
            match=(
                r"Invalid coordinates in <Point\s*>"
                "<coordinates>1</coordinates></Point>"
            ),
        ):
            Point.class_from_string(
                "<Point><coordinates>1</coordinates></Point>",
                ns="",
            )


class TestPointLxml(Lxml, TestPoint):
    """Test with lxml."""
