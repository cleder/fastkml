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

import pytest

try:
    import lxml

    LXML = True
except ImportError:
    LXML = False

from fastkml import config


def test_set_etree_implementation_xml() -> None:
    config.set_etree_implementation(xml.etree.ElementTree)

    assert config.etree.__name__ == "xml.etree.ElementTree"


@pytest.mark.skipif(not LXML, reason="lxml not installed")
def test_set_etree_implementation_lxml() -> None:
    config.set_etree_implementation(lxml.etree)

    assert config.etree.__name__ == "lxml.etree"


def test_register_namespaces() -> None:
    """Register namespaces for use in etree."""
    config.set_etree_implementation(xml.etree.ElementTree)
    ns = {
        "real_person": "http://people.example.com",
        "role": "http://characters.example.com",
    }

    config.register_namespaces(**ns)

    for k, v in ns.items():
        assert config.etree._namespace_map[v] == k


def test_default_registered_namespaces() -> None:
    assert {
        "kml": "http://www.opengis.net/kml/2.2",
        "atom": "http://www.w3.org/2005/Atom",
        "gx": "http://www.google.com/kml/ext/2.2",
    } == config.DEFAULT_NAME_SPACES


def test_set_default_namespaces() -> None:
    """Set the default namespaces."""
    config.set_etree_implementation(xml.etree.ElementTree)
    config.etree._namespace_map = {}

    config.set_default_namespaces()

    for k, v in config.DEFAULT_NAME_SPACES.items():
        assert config.etree._namespace_map[v] == k
