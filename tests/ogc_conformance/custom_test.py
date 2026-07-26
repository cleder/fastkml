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
"""Round-trip the custom/ Data, SchemaData, and SimpleField fixtures."""

import pytest

import fastkml.kml
import fastkml.validator
from fastkml.data import Schema
from fastkml.exceptions import KMLParseError
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR
from tests.ogc_conformance._helpers import actions
from tests.ogc_conformance._helpers import xmldiff

CUSTOMDIR = KMLFILEDIR / "custom"

# Both SchemaData-Ok.xml and SchemaData-InvalidDatum.xml declare their
# SimpleFields with a namespace-prefixed type ("xsd:string"/"xsd:int"); fastkml
# parses that fine but always re-serializes the bare, unprefixed type name.
_SCHEMA_DATA_TYPE_PREFIX_DIFF = [
    actions.InsertNamespace(prefix="kml", uri="http://www.opengis.net/kml/2.2"),
    actions.DeleteNamespace(prefix=None),
    actions.UpdateAttrib(node="/*/*/*[2]/*[1]", name="type", value="xsd:string"),
    actions.UpdateAttrib(node="/*/*/*[2]/*[2]", name="type", value="xsd:int"),
]


class TestLxml(Lxml):
    """Test with lxml."""

    def test_data_duplicate(self) -> None:
        """
        Two ExtendedData/Data elements share the same @name ("holeNumber").

        Neither the XSD (Data/@name is plain xsd:string) nor fastkml checks for
        duplicate names, so this round-trips exactly like a valid document.
        """
        fixture = CUSTOMDIR / "Data-Duplicate.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == []
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_data_ok(self) -> None:
        """Positive control: three ExtendedData/Data elements with distinct names."""
        fixture = CUSTOMDIR / "Data-Ok.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == []
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_schema_data_invalid_datum(self) -> None:
        """
        Intends to test a SimpleData value ("1.234") invalid for its xsd:int field.

        fastkml never checks a SimpleData value against its field's declared
        DataType, so this parses and round-trips identically to
        SchemaData-Ok.xml -- the fixture's intended semantic check isn't (and
        structurally can't easily be) performed here.
        """
        fixture = CUSTOMDIR / "SchemaData-InvalidDatum.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == _SCHEMA_DATA_TYPE_PREFIX_DIFF
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_schema_data_ok(self) -> None:
        """
        Marked [PASS] -- SchemaData conforms to its referenced Schema.

        `SimpleField type="xsd:string"` is a namespace-prefixed DataType value;
        fastkml strips the prefix before the enum lookup, so this parses fine.
        The prefix isn't preserved on round trip (fastkml always serializes the
        bare type name), hence the UpdateAttrib diffs below.
        """
        fixture = CUSTOMDIR / "SchemaData-Ok.xml"
        expected = fixture.read_bytes()

        doc = fastkml.kml.KML.parse(fixture)
        diff = xmldiff(doc.to_string(), expected)

        assert diff == _SCHEMA_DATA_TYPE_PREFIX_DIFF
        assert fastkml.validator.validate(file_to_validate=fixture)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_schema_data_no_schema(self) -> None:
        """
        SchemaData/@schemaUrl="#schema-2" references a Schema that doesn't exist.

        fastkml never checks schemaUrl referential integrity, so this parses
        and round-trips fine; the only diff is the namespace-prefix cosmetic
        difference (fastkml always serializes the default namespace).
        """
        fixture = CUSTOMDIR / "SchemaData-NoSchema.xml"
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

    def test_schema_data_remote_schema(self) -> None:
        """
        SchemaData/@schemaUrl points to a schema on a different, remote document.

        Confirmed no network call is made -- schemaUrl is stored as an opaque
        string. Same namespace-prefix cosmetic diff as SchemaData-NoSchema.xml.
        """
        fixture = CUSTOMDIR / "SchemaData-RemoteSchema.xml"
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

    def test_simple_field_ok(self) -> None:
        """
        Filename says "-Ok"; the fixture's own comment says otherwise.

        `<!-- [ERROR] SimpleField has unsupported data type -->`, `type="boolean"`
        (KML only recognizes `bool`, not `boolean`). The root is a bare <Schema>,
        not a <kml> document, so the correct entry point is
        fastkml.data.Schema.from_string(), not KML.parse().
        """
        fixture = CUSTOMDIR / "SimpleField-Ok.xml"

        with pytest.raises(KMLParseError, match="boolean"):
            Schema.from_string(fixture.read_text(encoding="utf-8"))
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_simple_field_unsupported_type(self) -> None:
        """
        A SimpleField with `type="xs:date"`, not a type KML/fastkml recognizes.

        Bare <Schema> root -- parsed via Schema.from_string().
        """
        fixture = CUSTOMDIR / "SimpleField-UnsupportedType.xml"

        with pytest.raises(KMLParseError, match="xs:date"):
            Schema.from_string(fixture.read_text(encoding="utf-8"))
        assert fastkml.validator.validate(file_to_validate=fixture)
