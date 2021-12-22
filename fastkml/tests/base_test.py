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

try:
    import lxml  # noqa: F401

    LXML = True
except ImportError:
    LXML = False

from fastkml import base
from fastkml import config


def test_to_string_xml():
    config.set_etree_implementation(xml.etree.ElementTree)
    config.set_default_namespaces()
    obj = base._BaseObject()
    obj.__name__ = "test"

    assert obj.to_string() == '<kml:test xmlns:kml="http://www.opengis.net/kml/2.2" />'
