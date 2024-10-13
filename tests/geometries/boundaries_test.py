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

"""Test the Outer and Inner Boundary classes."""

import pytest
from fastkml.exceptions import GeometryError
import pygeoif.geometry as geo

from fastkml.geometry import Coordinates
from fastkml.geometry import InnerBoundaryIs
from fastkml.geometry import LinearRing
from fastkml.geometry import OuterBoundaryIs
from tests.base import Lxml
from tests.base import StdLibrary


class TestBoundaries(StdLibrary):
    def test_outer_boundary(self) -> None:
        """Test the init method."""
        coords = ((1, 2), (2, 0), (0, 0), (1, 2))
        outer_boundary = OuterBoundaryIs(
            kml_geometry=LinearRing(kml_coordinates=Coordinates(coords=coords)),
        )

        assert outer_boundary.geometry == geo.LinearRing(coords)
        assert outer_boundary.to_string(prettyprint=False, precision=6).strip() == (
            '<kml:outerBoundaryIs xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:LinearRing><kml:coordinates>"
            "1.000000,2.000000 2.000000,0.000000 0.000000,0.000000 1.000000,2.000000"
            "</kml:coordinates></kml:LinearRing></kml:outerBoundaryIs>"
        )

    def test_read_outer_boundary(self) -> None:
        """Test the from_string method."""
        outer_boundary = OuterBoundaryIs.class_from_string(
            '<kml:outerBoundaryIs xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:LinearRing>"
            "<kml:coordinates>1.0,4.0 2.0,0.0 0.0,0.0 1.0,4.0</kml:coordinates>"
            "</kml:LinearRing>"
            "</kml:outerBoundaryIs>",
        )

        assert outer_boundary.geometry == geo.LinearRing(
            ((1, 4), (2, 0), (0, 0), (1, 4)),
        )

    def test_inner_boundary(self) -> None:
        """Test the init method."""
        coords = ((1, 2), (2, 0), (0, 0), (1, 2))

        inner_boundary = InnerBoundaryIs(
            kml_geometry=LinearRing(kml_coordinates=Coordinates(coords=coords)),
        )

        assert inner_boundary.geometry == geo.LinearRing(coords)
        assert bool(inner_boundary)
        assert inner_boundary.to_string(prettyprint=False, precision=6).strip() == (
            '<kml:innerBoundaryIs xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:LinearRing><kml:coordinates>"
            "1.000000,2.000000 2.000000,0.000000 0.000000,0.000000 1.000000,2.000000"
            "</kml:coordinates></kml:LinearRing></kml:innerBoundaryIs>"
        )

    def _test_boundary_geometry_error(self, boundary_class):
        p = geo.Point(1, 2)
        coords = ((1, 2), (2, 0), (0, 0), (1, 2))

        with pytest.raises(GeometryError):
            boundary_class(
                kml_geometry=LinearRing(kml_coordinates=Coordinates(coords=coords)),
                geometry=p
            )

    def test_outer_boundary_geometry_error(self):
        """Test that OuterBoundaryIs raises GeometryError with invalid geometry."""
        self._test_boundary_geometry_error(OuterBoundaryIs)

    def test_inner_boundary_geometry_error(self):
        """Test that InnerBoundaryIs raises GeometryError with invalid geometry."""
        self._test_boundary_geometry_error(InnerBoundaryIs)

    def test_read_inner_boundary_multiple_linestrings(self) -> None:
        """
        Test the from_string method.

        When there are multiple LinearRings in the innerBoundaryIs element
        only the first one is used.
        """
        inner_boundary = InnerBoundaryIs.class_from_string(
            '<kml:innerBoundaryIs xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:LinearRing>"
            "<kml:coordinates>1.0,4.0 2.0,0.0 0.0,0.0 1.0,4.0</kml:coordinates>"
            "</kml:LinearRing>"
            "<kml:LinearRing><kml:coordinates>"
            "-122.366212,37.818977,30 -122.365424,37.819294,30 "
            "-122.365704,37.819731,30 -122.366488,37.819402,30 -122.366212,37.818977,30"
            "</kml:coordinates></kml:LinearRing>"
            "</kml:innerBoundaryIs>",
        )

        assert inner_boundary.geometry == geo.LinearRing(
            ((1, 4), (2, 0), (0, 0), (1, 4)),
        )


class TestBoundariesLxml(Lxml, TestBoundaries):
    pass
