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
"""Round-trip the features/ Folder, Placemark, and PhotoOverlay fixtures."""

import fastkml.kml
import fastkml.validator
from fastkml.overlays import PhotoOverlay
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR
from tests.ogc_conformance._helpers import actions
from tests.ogc_conformance._helpers import xmldiff

FEATURESDIR = KMLFILEDIR / "features"


class TestLxml(Lxml):
    """Test with lxml."""

    def test_folder_empty(self) -> None:
        """An empty Folder at document top level is legal, byte-identical round trip."""
        fixture = FEATURESDIR / "Folder-Empty.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == []
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_placemark_author(self) -> None:
        """A Placemark with atom:author/atom:name/atom:uri -- a valid extension."""
        fixture = FEATURESDIR / "Placemark-Author.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == [
            actions.InsertNamespace(
                prefix="atom",
                uri="http://www.w3.org/2005/Atom",
            ),
            actions.UpdateTextIn(
                node="/*/*/*[2]/*[2]/*[1]",
                text="-90.86948943473118,48.25450093195546,0",
                oldtext="-90.86948943473118,48.25450093195546,0.0",
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_photo_overlay_href_params_without_image_pyramid(self) -> None:
        """
        [ERROR]: Icon/href has tiling params ($[level]/$[x]/$[y]) but no ImagePyramid.

        A semantic rule the KML spec states in prose; the XSD can't express it
        and fastkml doesn't enforce it. The root is a bare `kml:PhotoOverlay`,
        not a <kml> document -- fastkml.kml.KML.parse() would silently drop the
        content, so the correct entry point is PhotoOverlay.from_string().
        Round-trips clean.
        """
        fixture = FEATURESDIR / "PhotoOverlay-HrefParamsWithoutImagePyramid.xml"
        expected = fixture.read_bytes()

        overlay = PhotoOverlay.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(overlay.to_string(), expected)

        assert diff == []
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_photo_overlay_not_image(self) -> None:
        """
        Icon/href points at "NotImage-...png" -- fastkml never inspects href targets.

        Bare `kml:PhotoOverlay` root, parsed via PhotoOverlay.from_string().
        Round-trips clean.
        """
        fixture = FEATURESDIR / "PhotoOverlay-NotImage.xml"
        expected = fixture.read_bytes()

        overlay = PhotoOverlay.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(overlay.to_string(), expected)

        assert diff == []
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_photo_overlay_pyramid_without_href(self) -> None:
        """
        [ERROR]: ImagePyramid is present but Icon has no href -- both are empty.

        `<Icon />` and `<ImagePyramid />` are empty elements; fastkml's __bool__
        convention (see docs/contributing.rst) treats content-less elements as
        falsy and omits them from serialized output, so they're missing from
        the round trip -- documented, not a bug.
        """
        fixture = FEATURESDIR / "PhotoOverlay-PyramidWithoutHref.xml"
        expected = fixture.read_bytes()

        overlay = PhotoOverlay.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(overlay.to_string(), expected)

        assert diff == [
            actions.InsertNode(
                target="/kml:PhotoOverlay[1]",
                tag="{http://www.opengis.net/kml/2.2}Icon",
                position=0,
            ),
            actions.InsertNode(
                target="/kml:PhotoOverlay[1]",
                tag="{http://www.opengis.net/kml/2.2}ImagePyramid",
                position=1,
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_photo_overlay(self) -> None:
        """Positive case: Icon/href with tiling params + a matching ImagePyramid."""
        fixture = FEATURESDIR / "PhotoOverlay.xml"
        expected = fixture.read_bytes()

        overlay = PhotoOverlay.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(overlay.to_string(), expected)

        assert diff == []
        assert fastkml.validator.validate(file_to_validate=fixture)
