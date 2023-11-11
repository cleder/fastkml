# Copyright (C) 2023 Christian Ledermann
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

from fastkml.geometry import Polygon
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_exterior_only(self) -> None:
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

    def test_exterior_interior(self) -> None:
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

    def test_from_string_exterior_only(self) -> None:
        """Test exterior only."""
        doc = """<kml:Polygon xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:outerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
              0.000000,0.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:outerBoundaryIs>
        </kml:Polygon>"""

        polygon2 = cast(Polygon, Polygon.class_from_string(doc))

        assert polygon2.geometry == geo.Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])

    def test_from_string_exterior_interior(self) -> None:
        doc = """<kml:Polygon xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:outerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>-1.000000,-1.000000 2.000000,-1.000000 2.000000,2.000000
              -1.000000,-1.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:outerBoundaryIs>
          <kml:innerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
              0.000000,0.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:innerBoundaryIs>
        </kml:Polygon>
        """

        polygon2 = cast(Polygon, Polygon.class_from_string(doc))

        assert polygon2.geometry == geo.Polygon(
            [(-1, -1), (2, -1), (2, 2), (-1, -1)],
            [[(0, 0), (1, 0), (1, 1), (0, 0)]],
        )

    def test_empty_polygon(self) -> None:
        """Test empty polygon."""
        doc = (
            "<Polygon><tessellate>1</tessellate><outerBoundaryIs>"
            "<LinearRing><coordinates/></LinearRing></outerBoundaryIs></Polygon>"
        )

        polygon = cast(Polygon, Polygon.class_from_string(doc, ns=""))

        assert not polygon.geometry
        assert polygon.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
