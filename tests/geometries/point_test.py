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

import pygeoif.geometry as geo
import pytest

from fastkml.exceptions import KMLParseError
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
        assert point.extrude is None

    def test_to_string_2d(self) -> None:
        """Test the to_string method."""
        p = geo.Point(1, 2)

        point = Point(geometry=p)

        assert "Point" in point.to_string()
        assert "coordinates>1.000000,2.000000</" in point.to_string()

    def test_to_string_3d(self) -> None:
        """Test the to_string method."""
        p = geo.Point(1, 2, 3)

        point = Point(geometry=p)

        assert "Point" in point.to_string()
        assert "coordinates>1.000000,2.000000,3.000000</" in point.to_string()

    def test_to_string_2d_precision_0(self) -> None:
        """Test the to_string method."""
        p = geo.Point(1, 2)

        point = Point(geometry=p)

        assert "coordinates>1,2</" in point.to_string(precision=0)

    def test_to_string_3d_precision_0(self) -> None:
        """Test the to_string method."""
        p = geo.Point(1, 2, 3)

        point = Point(geometry=p)

        assert "coordinates>1,2,3</" in point.to_string(precision=0)

    def test_to_string_2d_precision_10(self) -> None:
        """Test the to_string method."""
        p = geo.Point(1, 2)

        point = Point(geometry=p)

        assert "coordinates>1.0000000000,2.0000000000</" in point.to_string(
            precision=10,
        )

    def test_to_string_3d_precision_10(self) -> None:
        """Test the to_string method."""
        p = geo.Point(1, 2, 3)

        point = Point(geometry=p)

        assert (
            "coordinates>1.0000000000,2.0000000000,3.0000000000</"
            in point.to_string(precision=10)
        )

    def test_to_string_empty_geometry(self) -> None:
        """Test the to_string method."""
        point = Point(geometry=geo.Point(None, None))  # type: ignore[arg-type]

        assert not point

    def test_from_string_2d(self) -> None:
        """Test the from_string method for a 2 dimensional point."""
        point = Point.class_from_string(
            '<Point xmlns="http://www.opengis.net/kml/2.2">'
            "<coordinates>1.000000,2.000000</coordinates>"
            "</Point>",
        )

        assert point.geometry == geo.Point(1, 2)
        assert point.altitude_mode is None
        assert point.extrude is None
        assert point.tessellate is None

    def test_from_string_uppercase_altitude_mode_relaxed(self) -> None:
        """Test the from_string method for an uppercase altitude mode."""
        point = Point.class_from_string(
            '<Point xmlns="http://www.opengis.net/kml/2.2">'
            "<altitudeMode>RELATIVETOGROUND</altitudeMode>"
            "<coordinates>1.000000,2.000000</coordinates>"
            "</Point>",
            strict=False,
        )

        assert point.geometry == geo.Point(1, 2)
        assert point.altitude_mode.value == "relativeToGround"

    def test_from_string_uppercase_altitude_mode_strict(self) -> None:
        """Test the from_string method for an uppercase altitude mode."""
        with pytest.raises(
            KMLParseError,
            match=r"Value RELATIVETOGROUND is not a valid value for Enum AltitudeMode$",
        ):
            assert Point.class_from_string(
                '<Point xmlns="http://www.opengis.net/kml/2.2">'
                "<altitudeMode>RELATIVETOGROUND</altitudeMode>"
                "<coordinates>1.000000,2.000000</coordinates>"
                "</Point>",
            )

    def test_from_string_3d(self) -> None:
        """Test the from_string method for a 3 dimensional point."""
        point = Point.class_from_string(
            '<Point xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<altitudeMode>absolute</altitudeMode>"
            "<coordinates>1.000000,2.000000,3.000000</coordinates>"
            "</Point>",
        )

        assert point.geometry == geo.Point(1, 2, 3)
        assert point.altitude_mode.value == "absolute"
        assert point.extrude
        assert point.tessellate

    def test_empty_from_string(self) -> None:
        """Test the from_string method."""
        point = Point.class_from_string(
            "<Point/>",
            ns="",
        )

        assert not point

    def test_empty_from_string_relaxed(self) -> None:
        """Test that no error is raised when the geometry is empty and not strict."""
        point = Point.class_from_string(
            "<Point/>",
            ns="",
            strict=False,
        )

        assert point.geometry is None

    def test_from_string_empty_coordinates(self) -> None:
        point = Point.class_from_string(
            '<Point xmlns="http://www.opengis.net/kml/2.2"><coordinates/></Point>',
            ns="",
        )

        assert not point
        assert point.geometry is None

    def test_from_string_invalid_coordinates(self) -> None:

        point = Point.class_from_string(
            '<Point xmlns="http://www.opengis.net/kml/2.2">'
            "<coordinates>1</coordinates></Point>",
        )

        assert not point

    def test_from_string_invalid_coordinates_4d(self) -> None:

        point = Point.class_from_string(
            '<Point xmlns="http://www.opengis.net/kml/2.2">'
            "<coordinates>1,2,3,4</coordinates></Point>",
        )
        assert not point

    def test_from_string_invalid_coordinates_non_numerical(self) -> None:
        with pytest.raises(
            KMLParseError,
            match=r"^Invalid coordinates in",
        ):
            Point.class_from_string(
                '<Point xmlns="http://www.opengis.net/kml/2.2">'
                "<coordinates>a,b,c</coordinates></Point>",
            )

    def test_from_string_invalid_coordinates_nan(self) -> None:
        with pytest.raises(
            KMLParseError,
            match=r"^Invalid coordinates in",
        ):
            Point.class_from_string(
                '<Point xmlns="http://www.opengis.net/kml/2.2">'
                "<coordinates>a,b</coordinates></Point>",
            )


class TestPointLxml(Lxml, TestPoint):
    """Test with lxml."""
