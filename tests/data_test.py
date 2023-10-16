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
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_schema(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"  # noqa: FS003
        pytest.raises(ValueError, kml.Schema, ns)
        s = kml.Schema(ns, "some_id")
        assert not list(s.simple_fields)
        s.append("int", "Integer", "An Integer")
        assert list(s.simple_fields)[0]["type"] == "int"
        assert list(s.simple_fields)[0]["name"] == "Integer"
        assert list(s.simple_fields)[0]["displayName"] == "An Integer"
        s.simple_fields = None
        assert not list(s.simple_fields)
        pytest.raises(TypeError, s.append, ("none", "Integer", "An Integer"))
        # pytest.raises(
        #     TypeError, s.simple_fields, ("none", "Integer", "An Integer"),
        # )
        # pytest.raises(TypeError, s.simple_fields, ("int", "Integer", "An Integer"))
        fields = {"type": "int", "name": "Integer", "display_name": "An Integer"}
        s.simple_fields = fields
        assert list(s.simple_fields)[0]["type"] == "int"
        assert list(s.simple_fields)[0]["name"] == "Integer"
        assert list(s.simple_fields)[0]["displayName"] == "An Integer"
        s.simple_fields = [["float", "Float"], fields]
        assert list(s.simple_fields)[0]["type"] == "int"
        assert list(s.simple_fields)[0]["name"] == "Integer"
        assert list(s.simple_fields)[0]["displayName"] == "An Integer"
        assert list(s.simple_fields)[1]["type"] == "float"
        assert list(s.simple_fields)[1]["name"] == "Float"
        assert list(s.simple_fields)[1]["displayName"] is None

    def test_schema_data(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"  # noqa: FS003
        pytest.raises(ValueError, data.SchemaData, ns)
        pytest.raises(ValueError, data.SchemaData, ns, "")
        sd = data.SchemaData(ns, "#default")
        sd.append_data("text", "Some Text")
        assert len(sd.data) == 1
        sd.append_data(value=1, name="Integer")
        assert len(sd.data) == 2
        assert sd.data[0] == {"value": "Some Text", "name": "text"}
        assert sd.data[1] == {"value": 1, "name": "Integer"}
        new_data = (("text", "Some new Text"), {"value": 2, "name": "Integer"})
        sd.data = new_data
        assert len(sd.data) == 2
        assert sd.data[0] == {"value": "Some new Text", "name": "text"}
        assert sd.data[1] == {"value": 2, "name": "Integer"}

    def test_untyped_extended_data(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"  # noqa: FS003
        k = kml.KML(ns=ns)

        p = kml.Placemark(ns, "id", "name", "description")
        p.extended_data = kml.ExtendedData(
            ns=ns,
            elements=[
                data.Data(ns=ns, name="info", value="so much to see"),
                data.Data(
                    ns=ns, name="weather", display_name="Weather", value="blue skies"
                ),
            ],
        )

        assert len(p.extended_data.elements) == 2
        k.append(p)

        k2 = kml.KML()
        k2.from_string(k.to_string(prettyprint=True))
        k.to_string()

        extended_data = list(k2.features())[0].extended_data
        assert extended_data is not None
        assert len(extended_data.elements), 2
        assert extended_data.elements[0].name == "info"
        assert extended_data.elements[0].value == "so much to see"
        assert extended_data.elements[0].display_name is None
        assert extended_data.elements[1].name == "weather"
        assert extended_data.elements[1].value == "blue skies"
        assert extended_data.elements[1].display_name == "Weather"

    def test_untyped_extended_data_nested(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"  # noqa: FS003
        k = kml.KML(ns=ns)

        d = kml.Document(ns, "docid", "doc name", "doc description")
        d.extended_data = kml.ExtendedData(
            ns=ns, elements=[data.Data(ns=ns, name="type", value="Document")]
        )

        f = kml.Folder(ns, "fid", "f name", "f description")
        f.extended_data = kml.ExtendedData(
            ns=ns, elements=[data.Data(ns=ns, name="type", value="Folder")]
        )

        k.append(d)
        d.append(f)

        k2 = kml.KML()
        k2.from_string(k.to_string())

        document_data = list(k2.features())[0].extended_data
        folder_data = list(list(k2.features())[0].features())[0].extended_data

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

        k = kml.KML()
        k.from_string(doc)

        extended_data = list(k.features())[0].extended_data

        assert extended_data.elements[0].name == "holeNumber"
        assert extended_data.elements[0].value == "1"
        assert "<b>This is hole </b>" in extended_data.elements[0].display_name

        assert extended_data.elements[1].name == "holePar"
        assert extended_data.elements[1].value == "4"
        assert (
            "<i>The par for this hole is </i>" in extended_data.elements[1].display_name
        )
        sd = extended_data.elements[2]
        assert sd.data[0]["name"] == "TrailHeadName"
        assert sd.data[1]["value"] == "347.45"

    def test_schema_data_from_str(self) -> None:
        doc = """<SchemaData schemaUrl="#TrailHeadTypeId">
          <SimpleData name="TrailHeadName">Pi in the sky</SimpleData>
          <SimpleData name="TrailLength">3.14159</SimpleData>
          <SimpleData name="ElevationGain">10</SimpleData>
        </SchemaData>"""

        sd = data.SchemaData(ns="", schema_url="#default")
        sd.from_string(doc)
        assert sd.schema_url == "#TrailHeadTypeId"
        assert sd.data[0] == {"name": "TrailHeadName", "value": "Pi in the sky"}
        assert sd.data[1] == {"name": "TrailLength", "value": "3.14159"}
        assert sd.data[2] == {"name": "ElevationGain", "value": "10"}
        sd1 = data.SchemaData(ns="", schema_url="#default")
        sd1.from_string(sd.to_string())
        assert sd1.schema_url == "#TrailHeadTypeId"
        assert sd.to_string() == sd1.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
