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
import pytest

from fastkml.exceptions import KMLParseError
from fastkml.geometry import AltitudeMode
from fastkml.geometry import Geometry
from fastkml.geometry import Point
from fastkml.geometry import _Geometry
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_altitude_mode(self) -> None:
        geom = Geometry()
        geom.geometry = geo.Point(0, 1)
        assert geom.altitude_mode is None
        assert "altitudeMode" not in str(geom.to_string())
        geom.altitude_mode = "unknown"
        pytest.raises(AttributeError, geom.to_string)
        geom.altitude_mode = AltitudeMode("clampToSeaFloor")
        assert "altitudeMode>clampToSeaFloor</" in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("relativeToSeaFloor")
        assert "altitudeMode>relativeToSeaFloor</" in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("clampToGround")
        assert "altitudeMode>clampToGround</" in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("relativeToGround")
        assert "altitudeMode>relativeToGround</" in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("absolute")
        assert "altitudeMode>absolute</" in str(geom.to_string())

    def test_extrude(self) -> None:
        geom = Geometry()
        assert geom.extrude is False
        geom.geometry = geo.Point(0, 1)
        geom.extrude = False
        assert "extrude" not in str(geom.to_string())
        geom.extrude = True
        geom.altitude_mode = AltitudeMode("clampToGround")
        assert "extrude" not in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("relativeToGround")
        assert "extrude>1</" in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("absolute")
        assert "extrude>1</" in str(geom.to_string())

    def test_tesselate(self) -> None:
        geom = Geometry()
        assert geom.tessellate is False
        geom.geometry = geo.LineString([(0, 0), (1, 1)])
        assert "tessellate" not in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("clampToGround")
        assert "tessellate" not in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("relativeToGround")
        assert "tessellate" not in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("absolute")
        assert "tessellate" not in str(geom.to_string())
        geom.tessellate = True
        geom.altitude_mode = None
        assert "tessellate" not in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("relativeToGround")
        assert "tessellate" not in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("absolute")
        assert "tessellate" not in str(geom.to_string())
        geom.altitude_mode = AltitudeMode("clampToGround")
        # XXX assert "tessellate>1</" in str(geom.to_string())
        # for geometries != LineString tesselate is ignored
        geom.geometry = geo.Point(0, 1)
        assert "tessellate" not in str(geom.to_string())
        geom.geometry = geo.Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])
        assert "tessellate" not in str(geom.to_string())


class TestGetGeometry(StdLibrary):
    def test_altitude_mode(self) -> None:
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:altitudeMode>clampToGround</kml:altitudeMode>
        </kml:Point>"""

        g = Geometry()
        assert g.altitude_mode is None
        g.from_string(doc)
        assert g.altitude_mode == AltitudeMode("clampToGround")

    def test_extrude(self) -> None:
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:extrude>1</kml:extrude>
        </kml:Point>"""

        g = Geometry()
        assert g.extrude is False
        g.from_string(doc)
        assert g.extrude is True

    def test_tesselate(self) -> None:
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:tessellate>1</kml:tessellate>
        </kml:Point>"""

        g = Geometry()
        assert g.tessellate is False
        g.from_string(doc)
        assert g.tessellate is True

    def test_point(self) -> None:
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
        </kml:Point>"""

        g = Geometry()
        g.from_string(doc)
        assert g.geometry.__geo_interface__ == {
            "type": "Point",
            "bbox": (0.0, 1.0, 0.0, 1.0),
            "coordinates": (0.0, 1.0),
        }

    def test_linestring(self) -> None:
        doc = """<kml:LineString xmlns:kml="http://www.opengis.net/kml/2.2">
            <kml:coordinates>0.000000,0.000000 1.000000,1.000000</kml:coordinates>
        </kml:LineString>"""

        g = Geometry()
        g.from_string(doc)
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

        g = Geometry()
        g.from_string(doc)
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

        g = Geometry()
        g.from_string(doc)
        assert g.geometry.__geo_interface__ == {
            "type": "Polygon",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": (((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)),),
        }
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

        g.from_string(doc)
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

        g = Geometry()
        g.from_string(doc)
        assert len(g.geometry) == 2

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

        g = Geometry()
        g.from_string(doc)
        assert len(g.geometry) == 2

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

        g = Geometry()
        g.from_string(doc)
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

        g = Geometry()
        g.from_string(doc)
        assert len(g.geometry) == 4
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

        g = Geometry()
        g.from_string(doc)
        assert len(g.geometry) == 2
        assert g.geometry.geom_type == "GeometryCollection"


class TestGeometry(StdLibrary):
    """Test the _Geometry class."""

    def test_init(self) -> None:
        """Test the init method."""
        g = _Geometry()

        assert g.ns == "{http://www.opengis.net/kml/2.2}"
        assert g.target_id is None
        assert g.id is None
        assert g.extrude is False
        assert g.altitude_mode is None
        assert g.tessellate is False

    def test_init_with_args(self) -> None:
        """Test the init method with arguments."""
        g = _Geometry(
            ns="",
            target_id="target_id",
            id="id",
            extrude=True,
            altitude_mode=AltitudeMode.clamp_to_ground,
            tessellate=True,
        )

        assert g.ns == ""
        assert g.target_id == "target_id"
        assert g.id == "id"
        assert g.extrude is True
        assert g.altitude_mode == AltitudeMode.clamp_to_ground
        assert g.tessellate is True

    def test_to_string(self) -> None:
        """Test the to_string method."""
        g = _Geometry()

        assert "http://www.opengis.net/kml/2.2" in g.to_string()
        assert "targetId=" not in g.to_string()
        assert "id=" not in g.to_string()
        assert "extrude>0</" in g.to_string()
        assert "altitudeMode" not in g.to_string()
        assert "tessellate>0<" in g.to_string()

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
        assert "extrude>1</" in g.to_string()
        assert "altitudeMode>relativeToGround<" in g.to_string()
        assert "tessellate>1<" in g.to_string()
        # assert not g.to_string()

    def test_from_string(self) -> None:
        """Test the from_string method."""
        g = _Geometry.class_from_string(
            '<_Geometry id="my-id" targetId="target_id">'
            "<extrude>1</extrude>"
            "<altitudeMode>relativeToGround</altitudeMode>"
            "<tessellate>1</tessellate>"
            "</_Geometry>",
            ns="",
        )

        assert g.ns == ""
        assert g.target_id == "target_id"
        assert g.id == "my-id"
        assert g.extrude is True
        assert g.altitude_mode == AltitudeMode.relative_to_ground
        assert g.tessellate is True

    def test_from_minimal_string(self) -> None:
        g = _Geometry.class_from_string(
            "<_Geometry/>",
            ns="",
        )

        assert g.ns == ""
        assert g.target_id == ""
        assert g.id == ""
        assert g.extrude is False
        assert g.altitude_mode is None
        assert g.tessellate is False

    def test_from_string_omitting_ns(self) -> None:
        """Test the from_string method."""
        g = _Geometry.class_from_string(
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
        assert g.extrude is True
        assert g.altitude_mode == AltitudeMode.relative_to_ground
        assert g.tessellate is True


class TestPoint(StdLibrary):
    """Test the Point class."""

    def test_init(self) -> None:
        """Test the init method."""
        p = geo.Point(1, 2)

        point = Point(geometry=p)

        assert point.geometry == p
        assert point.altitude_mode is None
        assert point.extrude is False

    def test_to_string(self) -> None:
        """Test the to_string method."""
        p = geo.Point(1, 2)

        point = Point(geometry=p)

        assert "Point" in point.to_string()
        assert "coordinates>1.000000,2.000000</" in point.to_string()

    def test_from_string(self) -> None:
        """Test the from_string method."""
        point = Point.class_from_string(
            '<Point xmlns="http://www.opengis.net/kml/2.2">'
            "<coordinates>1.000000,2.000000</coordinates>"
            "</Point>"
        )

        assert point.geometry == geo.Point(1, 2)
        assert point.altitude_mode is None
        assert point.extrude is False
        assert point.tessellate is False

    def test_empty_from_string(self) -> None:
        """Test the from_string method."""
        with pytest.raises(KMLParseError, match=r"Invalid coordinates in <Point\s*/>"):
            Point.class_from_string(
                "<Point/>",
                ns="",
            )

    def test_from_string_empty_coordinates(self) -> None:
        """Test the from_string method."""
        with pytest.raises(
            KMLParseError,
            match=r"Invalid coordinates in <Point\s*><coordinates\s*/></Point>",
        ):
            Point.class_from_string(
                "<Point><coordinates/></Point>",
                ns="",
            )


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""


class TestGetGeometryLxml(Lxml, TestGetGeometry):
    """Test with lxml."""


class TestGeometryLxml(Lxml, TestGeometry):
    """Test with lxml."""


class TestPointLxml(Lxml, TestPoint):
    """Test with lxml."""
