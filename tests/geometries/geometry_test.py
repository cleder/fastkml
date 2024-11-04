# Copyright (C) 2021 - 2024  Christian Ledermann
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
import pytest
from pygeoif import geometry as geo

from fastkml.enums import AltitudeMode
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.geometry import _Geometry
from fastkml.geometry import create_kml_geometry
from tests.base import Lxml
from tests.base import StdLibrary


class TestGetGeometry(StdLibrary):
    def test_altitude_mode(self) -> None:
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:altitudeMode>clampToGround</kml:altitudeMode>
        </kml:Point>"""

        g = Point.from_string(doc)

        assert g.altitude_mode == AltitudeMode("clampToGround")

    def test_gx_altitude_mode(self) -> None:
        doc = (
            '<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2" '
            'xmlns:gx="http://www.google.com/kml/ext/2.2">'
            "<kml:coordinates>0.000000,1.000000</kml:coordinates>"
            "<gx:altitudeMode>clampToSeaFloor</gx:altitudeMode>"
            "</kml:Point>"
        )
        g = Point.from_string(doc)

        assert g.altitude_mode == AltitudeMode("clampToSeaFloor")

    def test_extrude(self) -> None:
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:extrude>1</kml:extrude>
        </kml:Point>"""

        g = Point.from_string(doc)

        assert g.extrude is True

    def test_tessellate(self) -> None:
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:tessellate>1</kml:tessellate>
        </kml:Point>"""

        g = Point.from_string(doc)

        assert not hasattr(g, "tessellate")

    def test_point(self) -> None:
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
        </kml:Point>"""

        g = Point.from_string(doc)

        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "Point",
            "bbox": (0.0, 1.0, 0.0, 1.0),
            "coordinates": (0.0, 1.0),
        }

    def test_linestring(self) -> None:
        doc = """<kml:LineString xmlns:kml="http://www.opengis.net/kml/2.2">
            <kml:coordinates>0.000000,0.000000 1.000000,1.000000</kml:coordinates>
        </kml:LineString>"""

        g = LineString.from_string(doc)

        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "LineString",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": ((0.0, 0.0), (1.0, 1.0)),
        }

    def test_linearring(self) -> None:
        doc = """<kml:LinearRing xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
          0.000000,0.000000</kml:coordinates>
        </kml:LinearRing>
        """

        g = LinearRing.from_string(doc)

        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "LinearRing",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)),
        }

    def test_polygon(self) -> None:
        doc = """<kml:Polygon xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:outerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
              0.000000,0.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:outerBoundaryIs>
        </kml:Polygon>
        """

        g = Polygon.from_string(doc)

        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "Polygon",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": (((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)),),
        }

    def test_polygon_with_inner_boundary(self) -> None:
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

        g = Polygon.from_string(doc)

        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "Polygon",
            "bbox": (-1.0, -1.0, 2.0, 2.0),
            "coordinates": (
                ((-1.0, -1.0), (2.0, -1.0), (2.0, 2.0), (-1.0, -1.0)),
                ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)),
            ),
        }

    def test_multipoint(self) -> None:
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:Point>
            <kml:coordinates>0.000000,1.000000</kml:coordinates>
          </kml:Point>
          <kml:Point>
            <kml:coordinates>1.000000,1.000000</kml:coordinates>
          </kml:Point>
        </kml:MultiGeometry>
        """

        g = MultiGeometry.from_string(doc)

        assert len(g.geometry) == 2  # type: ignore[arg-type]

    def test_multilinestring(self) -> None:
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:LineString>
            <kml:coordinates>0.000000,0.000000 1.000000,0.000000</kml:coordinates>
          </kml:LineString>
          <kml:LineString>
            <kml:coordinates>0.000000,1.000000 1.000000,1.000000</kml:coordinates>
          </kml:LineString>
        </kml:MultiGeometry>
        """

        g = MultiGeometry.from_string(doc)

        assert len(g.geometry) == 2  # type: ignore[arg-type]

    def test_multipolygon(self) -> None:
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:Polygon>
            <kml:outerBoundaryIs>
              <kml:LinearRing>
                <kml:coordinates>-1.000000,-1.000000 2.000000,-1.000000
                2.000000,2.000000 -1.000000,-1.000000</kml:coordinates>
              </kml:LinearRing>
            </kml:outerBoundaryIs>
            <kml:innerBoundaryIs>
              <kml:LinearRing>
                <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000
                0.000000,0.000000</kml:coordinates>
              </kml:LinearRing>
            </kml:innerBoundaryIs>
          </kml:Polygon>
          <kml:Polygon>
            <kml:outerBoundaryIs>
              <kml:LinearRing>
                <kml:coordinates>3.000000,0.000000 4.000000,0.000000 4.000000,1.000000
                3.000000,0.000000</kml:coordinates>
              </kml:LinearRing>
            </kml:outerBoundaryIs>
          </kml:Polygon>
        </kml:MultiGeometry>
        """

        g = MultiGeometry.from_string(doc)

        assert g.geometry is not None
        assert len(g.geometry) == 2

    def test_geometrycollection(self) -> None:
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:Polygon>
            <kml:outerBoundaryIs>
              <kml:LinearRing>
                <kml:coordinates>3,0 4,0 4,1 3,0</kml:coordinates>
              </kml:LinearRing>
            </kml:outerBoundaryIs>
          </kml:Polygon>
          <kml:Point>
            <kml:coordinates>0.000000,1.000000</kml:coordinates>
          </kml:Point>
          <kml:LineString>
            <kml:coordinates>0.000000,0.000000 1.000000,1.000000</kml:coordinates>
          </kml:LineString>
          <kml:LinearRing>
            <kml:coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,1.0 0.0,0.0</kml:coordinates>
          </kml:LinearRing>
        </kml:MultiGeometry>
        """

        g = MultiGeometry.from_string(doc)

        assert len(g.geometry) == 4  # type: ignore[arg-type]

    def test_geometrycollection_with_linearring(self) -> None:
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:LinearRing>
            <kml:coordinates>3.0,0.0 4.0,0.0 4.0,1.0 3.0,0.0</kml:coordinates>
          </kml:LinearRing>
          <kml:LinearRing>
            <kml:coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,0.0</kml:coordinates>
          </kml:LinearRing>
        </kml:MultiGeometry>
        """

        g = MultiGeometry.from_string(doc)

        assert g.geometry
        assert len(g.geometry) == 2
        assert g.geometry.geom_type == "GeometryCollection"


class TestGeometry(StdLibrary):
    """Test the _Geometry class."""

    def test_init(self) -> None:
        """Test the init method."""
        g = _Geometry()

        assert g.ns == "{http://www.opengis.net/kml/2.2}"
        assert g.target_id == ""
        assert g.id == ""
        assert g.altitude_mode is None

    def test_init_with_args(self) -> None:
        """Test the init method with arguments."""
        g = _Geometry(
            ns="",
            target_id="target_id",
            id="id",
            altitude_mode=AltitudeMode.clamp_to_ground,
        )

        assert g.ns == ""
        assert g.target_id == "target_id"
        assert g.id == "id"
        assert g.altitude_mode == AltitudeMode.clamp_to_ground

    def test_to_string(self) -> None:
        """Test the to_string method."""
        g = _Geometry()

        assert "http://www.opengis.net/kml/2.2" in g.to_string()
        assert "targetId=" not in g.to_string()
        assert "id=" not in g.to_string()
        assert "extrude" not in g.to_string()
        assert "altitudeMode" not in g.to_string()
        assert "tessellate" not in g.to_string()

    def test_to_string_with_args(self) -> None:
        """Test the to_string method."""
        g = _Geometry(
            ns="{http://www.opengis.net/kml/2.3}",
            target_id="target_id",
            id="my-id",
            extrude=True,
            altitude_mode=AltitudeMode.relative_to_ground,
            tessellate=True,
        )

        assert "http://www.opengis.net/kml/2.3" in g.to_string()
        assert 'targetId="target_id"' in g.to_string()
        assert 'id="my-id"' in g.to_string()
        assert "extrude" not in g.to_string()
        assert "altitudeMode>relativeToGround<" not in g.to_string()
        assert "tessellate" not in g.to_string()

    def test_from_string(self) -> None:
        """Test the from_string method."""
        g = _Geometry.from_string(
            '<_Geometry id="my-id" targetId="target_id" '
            'xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<altitudeMode>relativeToGround</altitudeMode>"
            "<tessellate>1</tessellate>"
            "</_Geometry>",
        )

        assert g.ns == "{http://www.opengis.net/kml/2.2}"
        assert g.target_id == "target_id"
        assert g.id == "my-id"
        assert g.altitude_mode is None
        assert not hasattr(g, "tessellate")
        assert not hasattr(g, "extrude")

    def test_from_minimal_string(self) -> None:
        g = _Geometry.from_string(
            '<_Geometry xmlns="http://www.opengis.net/kml/2.2/" />',
        )

        assert g.ns == "{http://www.opengis.net/kml/2.2}"
        assert g.target_id == ""
        assert g.id == ""
        assert g.altitude_mode is None

    def test_from_string_omitting_ns(self) -> None:
        """Test the from_string method."""
        g = _Geometry.from_string(
            '<kml:_Geometry xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="my-id" targetId="target_id">'
            "<kml:extrude>1</kml:extrude>"
            "<kml:altitudeMode>relativeToGround</kml:altitudeMode>"
            "<kml:tessellate>1</kml:tessellate>"
            "</kml:_Geometry>",
        )

        assert g.ns == "{http://www.opengis.net/kml/2.2}"
        assert g.target_id == "target_id"
        assert g.id == "my-id"
        assert g.altitude_mode is None
        assert not hasattr(g, "tessellate")
        assert not hasattr(g, "extrude")


class TestCreateKmlGeometry(StdLibrary):
    def test_create_kml_geometry_point(self) -> None:
        """Test the create_kml_geometry function."""
        g = create_kml_geometry(geo.Point(0, 1))

        assert isinstance(g, Point)
        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "Point",
            "bbox": (0.0, 1.0, 0.0, 1.0),
            "coordinates": (0.0, 1.0),
        }
        assert "Point>" in g.to_string()
        assert "coordinates>0.000000,1.000000</" in g.to_string(precision=6)

    def test_create_kml_geometry_linestring(self) -> None:
        """Test the create_kml_geometry function."""
        g = create_kml_geometry(geo.LineString([(0, 0), (1, 1)]))

        assert isinstance(g, LineString)
        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "LineString",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": ((0.0, 0.0), (1.0, 1.0)),
        }
        assert "LineString>" in g.to_string()
        assert "coordinates>0.000000,0.000000 1.000000,1.000000</" in g.to_string(
            precision=6,
        )

    def test_create_kml_geometry_linearring(self) -> None:
        """Test the create_kml_geometry function."""
        g = create_kml_geometry(geo.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)]))

        assert isinstance(g, LinearRing)
        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "LinearRing",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": ((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
        }
        assert "LinearRing>" in g.to_string()
        assert (
            "coordinates>0.000000,0.000000 1.000000,1.000000 1.000000,0.000000 "
            "0.000000,0.000000</"
        ) in g.to_string(precision=6)

    def test_create_kml_geometry_polygon(self) -> None:
        """Test the create_kml_geometry function."""
        g = create_kml_geometry(geo.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)]))

        assert isinstance(g, Polygon)
        assert g.geometry
        assert g.geometry.__geo_interface__ == {
            "type": "Polygon",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": (((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),
        }
        assert "Polygon>" in g.to_string()
        assert (
            "coordinates>0.000000,0.000000 1.000000,1.000000 1.000000,0.000000 "
            "0.000000,0.000000</"
        ) in g.to_string(precision=6)

    def test_create_kml_geometry_multipoint(self) -> None:
        """Test the create_kml_geometry function."""
        g = create_kml_geometry(geo.MultiPoint([(0, 0), (1, 1), (1, 0), (2, 2)]))

        assert isinstance(g, MultiGeometry)
        assert g.geometry
        assert len(g.geometry) == 4
        xml = g.to_string(precision=6)
        assert "MultiGeometry>" in xml
        assert "Point>" in xml
        assert "coordinates>0.000000,0.000000</" in xml
        assert "coordinates>1.000000,1.000000</" in xml
        assert "coordinates>1.000000,0.000000</" in xml
        assert "coordinates>2.000000,2.000000</" in xml

    def test_create_kml_geometry_multilinestring(self) -> None:
        """Test the create_kml_geometry function."""
        g = create_kml_geometry(
            geo.MultiLineString([[(0, 0), (1, 1)], [(0, 0), (1, 1)]]),
        )

        assert isinstance(g, MultiGeometry)
        assert g.geometry
        assert len(g.geometry) == 2
        xml = g.to_string(precision=6)
        assert "MultiGeometry>" in xml
        assert "LineString>" in xml
        assert "coordinates>0.000000,0.000000 1.000000,1.000000</" in xml
        assert "coordinates>0.000000,0.000000 1.000000,1.000000</" in xml

    def test_create_kml_geometry_multipolygon(self) -> None:
        """Test the create_kml_geometry function."""
        g = create_kml_geometry(
            geo.MultiPolygon(
                (
                    (
                        ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                        [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
                    ),
                    (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
                ),
            ),
        )

        assert isinstance(g, MultiGeometry)
        assert g.geometry
        assert len(g.geometry) == 2
        xml = g.to_string(precision=6)
        assert "MultiGeometry>" in xml
        assert "Polygon>" in xml
        assert (
            "coordinates>0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</"
        ) in xml
        assert (
            "coordinates>0.100000,0.100000 0.100000,0.200000 0.200000,0.200000 "
            "0.200000,0.100000 0.100000,0.100000</"
        ) in xml
        assert (
            "coordinates>0.000000,0.000000 0.000000,1.000000 1.000000,1.000000 "
            "1.000000,0.000000 0.000000,0.000000</"
        ) in xml

    def test_create_kml_geometry_geometrycollection(self) -> None:
        multipoint = geo.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])
        gc1 = geo.GeometryCollection([geo.Point(0, 0), multipoint])
        line1 = geo.LineString([(0, 0), (3, 1)])
        gc2 = geo.GeometryCollection([gc1, line1])
        poly1 = geo.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
        e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
        poly2 = geo.Polygon(e, [i])
        p0 = geo.Point(0, 0)
        p1 = geo.Point(-1, -1)
        ring = geo.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        line = geo.LineString([(0, 0), (1, 1)])
        gc = geo.GeometryCollection([gc2, poly1, poly2, p0, p1, ring, line])

        g = create_kml_geometry(gc)

        assert isinstance(g, MultiGeometry)
        assert g.geometry
        assert len(g.geometry) == 7
        xml = g.to_string(precision=6)
        assert "MultiGeometry>" in xml
        assert "LineString>" in xml
        assert "LinearRing>" in xml
        assert "Polygon>" in xml
        assert "outerBoundaryIs>" in xml
        assert "innerBoundaryIs>" in xml
        assert "Point>" in xml
        assert "coordinates>0.000000,0.000000</" in xml
        assert g.geometry == gc

    def test_create_kml_geometry_geometrycollection_roundtrip(self) -> None:
        multipoint = geo.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])
        gc1 = geo.GeometryCollection([geo.Point(0, 0), multipoint])
        line1 = geo.LineString([(0, 0), (3, 1)])
        gc2 = geo.GeometryCollection([line1, gc1])
        poly1 = geo.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
        e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
        poly2 = geo.Polygon(e, [i])
        p0 = geo.Point(0, 0)
        p1 = geo.Point(-1, -1)
        ring = geo.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        line = geo.LineString([(0, 0), (1, 1)])
        gc = geo.GeometryCollection(
            [
                p0,
                p1,
                line,
                poly1,
                poly2,
                ring,
                gc2,
            ],
        )
        g = create_kml_geometry(gc)

        mg = MultiGeometry.from_string(g.to_string())

        assert mg.geometry == gc

    def test_create_kml_geometry_non_geometry(self) -> None:
        """Test the create_kml_geometry function."""
        with pytest.raises(
            AttributeError,
            match="^'str' object has no attribute '__geo_interface__'$",
        ):
            create_kml_geometry("not a geometry")  # type: ignore[arg-type]


class TestGetGeometryLxml(Lxml, TestGetGeometry):
    """Test with lxml."""


class TestGeometryLxml(Lxml, TestGeometry):
    """Test with lxml."""


class TestCreateKmlGeometryLxml(Lxml, TestCreateKmlGeometry):
    """Test with lxml."""
