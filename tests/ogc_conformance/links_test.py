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
Round-trip the links/ GroundOverlay, Link, NetworkLink, and Update fixtures.

Only Update-NoTarget.xml and Update-Placemark.xml are real <kml> documents;
the rest are bare fragments, parsed via the matching element class's own
from_string(). None of these fixtures' href/targetHref values are ever
dereferenced over the network by fastkml -- confirmed by inspecting
fastkml/links.py, fastkml/network_link_control.py, and fastkml/features.py
(href is stored as a plain string), and by timing a live run against each of
the real/remote URLs below.
"""

import pytest
from xmldiff import actions

import fastkml.kml
import fastkml.validator
from fastkml.features import NetworkLink
from fastkml.links import Link
from fastkml.overlays import GroundOverlay
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR
from tests.ogc_conformance._helpers import xmldiff

LINKSDIR = KMLFILEDIR / "links"


class TestLxml(Lxml):
    """Test with lxml."""

    def test_ground_overlay_http_ref(self) -> None:
        """Positive case: GroundOverlay Icon/href is a full https:// URL."""
        fixture = LINKSDIR / "GroundOverlay-httpRef.xml"
        expected = fixture.read_bytes()

        overlay = GroundOverlay.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(overlay.to_string(), expected)

        assert len(diff) == 5, diff
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_link_bad_http_query(self) -> None:
        """
        [ERROR]: httpQuery's value doesn't use a recognized KML substitution param.

        (e.g. [clientVersion]) -- a vocabulary rule fastkml doesn't check,
        since it stores http_query as an opaque string.
        """
        fixture = LINKSDIR / "Link-BadHttpQuery.xml"
        expected = fixture.read_bytes()

        link = Link.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(link.to_string(), expected)

        assert len(diff) == 5, diff
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_link(self) -> None:
        """
        Positive case (id="Link-Ok"), despite a comment second-guessing refreshMode.

        The comment says refreshMode should arguably be "onInterval" given
        refreshInterval is set, but fastkml has no cross-field validation for
        Link, so that note doesn't affect parsing either way.
        """
        fixture = LINKSDIR / "Link.xml"
        expected = fixture.read_bytes()

        link = Link.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(link.to_string(), expected)

        assert len(diff) == 5, diff
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_network_link_not_found(self) -> None:
        """
        NetworkLink/Link/href points at a URL that returns 404.

        A resource-existence check fastkml can't perform since it never
        dereferences href.
        """
        fixture = LINKSDIR / "NetworkLink-NotFound.xml"
        expected = fixture.read_bytes()

        link = NetworkLink.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(link.to_string(), expected)

        assert diff == [
            actions.InsertNamespace(
                prefix=None,
                uri="http://www.opengis.net/kml/2.2",
            ),
            actions.DeleteNamespace(prefix="kml"),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_network_link_relative_ref(self) -> None:
        """Positive case: NetworkLink/Link/href is a relative path."""
        fixture = LINKSDIR / "NetworkLink-relativeRef.xml"
        expected = fixture.read_bytes()

        link = NetworkLink.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(link.to_string(), expected)

        assert diff == [
            actions.InsertNamespace(
                prefix=None,
                uri="http://www.opengis.net/kml/2.2",
            ),
            actions.DeleteNamespace(prefix="kml"),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_update_no_target(self) -> None:
        """
        [ERROR]: Update/targetHref points at a file that doesn't exist.

        A file-existence check fastkml can't perform (no filesystem access);
        the round trip is otherwise byte-identical (namespace-prefix cosmetic
        diff only).
        """
        fixture = LINKSDIR / "Update-NoTarget.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == [
            actions.InsertNamespace(
                prefix="kml",
                uri="http://www.opengis.net/kml/2.2",
            ),
            actions.DeleteNamespace(prefix=None),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_update_placemark(self) -> None:
        """
        Marked [PASS], but the fixture itself has an unrelated defect.

        Update/targetHref refers to a valid KML resource, with a
        Change/Placemark patch -- but the inner `<name>` element is
        unprefixed with no default xmlns declared, so it lands in the empty
        namespace and fails schema validation. This documents that fixture
        bug, not evidence fastkml validates Update/Change semantics.
        """
        fixture = LINKSDIR / "Update-Placemark.xml"

        with pytest.raises(AssertionError, match="Element 'name'"):
            fastkml.kml.KML.parse(fixture)
        with pytest.raises(AssertionError, match="Element 'name'"):
            fastkml.validator.validate(file_to_validate=fixture)
