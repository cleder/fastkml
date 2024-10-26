# Copyright (C) 2021 - 2023 Christian Ledermann
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
"""Test the utils module."""
from fastkml import Schema
from fastkml import SchemaData
from fastkml import kml
from fastkml.utils import find_all
from tests.base import Lxml
from tests.base import StdLibrary


class TestFindAll(StdLibrary):
    """Test the find_all function."""

    def test_find_all(self) -> None:

        class A:
            def __init__(self, x: int) -> None:
                self.x = x

        class B:
            def __init__(self, y: int) -> None:
                self.y = y

        class C:
            def __init__(self, z: int) -> None:
                self.z = z

        class D:
            def __init__(self, a: A, b: B, c: C) -> None:
                self.a = a
                self.b = b
                self.c = c

        a1 = A(1)
        a2 = A(2)
        b1 = B(1)
        b2 = B(2)
        c1 = C(1)
        c2 = C(2)
        d1 = D(a1, b1, c1)
        d2 = D(a2, b2, c2)

        result = list(find_all(d1, of_type=A))
        assert result == [a1]

        result = list(find_all(d1, of_type=B))
        assert result == [b1]

        result = list(find_all(d1, of_type=C))
        assert result == [c1]

        result = list(find_all(d1, of_type=D))
        assert result == [d1]

        result = list(find_all(d1, of_type=A, x=1))
        assert result == [a1]

        result = list(find_all(d1, of_type=A, x=2))
        assert not result

        result = list(find_all(d1, of_type=A, x=1))
        assert result == [a1]

        result = list(find_all(d1, of_type=A, x=2))
        assert not result

        result = list(find_all(d1, of_type=A, x=1))
        assert result == [a1]

        result = list(find_all(d1, of_type=A, x=2))
        assert not result

        result = list(find_all(d1, of_type=A, x=1))
        assert result == [a1]

        result = list(find_all(d1, of_type=A, x=2))
        assert not result

        result = list(find_all(d1, of_type=A, x=1))
        assert result == [a1]

        result = list(find_all(d2, of_type=A, x=2))
        assert result == [a2]

    def test_find_all_empty(self) -> None:
        result = list(find_all(None, of_type=None))
        assert result == [None]

    def test_find_all_no_type(self) -> None:
        class A:
            def __init__(self, x: int) -> None:
                self.x = x

        a1 = A(1)

        result = list(find_all(a1, of_type=None))
        assert result == [a1]

    def test_find_schema_by_url(self) -> None:
        doc = (
            '<kml xmlns="http://www.opengis.net/kml/2.2">'
            "<Document>"
            "<name>ExtendedData+SchemaData</name>"
            "<open>1</open>"
            "<!-- Create a balloon template referring to the user-defined type -->"
            '<Style id="trailhead-balloon-template">'
            "<BalloonStyle>"
            "<text>"
            "<![CDATA["
            "<h2>My favorite trails!</h2>"
            "<br/><br/>"
            "The $[TrailHeadType/TrailHeadName/displayName] is "
            "<i>$[TrailHeadType/TrailHeadName]</i>."
            "The trail is $[TrailHeadType/TrailLength] miles.<br/>"
            "The climb is $[TrailHeadType/ElevationGain] meters.<br/><br/>"
            "]]>"
            "</text>"
            "</BalloonStyle>"
            "</Style>"
            '<!-- Declare the type "TrailHeadType" with 3 fields -->'
            '<Schema name="TrailHeadType" id="TrailHeadTypeId">'
            '<SimpleField type="string" name="TrailHeadName">'
            "<displayName><![CDATA[<b>Trail Head Name</b>]]></displayName>"
            "</SimpleField>"
            '<SimpleField type="double" name="TrailLength">'
            "<displayName><![CDATA[<i>The length in miles</i>]]></displayName>"
            "</SimpleField>"
            '<SimpleField type="int" name="ElevationGain">'
            "<displayName><![CDATA[<i>change in altitude</i>]]></displayName>"
            "</SimpleField>"
            "</Schema>"
            "<!-- Instantiate some Placemarks extended with TrailHeadType fields -->"
            "<Placemark>"
            "<name>Easy trail</name>"
            "<styleUrl>#trailhead-balloon-template</styleUrl>"
            "<ExtendedData>"
            '<SchemaData schemaUrl="#TrailHeadTypeId">'
            '<SimpleData name="TrailHeadName">Pi in the sky</SimpleData>'
            '<SimpleData name="TrailLength">3.14159</SimpleData>'
            '<SimpleData name="ElevationGain">10</SimpleData>'
            "</SchemaData>"
            "</ExtendedData>"
            "<Point>"
            "<coordinates>-122.000,37.002</coordinates>"
            "</Point>"
            "</Placemark>"
            "<Placemark>"
            "<name>Difficult trail</name>"
            "<styleUrl>#trailhead-balloon-template</styleUrl>"
            "<ExtendedData>"
            '<SchemaData schemaUrl="#TrailHeadTypeId">'
            '<SimpleData name="TrailHeadName">Mount Everest</SimpleData>'
            '<SimpleData name="TrailLength">347.45</SimpleData>'
            '<SimpleData name="ElevationGain">10000</SimpleData>'
            "</SchemaData>"
            "</ExtendedData>"
            "<Point>"
            "<coordinates>-121.998,37.0078</coordinates>"
            "</Point>"
            "</Placemark>"
            "</Document>"
            "</kml>"
        )
        k = kml.KML.from_string(doc, strict=False)

        schema = list(find_all(k, of_type=Schema, id="TrailHeadTypeId"))
        schema_data = list(find_all(k, of_type=SchemaData))
        assert len(schema) == 1
        assert schema[0].id == "TrailHeadTypeId"  # type: ignore[attr-defined]
        assert len(schema_data) == 2
        for data in schema_data:
            assert isinstance(data, SchemaData)
            assert data.schema_url == "#TrailHeadTypeId"


class TestFindAllLxml(Lxml):
    """Run the tests using lxml."""
