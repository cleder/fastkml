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
Round-trip the styles/ Style and StyleMap fixtures.

All five are real <kml> documents, so KML.parse() is the right entry point.
Every one of them uses an explicit `kml:` namespace prefix in the fixture,
which fastkml always re-serializes as the default (unprefixed) namespace --
that cosmetic InsertNamespace/DeleteNamespace pair shows up in every diff
below (on top of any other, genuine differences) and carries no semantic
meaning.
"""

import fastkml.kml
import fastkml.validator
from fastkml.styles import StyleMap
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR
from tests.ogc_conformance._helpers import actions
from tests.ogc_conformance._helpers import xmldiff

STYLESDIR = KMLFILEDIR / "styles"

_NAMESPACE_ONLY_DIFF = [
    actions.InsertNamespace(prefix="kml", uri="http://www.opengis.net/kml/2.2"),
    actions.DeleteNamespace(prefix=None),
]


class TestLxml(Lxml):
    """Test with lxml."""

    def test_style_map_duplicate_keys(self) -> None:
        """
        Two Pair/key elements are both "normal", which the KML spec disallows.

        Neither the XSD nor fastkml enforces "at most one Pair per key", so
        this round-trips like a valid document (modulo the namespace-prefix
        cosmetic diff).
        """
        fixture = STYLESDIR / "StyleMap-DuplicateKeys.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == _NAMESPACE_ONLY_DIFF
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_style_map_error(self) -> None:
        """
        The fixture's actual [ERROR] point: the last Pair has no terminating value.

        The "highlight" Pair contains a nested StyleMap, whose own "highlight"
        Pair has no styleUrl/Style/StyleMap at all. fastkml.styles.Pair.style
        supports a nested StyleMap, so the outer structure round-trips; the
        genuinely-empty inner Pair is dropped from serialized output because
        `Pair.__bool__()` is False when `style` is None -- documented, not a bug.
        """
        fixture = STYLESDIR / "StyleMap-Error.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert len(diff) == 5, diff
        style_map = doc.features[0].styles[0]
        assert len(style_map.pairs) == 2
        assert style_map.pairs[1].key.value == "highlight"
        nested = style_map.pairs[1].style
        assert isinstance(nested, StyleMap)
        assert len(nested.pairs) == 2
        assert nested.pairs[1].style is None, (
            "the innermost 'highlight' Pair genuinely has no style -- that's the "
            "fixture's actual [ERROR] point"
        )
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_style_map_ok(self) -> None:
        """Positive control: a well-formed StyleMap with two distinct Pair keys."""
        fixture = STYLESDIR / "StyleMap-Ok.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == _NAMESPACE_ONLY_DIFF
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_styles(self) -> None:
        """
        A single Style/LineStyle, also the target referenced by styleUrl-fileRef.xml.

        Beyond the namespace-prefix cosmetic diff, `LineStyle/width` gains a
        genuine reformat ("15" -> "15.0", fastkml always serializes width as a
        float).
        """
        fixture = STYLESDIR / "styles.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == [
            *_NAMESPACE_ONLY_DIFF,
            actions.UpdateTextIn(node="/*/*/*/*/*[2]", text="15", oldtext="15.0"),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_style_url_file_ref(self) -> None:
        """
        One Placemark's styleUrl points locally; the other at a dangling fragment.

        fastkml never resolves styleUrl targets (local or dangling) at parse
        time, so both preserve their (unresolved) value verbatim.
        """
        fixture = STYLESDIR / "styleUrl-fileRef.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == _NAMESPACE_ONLY_DIFF
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())
