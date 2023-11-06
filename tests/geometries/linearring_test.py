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

from fastkml.geometry import LinearRing
from tests.base import Lxml
from tests.base import StdLibrary


class TestLinearRing(StdLibrary):
    def test_init(self) -> None:
        """Test the init method."""
        lr = geo.LinearRing(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))

        linear_ring = LinearRing(geometry=lr)

        assert linear_ring.geometry == lr
        assert linear_ring.altitude_mode is None
        assert linear_ring.extrude is False

    def test_to_string(self) -> None:
        """Test the to_string method."""
        lr = geo.LinearRing(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))

        linear_ring = LinearRing(geometry=lr)

        assert "LinearRing" in linear_ring.to_string()
        assert (
            "coordinates>0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</" in linear_ring.to_string()
        )

    def test_from_string(self) -> None:
        """Test the from_string method."""
        linear_ring = cast(
            LinearRing,
            LinearRing.class_from_string(
                '<kml:LinearRing xmlns:kml="http://www.opengis.net/kml/2.2">'
                "<kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.0,1.0 "
                "0.000000,0.000000</kml:coordinates>"
                "</kml:LinearRing>",
            ),
        )

        assert linear_ring.geometry == geo.LinearRing(((0, 0), (1, 0), (1, 1), (0, 0)))


class TestLinearRingLxml(Lxml, TestLinearRing):
    """Test with lxml."""
