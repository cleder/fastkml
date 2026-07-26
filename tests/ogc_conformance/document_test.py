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
Round-trip the top-level, full <kml> documents in the OGC conformance suite.

For each fixture: parse with fastkml.kml.KML.parse(), reproduce it with
to_string(), and diff against the original bytes. Where the diff isn't empty,
the count/content is pinned as a regression baseline rather than asserted as
an aspirational `== []` -- see the module docstrings in this package's other
test files for why fastkml doesn't (and can't, via XSD alone) always achieve a
byte-identical round trip.
"""

import pytest
from xmldiff import actions

import fastkml.kml
import fastkml.validator
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR
from tests.ogc_conformance._helpers import xmldiff


class TestLxml(Lxml):
    """Test with lxml."""

    def test_document_clean(self) -> None:
        """
        A rich document using NetworkLinkControl, atom:author, xal:AddressDetails.

        fastkml doesn't model xal:AddressDetails or the kml root's arbitrary `hint`
        attribute, and reorders/reformats some content, so the diff is pinned by
        action count rather than asserted empty.
        """
        clean_doc = KMLFILEDIR / "Document-clean.kml"
        expected = clean_doc.read_bytes()

        doc = fastkml.kml.KML.parse(clean_doc)
        diff = xmldiff(doc.to_string(), expected)

        assert len(diff) == 103, diff
        assert fastkml.validator.validate(file_to_validate=clean_doc)
        # fastkml serializes NetworkLinkControl after the root feature, but the
        # XSD's KmlType requires it first -- fastkml's own round-trip output for
        # this file is not itself schema-valid. Known limitation, pinned here.
        with pytest.raises(AssertionError, match="NetworkLinkControl"):
            fastkml.validator.validate(element=doc.etree_element())

    def test_document_deprecated(self) -> None:
        """Same content as Document-clean.kml, using KML 2.0-era deprecated tags."""
        deprecated_doc = KMLFILEDIR / "Document-deprecated.kml"
        expected = deprecated_doc.read_bytes()

        doc = fastkml.kml.KML.parse(deprecated_doc)
        diff = xmldiff(doc.to_string(), expected)

        assert len(diff) == 9, diff
        assert fastkml.validator.validate(file_to_validate=deprecated_doc)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_document_places(self) -> None:
        """
        Two simple Placemarks with a 0.00 altitude.

        fastkml's coordinate serializer always strips trailing zeros ("0.00" ->
        "0"), so this can never be a byte-identical round trip regardless of the
        `precision` passed to to_string() -- pinned as the (small) expected diff.
        """
        places_doc = KMLFILEDIR / "Document-places.kml"
        expected = places_doc.read_bytes()

        doc = fastkml.kml.KML.parse(places_doc)
        diff = xmldiff(doc.to_string(precision=2), expected)

        assert diff == [
            actions.UpdateTextIn(
                node="/*/*/*[1]/*[2]/*[1]",
                text="-95.44,40.42,0",
                oldtext="-95.44,40.42,0.00",
            ),
            actions.UpdateTextIn(
                node="/*/*/*[2]/*[2]/*[1]",
                text="-95.43,40.42,0",
                oldtext="-95.43,40.42,0.00",
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=places_doc)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_document_kml_samples(self) -> None:
        """
        The bundled OGC "KML Samples" showcase document.

        Exercises a wide swath of the format (schemas, styles, overlays, models,
        gx tracks); pinned by action count -- almost entirely int/float text
        reformatting ("2" -> "2.0") plus an unmodeled xsi:schemaLocation attribute.
        """
        kml_samples_doc = KMLFILEDIR / "KML_Samples.kml"
        expected = kml_samples_doc.read_bytes()

        doc = fastkml.kml.KML.parse(kml_samples_doc)
        diff = xmldiff(doc.to_string(), expected)

        assert len(diff) == 94, diff
        assert fastkml.validator.validate(file_to_validate=kml_samples_doc)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_empty_placemark_without_id(self) -> None:
        """A minimal, empty Placemark with no id -- round-trips byte-identical."""
        empty_placemark = KMLFILEDIR / "emptyPlacemarkWithoutId.xml"
        expected = empty_placemark.read_bytes()

        doc = fastkml.kml.KML.parse(empty_placemark)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == []
        assert fastkml.validator.validate(file_to_validate=empty_placemark)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_model_relative_target(self) -> None:
        """
        A Placemark with a Model geometry, nested two Documents deep.

        Pinned diff is just int->float Location coordinate reformatting
        ("1" -> "1.0").
        """
        model_doc = KMLFILEDIR / "models" / "model_relative_target.kml"
        expected = model_doc.read_bytes()

        doc = fastkml.kml.KML.parse(model_doc)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == [
            actions.UpdateTextIn(
                node="/*/*/*/*[2]/*/*[2]/*[1]",
                text="1",
                oldtext="1.0",
            ),
            actions.UpdateTextIn(
                node="/*/*/*/*[2]/*/*[2]/*[2]",
                text="1",
                oldtext="1.0",
            ),
            actions.UpdateTextIn(
                node="/*/*/*/*[2]/*/*[2]/*[3]",
                text="1",
                oldtext="1.0",
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=model_doc)
        assert fastkml.validator.validate(element=doc.etree_element())
