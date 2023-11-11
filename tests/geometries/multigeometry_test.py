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

from fastkml.geometry import MultiGeometry
from tests.base import Lxml
from tests.base import StdLibrary


class TestMultiPointStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_1_point(self) -> None:
        """Test with one point."""
        p = geo.MultiPoint([(1, 2)])

        mg = MultiGeometry(ns="", geometry=p)

        assert "coordinates>1.000000,2.000000</" in mg.to_string()
        assert "MultiGeometry>" in mg.to_string()
        assert "Point>" in mg.to_string()

    def test_2_points(self) -> None:
        """Test with two points."""
        p = geo.MultiPoint([(1, 2), (3, 4)])

        mg = MultiGeometry(ns="", geometry=p)

        assert "coordinates>1.000000,2.000000</" in mg.to_string()
        assert "coordinates>3.000000,4.000000</" in mg.to_string()
        assert "MultiGeometry>" in mg.to_string()
        assert "Point>" in mg.to_string()

    def test_2_points_read(self) -> None:
        xml = (
            "<MultiGeometry><extrude>0</extrude><tessellate>0</tessellate>"
            "<Point><coordinates>1.000000,2.000000</coordinates></Point>"
            "<Point><coordinates>3.000000,4.000000</coordinates></Point></MultiGeometry>"
        )

        mg = MultiGeometry.class_from_string(xml, ns="")

        assert mg.geometry == geo.MultiPoint([(1, 2), (3, 4)])


class TestMultiLineStringStdLibrary(StdLibrary):
    def test_1_linestring(self) -> None:
        """Test with one linestring."""
        p = geo.MultiLineString([[(1, 2), (3, 4)]])

        mg = MultiGeometry(ns="", geometry=p)

        assert "coordinates>1.000000,2.000000 3.000000,4.000000</" in mg.to_string()
        assert "MultiGeometry>" in mg.to_string()
        assert "LineString>" in mg.to_string()

    def test_2_linestrings(self) -> None:
        """Test with two linestrings."""
        p = geo.MultiLineString([[(1, 2), (3, 4)], [(5, 6), (7, 8)]])

        mg = MultiGeometry(ns="", geometry=p)

        assert "coordinates>1.000000,2.000000 3.000000,4.000000</" in mg.to_string()
        assert "coordinates>5.000000,6.000000 7.000000,8.000000</" in mg.to_string()
        assert "MultiGeometry>" in mg.to_string()
        assert "LineString>" in mg.to_string()

    def test_2_linestrings_read(self) -> None:
        xml = (
            "<MultiGeometry><extrude>0</extrude><tessellate>0</tessellate>"
            "<LineString><coordinates>1.000000,2.000000 3.000000,4.000000</coordinates>"
            "</LineString><LineString>"
            "<coordinates>5.000000,6.000000 7.000000,8.000000</coordinates>"
            "</LineString></MultiGeometry>"
        )

        mg = MultiGeometry.class_from_string(xml, ns="")

        assert mg.geometry == geo.MultiLineString([[(1, 2), (3, 4)], [(5, 6), (7, 8)]])


class TestMultiPolygonStdLibrary(StdLibrary):
    def test_1_polygon(self) -> None:
        """Test with one polygon."""
        p = geo.MultiPolygon([[[[1, 2], [3, 4], [5, 6], [1, 2]]]])

        mg = MultiGeometry(ns="", geometry=p)

        assert (
            "coordinates>1.000000,2.000000 3.000000,4.000000 5.000000,6.000000 "
            "1.000000,2.000000</" in mg.to_string()
        )
        assert "MultiGeometry>" in mg.to_string()
        assert "Polygon>" in mg.to_string()
        assert "outerBoundaryIs>" in mg.to_string()
        assert "innerBoundaryIs>" not in mg.to_string()

    def test_1_polygons_with_holes(self) -> None:
        """Test with one polygon with holes."""
        p = geo.MultiPolygon(
            [
                (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                    [((0.25, 0.25), (0.25, 0.5), (0.5, 0.5), (0.5, 0.25))],
                ),
            ],
        )
        mg = MultiGeometry(ns="", geometry=p)

        assert (
            "coordinates>0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</coordinates" in mg.to_string()
        )
        assert (
            "coordinates>0.250000,0.250000 0.250000,0.500000 0.500000,0.500000 "
            "0.500000,0.250000 0.250000,0.250000</coordinates" in mg.to_string()
        )
        assert "MultiGeometry>" in mg.to_string()
        assert "Polygon>" in mg.to_string()
        assert "outerBoundaryIs>" in mg.to_string()
        assert "innerBoundaryIs>" in mg.to_string()

    def test_2_polygons(self) -> None:
        """Test with two polygons."""
        p = geo.MultiPolygon(
            [
                (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                    [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
                ),
                (((0.0, 0.0), (0.0, 2.0), (1.0, 1.0), (1.0, 0.0)),),
            ],
        )

        mg = MultiGeometry(ns="", geometry=p)

        assert (
            "coordinates>0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</coordinates" in mg.to_string()
        )
        assert (
            "coordinates>0.100000,0.100000 0.100000,0.200000 0.200000,0.200000 "
            "0.200000,0.100000 0.100000,0.100000</coordinates" in mg.to_string()
        )
        assert (
            "coordinates>0.000000,0.000000 0.000000,2.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</coordinates" in mg.to_string()
        )
        assert "MultiGeometry>" in mg.to_string()
        assert "Polygon>" in mg.to_string()
        assert "outerBoundaryIs>" in mg.to_string()
        assert "innerBoundaryIs>" in mg.to_string()

    def test_2_polygons_read(self) -> None:
        xml = (
            "<MultiGeometry><extrude>0</extrude><tessellate>0</tessellate>"
            "<Polygon><outerBoundaryIs><LinearRing>"
            "<coordinates>0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</coordinates>"
            "</LinearRing></outerBoundaryIs>"
            "<innerBoundaryIs><LinearRing>"
            "<coordinates>0.100000,0.100000 0.100000,0.200000 0.200000,0.200000 "
            "0.200000,0.100000 0.100000,0.100000</coordinates>"
            "</LinearRing></innerBoundaryIs></Polygon>"
            "<Polygon><outerBoundaryIs><LinearRing>"
            "<coordinates>0.000000,0.000000 0.000000,2.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</coordinates>"
            "</LinearRing></outerBoundaryIs></Polygon></MultiGeometry>"
        )

        mg = MultiGeometry.class_from_string(xml, ns="")

        assert mg.geometry == geo.MultiPolygon(
            [
                (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                    [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
                ),
                (((0.0, 0.0), (0.0, 2.0), (1.0, 1.0), (1.0, 0.0)),),
            ],
        )


class TestGeometryCollectionStdLibrary(StdLibrary):
    """Test heterogeneous geometry collections."""

    def test_1_point(self) -> None:
        """Test with one point."""
        p = geo.GeometryCollection([geo.Point(1, 2)])

        mg = MultiGeometry(ns="", geometry=p)

        assert "coordinates>1.000000,2.000000</" in mg.to_string()
        assert "MultiGeometry>" in mg.to_string()
        assert "Point>" in mg.to_string()

    def test_geometries(self) -> None:
        p = geo.Point(1, 2)
        ls = geo.LineString(((1, 2), (2, 0)))
        lr = geo.LinearRing(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        poly = geo.Polygon(
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],
            [[(0.1, 0.1), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1), (0.1, 0.1)]],
        )
        gc = geo.GeometryCollection([p, ls, lr, poly])

        mg = MultiGeometry(ns="", geometry=gc)

        assert "Point>" in mg.to_string()
        assert "LineString>" in mg.to_string()
        assert "LinearRing>" in mg.to_string()
        assert "Polygon>" in mg.to_string()
        assert "MultiGeometry>" in mg.to_string()

    def test_multi_geometries(self) -> None:
        p = geo.Point(1, 2)
        ls = geo.LineString(((1, 2), (2, 0)))
        lr = geo.LinearRing(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        poly = geo.Polygon(
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],
            [[(0.1, 0.1), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1), (0.1, 0.1)]],
        )
        gc = geo.GeometryCollection([p, ls, lr, poly])
        mp = geo.MultiPolygon(
            [
                (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                    [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
                ),
                (((0.0, 0.0), (0.0, 2.0), (1.0, 1.0), (1.0, 0.0)),),
            ],
        )
        ml = geo.MultiLineString([[(1, 2), (3, 4)], [(5, 6), (7, 8)]])
        mgc = geo.GeometryCollection([gc, mp, ml])
        mg = MultiGeometry(ns="", geometry=mgc)

        assert "Point>" in mg.to_string()
        assert "LineString>" in mg.to_string()
        assert "LinearRing>" in mg.to_string()
        assert "Polygon>" in mg.to_string()
        assert "MultiGeometry>" in mg.to_string()

    def test_multi_geometries_read(self) -> None:
        xml = (
            "<MultiGeometry><extrude>0</extrude><tessellate>0</tessellate>"
            "<MultiGeometry><Point><coordinates>1.000000,2.000000</coordinates></Point>"
            "<LineString><coordinates>1.000000,2.000000 2.000000,0.000000</coordinates>"
            "</LineString><LinearRing><coordinates>0.000000,0.000000 0.000000,1.000000 "
            "1.000000,1.000000 1.000000,0.000000 0.000000,0.000000</coordinates>"
            "</LinearRing><Polygon><outerBoundaryIs><LinearRing>"
            "<coordinates>0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</coordinates></LinearRing>"
            "</outerBoundaryIs><innerBoundaryIs><LinearRing>"
            "<coordinates>0.100000,0.100000 0.100000,0.900000 0.900000,0.900000 "
            "0.900000,0.100000 0.100000,0.100000</coordinates></LinearRing>"
            "</innerBoundaryIs></Polygon></MultiGeometry>"
            "<MultiGeometry><Polygon><outerBoundaryIs><LinearRing>"
            "<coordinates>0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</coordinates></LinearRing>"
            "</outerBoundaryIs><innerBoundaryIs><LinearRing>"
            "<coordinates>0.100000,0.100000 0.100000,0.200000 0.200000,0.200000 "
            "0.200000,0.100000 0.100000,0.100000</coordinates></LinearRing>"
            "</innerBoundaryIs></Polygon>"
            "<Polygon><outerBoundaryIs><LinearRing>"
            "<coordinates>0.000000,0.000000 0.000000,2.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</coordinates></LinearRing>"
            "</outerBoundaryIs></Polygon></MultiGeometry><MultiGeometry><LineString>"
            "<coordinates>1.000000,2.000000 3.000000,4.000000</coordinates>"
            "</LineString><LineString><coordinates>5.000000,6.000000 7.000000,8.000000"
            "</coordinates></LineString></MultiGeometry></MultiGeometry>"
        )

        mg = MultiGeometry.class_from_string(xml, ns="")

        assert mg.geometry == geo.GeometryCollection(
            (
                geo.GeometryCollection(
                    (
                        geo.Point(1.0, 2.0),
                        geo.LineString(((1.0, 2.0), (2.0, 0.0))),
                        geo.Polygon(
                            (
                                (0.0, 0.0),
                                (0.0, 1.0),
                                (1.0, 1.0),
                                (1.0, 0.0),
                                (0.0, 0.0),
                            ),
                            (
                                (
                                    (0.1, 0.1),
                                    (0.1, 0.9),
                                    (0.9, 0.9),
                                    (0.9, 0.1),
                                    (0.1, 0.1),
                                ),
                            ),
                        ),
                        geo.LinearRing(
                            (
                                (0.0, 0.0),
                                (0.0, 1.0),
                                (1.0, 1.0),
                                (1.0, 0.0),
                                (0.0, 0.0),
                            ),
                        ),
                    ),
                ),
                geo.MultiPolygon(
                    (
                        (
                            (
                                (0.0, 0.0),
                                (0.0, 1.0),
                                (1.0, 1.0),
                                (1.0, 0.0),
                                (0.0, 0.0),
                            ),
                            (
                                (
                                    (0.1, 0.1),
                                    (0.1, 0.2),
                                    (0.2, 0.2),
                                    (0.2, 0.1),
                                    (0.1, 0.1),
                                ),
                            ),
                        ),
                        (((0.0, 0.0), (0.0, 2.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),
                    ),
                ),
                geo.MultiLineString(
                    (((1.0, 2.0), (3.0, 4.0)), ((5.0, 6.0), (7.0, 8.0))),
                ),
            ),
        )

    def test_empty_multi_geometries_read(self) -> None:
        xml = (
            "<MultiGeometry><extrude>0</extrude><tessellate>0</tessellate>"
            "<MultiGeometry></MultiGeometry></MultiGeometry>"
        )

        mg = MultiGeometry.class_from_string(xml, ns="")

        assert mg.geometry is None
        assert "MultiGeometry>" in mg.to_string()
        assert "coordinates>" not in mg.to_string()


class TestMultiPointLxml(Lxml, TestMultiPointStdLibrary):
    """Test with lxml."""


class TestMultiLineStringLxml(Lxml, TestMultiLineStringStdLibrary):
    """Test with lxml."""


class TestMultiPolygonLxml(Lxml, TestMultiPolygonStdLibrary):
    """Test with lxml."""


class TestGeometryCollectionLxml(Lxml, TestGeometryCollectionStdLibrary):
    """Test with lxml."""
