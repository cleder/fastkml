# Copyright (C) 2021  Christian Ledermann
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
from typing import cast

import pytest

from fastkml import base
from fastkml import config
from fastkml import types
from fastkml.tests.base import Lxml
from fastkml.tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test the base object with the standard library."""

    def test_to_string(self) -> None:
        obj = base._BaseObject(id="id-0", target_id="target-id-0")
        obj.__name__ = "test"

        assert (
            obj.to_string()
            == '<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" id="id-0" targetId="target-id-0" />'
        )

    def test_from_string(self) -> None:
        be = base._BaseObject()
        be.__name__ = "test"

        be.from_string(
            xml_string='<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" id="id-0" targetId="target-id-0" />'
        )

        assert be.id == "id-0"
        assert be.target_id == "target-id-0"

    def test_base_etree_element_raises(self) -> None:
        be = base._BaseObject()

        with pytest.raises(NotImplementedError):
            be.etree_element()

    def test_base_etree_element_raises_subclass(self) -> None:
        class Test(base._BaseObject):
            pass

        with pytest.raises(NotImplementedError):
            Test().etree_element()

    def test_base_from_element_raises(self) -> None:
        be = base._BaseObject()
        element = cast(types.Element, config.etree.Element(config.KMLNS + "Base"))  # type: ignore[attr-defined]

        with pytest.raises(TypeError):
            be.from_element(element=element)

    def test_base_from_string_raises(self) -> None:
        be = base._BaseObject()

        with pytest.raises(TypeError):
            be.from_string(
                xml_string='<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" id="id-0" />'
            )


class TestLxml(Lxml, TestStdLibrary):
    """Test the base object with lxml."""

    def test_to_string(self) -> None:
        obj = base._BaseObject(id="id-0")
        obj.__name__ = "test"

        assert (
            obj.to_string()
            == '<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" id="id-0"/>\n'
        )

    def test_from_string(self) -> None:
        be = base._BaseObject()
        be.__name__ = "test"

        be.from_string(
            xml_string='<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" id="id-0" targetId="target-id-0"/>\n'
        )

        assert be.id == "id-0"
        assert be.target_id == "target-id-0"
