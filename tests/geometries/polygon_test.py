# Copyright (C) 2021  Christian Ledermann
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

from fastkml.geometry import Polygon
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_exterior_only(self):
        """Test exterior only."""
        poly = geo.Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])

        polygon = Polygon(ns="", geometry=poly)

        assert "outerBoundaryIs>" in polygon.to_string()
        assert "innerBoundaryIs>" not in polygon.to_string()
        assert "LinearRing>" in polygon.to_string()
        assert (
            "0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000"
        ) in polygon.to_string()

    def test_exterior_interior(self):
        """Test exterior and interior."""
        poly = geo.Polygon(
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],
            [[(0.1, 0.1), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1), (0.1, 0.1)]],
        )

        polygon = Polygon(ns="", geometry=poly)

        assert "outerBoundaryIs>" in polygon.to_string()
        assert "innerBoundaryIs>" in polygon.to_string()
        assert "LinearRing>" in polygon.to_string()
        assert (
            "0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000"
        ) in polygon.to_string()
        assert (
            "0.100000,0.100000 0.100000,0.900000 0.900000,0.900000 "
            "0.900000,0.100000 0.100000,0.100000"
        ) in polygon.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
