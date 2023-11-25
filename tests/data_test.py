# Copyright (C) 2023  Christian Ledermann
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
"""Test the gx classes."""
import pytest

import fastkml as kml
from fastkml import data
from fastkml.enums import DataType
from fastkml.exceptions import KMLSchemaError
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_schema_requires_id(self) -> None:
        pytest.raises(KMLSchemaError, kml.Schema, "")

    def test_schema(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        s = kml.Schema(ns=ns, id="some_id")
        assert not list(s.simple_fields)
        field = data.SimpleField(
            name="Integer",
            type=DataType.int_,
            display_name="An Integer",
        )
        s.append(field)
        assert s.simple_fields[0] == field
        s.simple_fields = []
        assert not s.simple_fields
        fields = {"type": "int", "name": "Integer", "display_name": "An Integer"}
        s.simple_fields = (data.SimpleField(**fields),)
        assert s.simple_fields[0] == data.SimpleField(**fields)

    def test_schema_from_string(self) -> None:
        doc = """<Schema name="TrailHeadType" id="TrailHeadTypeId">
            <SimpleField type="string" name="TrailHeadName">
              <displayName><![CDATA[<b>Trail Head Name</b>]]></displayName>
            </SimpleField>
            <SimpleField type="double" name="TrailLength">
              <displayName><![CDATA[<i>The length in miles</i>]]></displayName>
            </SimpleField>
            <SimpleField type="int" name="ElevationGain">
              <displayName><![CDATA[<i>change in altitude</i>]]></displayName>
            </SimpleField>
          </Schema> """

        s = kml.Schema.class_from_string(doc, ns="")
        assert len(s.simple_fields) == 3
        assert s.simple_fields[0].type == DataType("string")
        assert s.simple_fields[1].type == DataType("double")
        assert s.simple_fields[2].type == DataType("int")
        assert s.simple_fields[0].name == "TrailHeadName"
        assert s.simple_fields[1].name == "TrailLength"
        assert s.simple_fields[2].name == "ElevationGain"
        assert s.simple_fields[0].display_name == "<b>Trail Head Name</b>"
        assert s.simple_fields[1].display_name == "<i>The length in miles</i>"
        assert s.simple_fields[2].display_name == "<i>change in altitude</i>"
        s1 = kml.Schema.class_from_string(s.to_string(), ns="")
        assert len(s1.simple_fields) == 3
        assert s1.simple_fields[0].type == DataType("string")
        assert s1.simple_fields[1].name == "TrailLength"
        assert s1.simple_fields[2].display_name == "<i>change in altitude</i>"
        assert s.to_string() == s1.to_string()
        doc1 = f"<kml><Document>{doc}</Document></kml>"
        k = kml.KML.class_from_string(doc1, ns="")
        d = next(iter(k.features()))
        s2 = next(iter(d.schemata()))
        # s.ns = config.KMLNS
        assert s.to_string() == s2.to_string()
        k1 = kml.KML.class_from_string(k.to_string())
        assert "Schema" in k1.to_string()
        assert "SimpleField" in k1.to_string()
        assert k1.to_string().replace("kml:", "").replace(
            ":kml",
            "",
        ) == k.to_string().replace("kml:", "").replace(":kml", "")

    def test_schema_data(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        pytest.raises(ValueError, data.SchemaData, ns)
        pytest.raises(ValueError, data.SchemaData, ns, "")
        sd = data.SchemaData(ns=ns, schema_url="#default")
        sd.append_data(data.SimpleData("text", "Some Text"))
        assert len(sd.data) == 1
        sd.append_data(data.SimpleData(value=1, name="Integer"))
        assert len(sd.data) == 2
        assert sd.data[0] == data.SimpleData(value="Some Text", name="text")
        assert sd.data[1] == data.SimpleData(value=1, name="Integer")
        new_data = (
            data.SimpleData("text", "Some new Text"),
            data.SimpleData(value=2, name="Integer"),
        )
        sd.data = new_data
        assert len(sd.data) == 2
        assert sd.data[0].name == "text"
        assert sd.data[0].value == "Some new Text"
        assert sd.data[1].name == "Integer"
        assert sd.data[1].value == 2

    def test_untyped_extended_data(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        k = kml.KML(ns=ns)

        p = kml.Placemark(ns, id="id", name="name", description="description")
        p.extended_data = kml.ExtendedData(
            ns=ns,
            elements=[
                data.Data(ns=ns, name="info", value="so much to see"),
                data.Data(
                    ns=ns,
                    name="weather",
                    display_name="Weather",
                    value="blue skies",
                ),
            ],
        )

        assert len(p.extended_data.elements) == 2
        k.append(p)

        k2 = kml.KML.class_from_string(k.to_string(prettyprint=True))
        k.to_string()

        extended_data = next(iter(k2.features())).extended_data
        assert extended_data is not None
        assert len(extended_data.elements), 2
        assert extended_data.elements[0].name == "info"
        assert extended_data.elements[0].value == "so much to see"
        assert extended_data.elements[0].display_name is None
        assert extended_data.elements[1].name == "weather"
        assert extended_data.elements[1].value == "blue skies"
        assert extended_data.elements[1].display_name == "Weather"

    def test_untyped_extended_data_nested(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        k = kml.KML(ns=ns)

        d = kml.Document(ns, id="docid", name="doc name", description="doc description")
        d.extended_data = kml.ExtendedData(
            ns=ns,
            elements=[data.Data(ns=ns, name="type", value="Document")],
        )

        f = kml.Folder(ns, id="fid", name="f name", description="f description")
        f.extended_data = kml.ExtendedData(
            ns=ns,
            elements=[data.Data(ns=ns, name="type", value="Folder")],
        )

        k.append(d)
        d.append(f)

        k2 = kml.KML.class_from_string(k.to_string())

        document_data = next(iter(k2.features())).extended_data
        folder_data = next(iter(next(iter(k2.features())).features())).extended_data

        assert document_data.elements[0].name == "type"
        assert document_data.elements[0].value == "Document"

        assert folder_data.elements[0].name == "type"
        assert folder_data.elements[0].value == "Folder"

    def test_extended_data(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
          <Placemark>
            <name>Simple placemark</name>
            <description></description>
            <Point>
              <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
            </Point>
            <ExtendedData>
              <Data name="holeNumber">
                <displayName><![CDATA[
                    <b>This is hole </b>
                ]]></displayName>
                <value>1</value>
              </Data>
              <Data name="holePar">
                <displayName><![CDATA[
                  <i>The par for this hole is </i>
                ]]></displayName>
                <value>4</value>
              </Data>
              <SchemaData schemaUrl="#TrailHeadTypeId">
                <SimpleData name="TrailHeadName">Mount Everest</SimpleData>
                <SimpleData name="TrailLength">347.45</SimpleData>
                <SimpleData name="ElevationGain">10000</SimpleData>
              </SchemaData>
            </ExtendedData>
          </Placemark>
        </kml>"""

        k = kml.KML.class_from_string(doc)

        extended_data = next(iter(k.features())).extended_data

        assert extended_data.elements[0].name == "holeNumber"
        assert extended_data.elements[0].value == "1"
        assert "<b>This is hole </b>" in extended_data.elements[0].display_name

        assert extended_data.elements[1].name == "holePar"
        assert extended_data.elements[1].value == "4"
        assert (
            "<i>The par for this hole is </i>" in extended_data.elements[1].display_name
        )
        sd = extended_data.elements[2]
        assert sd.data[0] == data.SimpleData(
            name="TrailHeadName",
            value="Mount Everest",
        )
        assert sd.data[1] == data.SimpleData(name="TrailLength", value="347.45")
        assert sd.data[2] == data.SimpleData(name="ElevationGain", value="10000")

    def test_schema_data_from_str(self) -> None:
        doc = """<SchemaData schemaUrl="#TrailHeadTypeId">
          <SimpleData name="TrailHeadName">Pi in the sky</SimpleData>
          <SimpleData name="TrailLength">3.14159</SimpleData>
          <SimpleData name="ElevationGain">10</SimpleData>
        </SchemaData>"""

        sd = data.SchemaData.class_from_string(doc, ns="")
        assert sd.schema_url == "#TrailHeadTypeId"
        assert sd.data[0].name == "TrailHeadName"
        assert sd.data[0].value == "Pi in the sky"
        assert sd.data[1].name == "TrailLength"
        assert sd.data[1].value == "3.14159"
        assert sd.data[2].name == "ElevationGain"
        assert sd.data[2].value == "10"
        sd1 = data.SchemaData.class_from_string(sd.to_string(), ns="")
        assert sd1.schema_url == "#TrailHeadTypeId"
        assert sd.to_string() == sd1.to_string()

    def test_data_from_string(self) -> None:
        doc = """<Data name="holeNumber">
          <displayName><![CDATA[
              <b>This is hole </b>
          ]]></displayName>
          <value>1</value>
        </Data>"""

        d = data.Data.class_from_string(doc, ns="")
        assert d.name == "holeNumber"
        assert d.value == "1"
        assert "<b>This is hole </b>" in d.display_name
        d1 = data.Data.class_from_string(d.to_string(), ns="")
        assert d1.name == "holeNumber"
        assert d.to_string() == d1.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
