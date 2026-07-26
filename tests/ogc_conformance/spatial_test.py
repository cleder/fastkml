# Copyright (C) 2025  Christian Ledermann
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
"""
Round-trip the spatial/ geometry and view fixtures.

None of these are full <kml> documents -- each fixture's root is a bare
Placemark/LatLonAltBox/LineString/Polygon fragment -- so every test parses via
the matching element class's own from_string(), not fastkml.kml.KML.parse().
"""

import fastkml.validator
from fastkml.features import Placemark
from fastkml.geometry import LineString
from fastkml.geometry import Polygon
from fastkml.views import LatLonAltBox
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR
from tests.ogc_conformance._helpers import actions
from tests.ogc_conformance._helpers import xmldiff

SPATIALDIR = KMLFILEDIR / "spatial"


class TestLxml(Lxml):
    """Test with lxml."""

    def test_invalid_polygon_boundary(self) -> None:
        """
        [ERROR]: the Polygon's inner ring boundary lies outside its outer ring.

        A geometric-containment rule the XSD can't express and fastkml doesn't
        check. The fixture also carries an rdf:Description Metadata block
        fastkml doesn't model at all, plus a legacy `visibility` boolean
        spelled "1" instead of "true" -- both round-trip as content
        differences, pinned by count.
        """
        fixture = SPATIALDIR / "invalidPolygonBoundary.xml"
        expected = fixture.read_bytes()

        placemark = Placemark.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(placemark.to_string(), expected)

        assert len(diff) == 12, diff
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_lat_lon_alt_box_south_greater_than_north(self) -> None:
        """
        [ERROR]: south (11.0) is greater than north (10.0).

        A range/ordering rule the XSD (plain xsd:double fields) can't express;
        fastkml doesn't check it either. Round-trips byte-identical.
        """
        fixture = SPATIALDIR / "LatLonAltBox-SgtN.xml"
        expected = fixture.read_bytes()

        box = LatLonAltBox.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(box.to_string(), expected)

        assert diff == []
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_line_string_clamp_to_ground(self) -> None:
        """Positive case: LineString with explicit altitudeMode=clampToGround."""
        fixture = SPATIALDIR / "LineString-ClampToGround.xml"
        expected = fixture.read_bytes()

        line = LineString.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(line.to_string(), expected)

        assert diff == [
            actions.InsertNamespace(
                prefix=None,
                uri="http://www.opengis.net/kml/2.2",
            ),
            actions.DeleteNamespace(prefix="kml"),
            actions.UpdateTextIn(
                node="/kml:LineString/kml:coordinates[1]",
                text="-122.378009,37.830128,0 -122.377885,37.830379,0",
                oldtext="-122.378009,37.830128,0.0 -122.377885,37.830379,0.0",
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_line_string_tessellate(self) -> None:
        """Positive case: LineString relying on the default altitudeMode."""
        fixture = SPATIALDIR / "LineString-Tessellate.xml"
        expected = fixture.read_bytes()

        line = LineString.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(line.to_string(), expected)

        assert diff == [
            actions.InsertNamespace(
                prefix=None,
                uri="http://www.opengis.net/kml/2.2",
            ),
            actions.DeleteNamespace(prefix="kml"),
            actions.UpdateTextIn(
                node="/kml:LineString/kml:coordinates[1]",
                text="-122.378009,37.830128,0 -122.377885,37.830379,0",
                oldtext="-122.378009,37.830128,0.0 -122.377885,37.830379,0.0",
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_placemark_truncated_line_string(self) -> None:
        """
        [ERROR]: this LineString has only one coordinate tuple, needs at least two.

        A cardinality rule stated in the KML spec's prose; `coordinates` is
        just an xsd:string, so the XSD can't enforce it, and fastkml doesn't
        either.
        """
        fixture = SPATIALDIR / "Placemark-TruncatedLineString.xml"
        expected = fixture.read_bytes()

        placemark = Placemark.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(placemark.to_string(), expected)

        assert diff == [
            actions.InsertNamespace(
                prefix=None,
                uri="http://www.opengis.net/kml/2.2",
            ),
            actions.DeleteNamespace(prefix="kml"),
            actions.UpdateTextIn(
                node="/kml:Placemark/kml:LineString/kml:coordinates[1]",
                text="\n\t\t\t-122.378009,37.830128,0\n\t\t",
                oldtext="-122.378009,37.830128,0.0",
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_polygon_absolute(self) -> None:
        """Positive case: single-ring Polygon with altitudeMode=absolute."""
        fixture = SPATIALDIR / "Polygon-Absolute.xml"
        expected = fixture.read_bytes()

        polygon = Polygon.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(polygon.to_string(), expected)

        assert len(diff) == 4, diff
        assert fastkml.validator.validate(file_to_validate=fixture)
