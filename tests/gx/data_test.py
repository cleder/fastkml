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
"""Test the gx.data classes."""

from typing import cast

import fastkml as kml
from fastkml.data import Schema
from fastkml.data import SchemaData
from fastkml.enums import DataType
from fastkml.gx.data import SimpleArrayData
from fastkml.gx.data import SimpleArrayField
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_simple_array_field_from_string_0(self) -> None:
        doc = (
            '<SimpleArrayField name="0" type="string">'
            "<displayName>0</displayName></SimpleArrayField>"
        )

        sf = SimpleArrayField.from_string(doc)

        assert sf.name == "0"
        assert sf.type_ == DataType("string")
        assert sf.display_name == "0"

    def test_schema(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        s = Schema(ns=ns, id="some_id")
        assert not list(s.fields)
        field = SimpleArrayField(
            name="Integer",
            type_=DataType.int_,
            display_name="An Integer",
        )
        s.append(field)
        assert s.fields[0] == field
        s.fields = []
        assert not s.fields
        fields = {
            "type_": DataType.int_,
            "name": "Integer",
            "display_name": "An Integer",
        }
        s.fields = [SimpleArrayField(**fields)]
        assert s.fields[0] == SimpleArrayField(**fields)

    def test_schema_from_string(self) -> None:
        doc = """    <Schema id="schema"
        xmlns="http://www.opengis.net/kml/2.2"
        xmlns:gx="http://www.google.com/kml/ext/2.2">
      <gx:SimpleArrayField name="heartrate" type="int">
        <displayName>Heart Rate</displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="cadence" type="int">
        <displayName>Cadence</displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="power" type="float">
        <displayName>Power</displayName>
      </gx:SimpleArrayField>
    </Schema>"""

        s = Schema.from_string(doc, ns=None)

        assert len(s.fields) == 3
        assert s.fields[0].type_ == DataType("int")
        assert s.fields[1].type_ == DataType("int")
        assert s.fields[2].type_ == DataType("float")
        assert s.fields[0].name == "heartrate"
        assert s.fields[1].name == "cadence"
        assert s.fields[2].name == "power"
        assert s.fields[0].display_name == "Heart Rate"
        assert s.fields[1].display_name == "Cadence"
        assert s.fields[2].display_name == "Power"

        s1 = Schema.from_string(s.to_string(), ns=None)
        assert len(s1.fields) == 3
        assert s1.fields[0].type_ == DataType("int")
        assert s1.fields[1].name == "cadence"
        assert s1.fields[2].display_name == "Power"
        assert s.to_string() == s1.to_string()
        doc1 = (
            '<kml xmlns="http://www.opengis.net/kml/2.2">'
            f"<Document>{doc}</Document></kml>"
        )
        k = kml.KML.from_string(doc1, ns=None)
        d = cast("kml.Document", k.features[0])
        s2 = d.schemata[0]
        assert s.to_string() == s2.to_string()
        k1 = kml.KML.from_string(k.to_string())
        assert "Schema" in k1.to_string()
        assert "SimpleArrayField" in k1.to_string()
        assert k1.to_string().replace("kml:", "").replace(
            ":kml",
            "",
        ) == k.to_string().replace("kml:", "").replace(":kml", "")

    def test_schema_data(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        sd = SchemaData(ns=ns, schema_url="#default")
        assert not sd
        sd.append_data(SimpleArrayData(data=["some", "text"], name="Some Text"))
        assert len(sd.data) == 1
        assert sd
        sd.append_data(SimpleArrayData(data=["1", "10"], name="Integer"))
        assert len(sd.data) == 2
        assert isinstance(sd.data[0], SimpleArrayData)
        assert sd.data[0].name == "Some Text"
        assert sd.data[0].data == ["some", "text"]
        assert isinstance(sd.data[1], SimpleArrayData)
        assert sd.data[1].data == ["1", "10"]
        new_data = [
            SimpleArrayData(data=["new", "text"], name="Some new Text"),
            SimpleArrayData(data=["2", "20"], name="Integer"),
        ]
        sd.data = new_data
        assert len(sd.data) == 2
        assert sd.data[0].name == "Some new Text"
        assert sd.data[0].data == ["new", "text"]
        assert sd.data[1].name == "Integer"
        assert sd.data[1].data == ["2", "20"]

    def test_schema_data_from_str(self) -> None:
        doc = """<SchemaData schemaUrl="#schema"
                  xmlns:gx="http://www.google.com/kml/ext/2.2"
                  xmlns="http://www.opengis.net/kml/2.2">
            <gx:SimpleArrayData name="cadence">
            <gx:value>86</gx:value>
            <gx:value>103</gx:value>
            </gx:SimpleArrayData>
            <gx:SimpleArrayData name="heartrate">
            <gx:value>181</gx:value>
            <gx:value>177</gx:value>
            </gx:SimpleArrayData>
            <gx:SimpleArrayData name="power">
            <gx:value>327.0</gx:value>
            <gx:value>177.0</gx:value>
            </gx:SimpleArrayData>
            </SchemaData>"""

        sd = SchemaData.from_string(doc)
        assert sd.schema_url == "#schema"
        assert isinstance(sd.data[0], SimpleArrayData)
        assert sd.data[0].name == "cadence"
        assert sd.data[0].data == ["86", "103"]
        assert isinstance(sd.data[1], SimpleArrayData)
        assert sd.data[1].name == "heartrate"
        assert sd.data[1].data == ["181", "177"]
        assert isinstance(sd.data[2], SimpleArrayData)
        assert sd.data[2].name == "power"
        assert sd.data[2].data == ["327.0", "177.0"]
        sd1 = SchemaData.from_string(sd.to_string())
        assert sd1.schema_url == "#schema"
        assert sd.to_string() == sd1.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
