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

"""Test the configuration options."""
import xml.etree.ElementTree
from typing import cast

import pytest

try:  # pragma: no cover
    import lxml  # noqa: F401

    LXML = True
except ImportError:  # pragma: no cover
    LXML = False

from fastkml import base
from fastkml import config
from fastkml import types


class TestStdLibrary:
    """Test the base object with the standard library."""

    def setup_method(self) -> None:
        """Always test with the same parser."""
        config.set_etree_implementation(xml.etree.ElementTree)
        config.set_default_namespaces()

    def test_to_string(self) -> None:
        obj = base._BaseObject(id="id-0")
        obj.__name__ = "test"  # type: ignore[assignment]

        assert (
            obj.to_string()
            == '<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" id="id-0" />'
        )

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
        element = cast(types.Element, config.etree.Element(config.KMLNS + "Base"))

        with pytest.raises(TypeError):
            be.from_element(element=element)

    def test_base_from_string_raises(self) -> None:
        be = base._BaseObject()

        with pytest.raises(TypeError):
            be.from_string(
                xml_string='<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" id="id-0" />'
            )


@pytest.mark.skipif(not LXML, reason="lxml not installed")
class TestLxml(TestStdLibrary):
    """Test the base object with lxml."""

    def setup_method(self) -> None:
        """Always test with the same parser."""
        config.set_etree_implementation(lxml.etree)
        config.set_default_namespaces()

    def test_to_string(self) -> None:
        obj = base._BaseObject(id="id-0")
        obj.__name__ = "test"  # type: ignore[assignment]

        assert (
            obj.to_string()
            == '<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" id="id-0"/>\n'
        )
