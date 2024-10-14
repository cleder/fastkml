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

"""Test the geometry classes."""

import pygeoif.geometry as geo
import pytest

from fastkml import exceptions
from fastkml.enums import Verbosity
from fastkml.exceptions import GeometryError, KMLParseError
from fastkml.geometry import Coordinates, LineString
from tests.base import Lxml
from tests.base import StdLibrary


class TestLineString(StdLibrary):
    def test_init(self) -> None:
        """Test the init method."""
        ls = geo.LineString(((1, 2), (2, 0)))

        line_string = LineString(geometry=ls)

        assert line_string.geometry == ls
        assert line_string.altitude_mode is None
        assert line_string.extrude is None

    def test_geometry_error(self) -> None:
        """Test GeometryError."""
        p = geo.Point(1, 2)
        q = Coordinates(ns="ns")

        with pytest.raises(GeometryError):
            LineString(geometry=p, kml_coordinates=q)

    def test_to_string(self) -> None:
        """Test the to_string method."""
        ls = geo.LineString(((1, 2), (2, 0)))

        line_string = LineString(geometry=ls)

        assert "LineString" in line_string.to_string()
        assert (
            "coordinates>1.000000,2.000000 2.000000,0.000000</"
            in line_string.to_string(precision=6)
        )

    def test_from_string(self) -> None:
        """Test the from_string method."""
        linestring = LineString.class_from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<coordinates>"
            "-122.364383,37.824664,0 -122.364152,37.824322,0"
            "</coordinates>"
            "</LineString>",
        )

        assert linestring.geometry == geo.LineString(
            ((-122.364383, 37.824664, 0), (-122.364152, 37.824322, 0)),
        )

    def test_mixed_2d_3d_coordinates_from_string(self) -> None:

        linestring = LineString.class_from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<coordinates>"
            "-122.364383,37.824664 -122.364152,37.824322,0"
            "</coordinates>"
            "</LineString>",
        )

        assert not linestring

    def test_mixed_2d_3d_coordinates_from_string_relaxed(self) -> None:
        line_string = LineString.class_from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<coordinates>"
            "-122.364383,37.824664 -122.364152,37.824322,0"
            "</coordinates>"
            "</LineString>",
            strict=False,
        )

        assert not line_string

    def test_empty_from_string(self) -> None:
        """Test the from_string method with an empty LineString."""
        linestring = LineString.class_from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<coordinates>"
            "</coordinates>"
            "</LineString>",
        )

        assert not linestring.geometry

    def test_no_coordinates_from_string(self) -> None:
        """Test the from_string method with no coordinates."""
        linestring = LineString.class_from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "</LineString>",
        )

        assert not linestring.geometry

    def test_from_string_invalid_coordinates_non_numerical(self) -> None:
        """Test the from_string method with invalid coordinates."""
        with pytest.raises(
            KMLParseError,
            match=r"^Invalid coordinates in",
        ):
            LineString.class_from_string(
                '<LineString xmlns="http://www.opengis.net/kml/2.2">'
                "<extrude>1</extrude>"
                "<tessellate>1</tessellate>"
                "<coordinates>"
                "foo,bar"
                "</coordinates>"
                "</LineString>",
            )

    def test_from_string_invalid_coordinates_nan(self) -> None:
        line_string = LineString.class_from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>false</extrude>"
            "<tessellate>true</tessellate>"
            "<coordinates>"
            "-70.64950,-35.31494,2178 -70.64898,-35.31520,2121 "
            "-70.65240,-35.32666,1930 -70.65347,-35.32906,NaN "
            "-70.65340,-35.33055,1640  -70.64347,-35.34734,1468"
            "</coordinates>"
            "</LineString>",
        )

        assert line_string.geometry
        assert len(line_string.geometry.coords) == 5
        assert line_string.to_string()

    def test_from_string_invalid_extrude(self) -> None:
        """Test the from_string method."""
        with pytest.raises(
            exceptions.KMLParseError,
        ):
            LineString.class_from_string(
                '<LineString id="my-id" targetId="target_id" '
                'xmlns="http://www.opengis.net/kml/2.2">'
                "<extrude>invalid</extrude>"
                "</LineString>",
            )

    def test_from_string_invalid_tessellate(self) -> None:
        """Test the from_string method."""
        with pytest.raises(
            exceptions.KMLParseError,
        ):
            LineString.class_from_string(
                '<LineString id="my-id" targetId="target_id" '
                'xmlns="http://www.opengis.net/kml/2.2">'
                "<tessellate>invalid</tessellate>"
                "</LineString>",
            )

    def test_to_string_terse_default(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls, extrude=False, tessellate=False)

        xml = line_string.to_string(verbosity=Verbosity.terse)

        assert "tessellate" not in xml
        assert "extrude" not in xml

    def test_to_string_terse(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls, extrude=True, tessellate=True)

        xml = line_string.to_string(verbosity=Verbosity.terse)

        assert "tessellate>1</" in xml
        assert "extrude>1</" in xml

    def test_to_string_verbose_default(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls, extrude=False, tessellate=False)

        xml = line_string.to_string(verbosity=Verbosity.verbose)

        assert "tessellate>0</" in xml
        assert "extrude>0</" in xml

    def test_to_string_verbose(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls, extrude=True, tessellate=True)

        xml = line_string.to_string(verbosity=Verbosity.verbose)

        assert "tessellate>1</" in xml
        assert "extrude>1</" in xml

    def test_to_string_verbose_none(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls)

        xml = line_string.to_string(verbosity=Verbosity.verbose)

        assert "tessellate>0</" in xml
        assert "extrude>0</" in xml


class TestLineStringLxml(Lxml, TestLineString):
    """Test with lxml."""
