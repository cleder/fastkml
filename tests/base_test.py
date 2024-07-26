# Copyright (C) 2021 - 2024  Christian Ledermann
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

"""Test the base classes."""


from fastkml import base
from fastkml import kml_base
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test the base object with the standard library."""

    def test_to_string(self) -> None:
        obj = kml_base._BaseObject(id="id-0", target_id="target-id-0")

        assert obj.to_string() == (
            '<kml:_BaseObject xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-0" targetId="target-id-0" />'
        )

    def test_str(self) -> None:
        obj = kml_base._BaseObject(id="id-0", target_id="target-id-0")
        assert str(obj) == obj.to_string()

    def test_custom_kwargs(self) -> None:
        obj = kml_base._BaseObject(
            id="id-0",
            target_id="target-id-0",
            custom="custom",
            altkw=2,
        )

        assert obj.custom == "custom"
        assert obj.altkw == 2

    def test_custom_kwargs_splat(self) -> None:
        obj = kml_base._BaseObject(
            id="id-0",
            target_id="target-id-0",
            custom="custom",
            altkw=2,
        )

        assert obj._get_splat() == {"custom": "custom", "altkw": 2}

    def test_eq(self) -> None:
        obj1 = kml_base._BaseObject(id="id-0", target_id="target-id-0")
        obj2 = kml_base._BaseObject(id="id-0", target_id="target-id-0")
        assert obj1 == obj2

    def test_ne(self) -> None:
        obj1 = kml_base._BaseObject(id="id-0", target_id="target-id-0")
        obj2 = kml_base._BaseObject(id="id-1", target_id="target-id-0")
        assert obj1 != obj2

    def test_ne_basexml(self) -> None:
        obj1 = object()
        obj2 = base._XMLObject()
        assert obj1 != obj2

    def test_ne_basexml_2(self) -> None:
        obj1 = base._XMLObject()
        obj2 = kml_base._BaseObject()
        assert obj1 != obj2

    def test_to_str_empty_ns(self) -> None:
        obj = kml_base._BaseObject(ns="", id="id-0", target_id="target-id-0")

        assert obj.to_string().replace(" ", "").replace(
            "\n",
            "",
        ) == '<_BaseObject id="id-0" targetId="target-id-0" />'.replace(" ", "")

    def test_from_string(self) -> None:
        be = kml_base._BaseObject.class_from_string(
            string=(
                '<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" '
                'id="id-0" targetId="target-id-0" />'
            ),
        )
        assert be.id == "id-0"
        assert be.target_id == "target-id-0"

    def test_from_string_attr_ns_prefix(self) -> None:
        be = kml_base._BaseObject.class_from_string(
            string=(
                '<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" '
                'kml:id="id-0" kml:targetId="target-id-0" />'
            ),
        )
        assert be.id == "id-0"
        assert be.target_id == "target-id-0"

    def test_base_class_from_string(self) -> None:
        be = kml_base._BaseObject.class_from_string(
            '<test id="id-0" targetId="td-00" />',
        )

        assert be.id == "id-0"
        assert be.target_id == "td-00"
        assert be.ns == "{http://www.opengis.net/kml/2.2}"

    def test_base_class_from_empty_string(self) -> None:
        be = kml_base._BaseObject.class_from_string("<test/>")

        assert be.id == ""
        assert be.target_id == ""
        assert be.ns == "{http://www.opengis.net/kml/2.2}"

    def test_xml_object_roundtrip(self) -> None:
        obj = base._XMLObject()
        obj2 = base._XMLObject.class_from_string(obj.to_string(), ns="")

        assert obj == obj2
        assert str(obj) == obj2.to_string()
        assert repr(obj) == repr(obj2)

    def test_base_object_roundtrip(self) -> None:
        obj = kml_base._BaseObject(id="id-0", target_id="target-id-0")

        obj2 = kml_base._BaseObject.class_from_string(obj.to_string())

        assert obj == obj2
        assert str(obj) == obj2.to_string()
        assert repr(obj) == repr(obj2)


class TestLxml(Lxml, TestStdLibrary):
    """Test the base object with lxml."""

    def test_to_string(self) -> None:
        obj = kml_base._BaseObject(id="id-0")

        assert obj.to_string() == (
            '<kml:_BaseObject xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-0"/>\n'
        )

    def test_from_string(self) -> None:
        be = kml_base._BaseObject.class_from_string(
            string=(
                '<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" '
                'id="id-0" targetId="target-id-0"/>\n'
            ),
        )

        assert be.id == "id-0"
        assert be.target_id == "target-id-0"
