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

import pygeoif.geometry as geo
import pytest

from fastkml.exceptions import KMLParseError
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

        polygon2 = Polygon.class_from_string(doc)

        assert polygon2.geometry == geo.Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])

    def test_from_string_interiors_only(self) -> None:
        """Test polygon without exterior."""
        doc = """<kml:Polygon xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:innerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
              0.000000,0.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:innerBoundaryIs>
        </kml:Polygon>"""

        with pytest.raises(KMLParseError, match=r"^Missing outerBoundaryIs in <"):
            Polygon.class_from_string(doc)

    def test_from_string_exterior_wo_linearring(self) -> None:
        """Test exterior when no LinearRing in outer boundary."""
        doc = """<kml:Polygon xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:outerBoundaryIs>
            <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
            0.000000,0.000000</kml:coordinates>
          </kml:outerBoundaryIs>
          </kml:Polygon>"""

        with pytest.raises(KMLParseError, match=r"^Missing LinearRing in <"):
            Polygon.class_from_string(doc)

    def test_from_string_interior_wo_linearring(self) -> None:
        """Test interior when no LinearRing in inner boundary."""
        doc = """<kml:Polygon xmlns:kml="http://www.opengis.net/kml/2.2">
        <kml:outerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
              0.000000,0.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:outerBoundaryIs>
        <kml:innerBoundaryIs>
        <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
        0.000000,0.000000</kml:coordinates>
        </kml:innerBoundaryIs>
        </kml:Polygon>"""

        with pytest.raises(KMLParseError, match=r"^Missing LinearRing in <"):
            Polygon.class_from_string(doc)

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

        polygon = Polygon.class_from_string(doc)

        assert polygon.geometry == geo.Polygon(
            [(-1, -1), (2, -1), (2, 2), (-1, -1)],
            [[(0, 0), (1, 0), (1, 1), (0, 0)]],
        )

    def test_from_string_exterior_mixed_interior_relaxed(self) -> None:
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
              0.000000,0.000000,1.00000</kml:coordinates>
            </kml:LinearRing>
          </kml:innerBoundaryIs>
        </kml:Polygon>
        """

        polygon = Polygon.class_from_string(doc, strict=False)

        assert polygon.geometry == geo.Polygon(
            ((-1.0, -1.0), (2.0, -1.0), (2.0, 2.0), (-1.0, -1.0)),
        )

    def test_empty_polygon(self) -> None:
        """Test empty polygon."""
        doc = (
            "<Polygon><tessellate>1</tessellate><outerBoundaryIs>"
            "<LinearRing><coordinates/></LinearRing></outerBoundaryIs></Polygon>"
        )

        polygon = Polygon.class_from_string(doc, ns="")

        assert not polygon.geometry
        assert polygon.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
