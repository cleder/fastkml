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
from typing import cast

import pygeoif.geometry as geo

from fastkml.geometry import LineString
from tests.base import Lxml
from tests.base import StdLibrary


class TestLineString(StdLibrary):
    def test_init(self) -> None:
        """Test the init method."""
        ls = geo.LineString(((1, 2), (2, 0)))

        line_string = LineString(geometry=ls)

        assert line_string.geometry == ls
        assert line_string.altitude_mode is None
        assert line_string.extrude is False

    def test_to_string(self) -> None:
        """Test the to_string method."""
        ls = geo.LineString(((1, 2), (2, 0)))

        line_string = LineString(geometry=ls)

        assert "LineString" in line_string.to_string()
        assert (
            "coordinates>1.000000,2.000000 2.000000,0.000000</"
            in line_string.to_string()
        )

    def test_from_string(self) -> None:
        """Test the from_string method."""
        linestring = cast(
            LineString,
            LineString.class_from_string(
                '<LineString xmlns="http://www.opengis.net/kml/2.2">'
                "<extrude>1</extrude>"
                "<tessellate>1</tessellate>"
                "<coordinates>"
                "-122.364383,37.824664,0 -122.364152,37.824322,0"
                "</coordinates>"
                "</LineString>",
            ),
        )

        assert linestring.geometry == geo.LineString(
            ((-122.364383, 37.824664, 0), (-122.364152, 37.824322, 0)),
        )


class TestLineStringLxml(Lxml, TestLineString):
    """Test with lxml."""
