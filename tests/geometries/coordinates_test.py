# Copyright (C) 2023 - 2024 Christian Ledermann
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

"""Test the coordinates class."""


from fastkml.geometry import Coordinates
from tests.base import Lxml
from tests.base import StdLibrary


class TestCoordinates(StdLibrary):
    def test_coordinates(self) -> None:
        """Test the init method."""
        coords = ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))

        coordinates = Coordinates(coords=coords)

        assert coordinates.to_string(precision=6).strip() == (
            '<kml:coordinates xmlns:kml="http://www.opengis.net/kml/2.2">'
            "0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000"
            "</kml:coordinates>"
        )

    def test_coordinates_from_string(self) -> None:
        """Test the from_string method."""
        coordinates = Coordinates.class_from_string(
            '<kml:coordinates xmlns:kml="http://www.opengis.net/kml/2.2">'
            "0.000000,0.000000 1.000000,0.000000 1.0,1.0 0.000000,0.000000"
            "</kml:coordinates>",
        )

        assert coordinates.coords == [(0, 0), (1, 0), (1, 1), (0, 0)]

    def test_coordinates_from_string_with_whitespace(self) -> None:
        """Test the from_string method with whitespace."""
        coordinates = Coordinates.class_from_string(
            '<kml:coordinates xmlns:kml="http://www.opengis.net/kml/2.2">\n'
            "-123.9404499372,49.169275246690,17 -123.940493701601,49.1694596207446,17 "
            "-123.940356261489,49.16947180231761,17 -123.940306243,49.169291706171,17 "
            "-123.940449937288,49.16927524669021,17   \n"
            "</kml:coordinates>",
        )

        assert coordinates.coords == [
            (-123.9404499372, 49.16927524669, 17.0),
            (-123.940493701601, 49.1694596207446, 17.0),
            (-123.940356261489, 49.16947180231761, 17.0),
            (-123.940306243, 49.169291706171, 17.0),
            (-123.940449937288, 49.16927524669021, 17.0),
        ]


class TestCoordinatesLxml(Lxml, TestCoordinates):
    pass
