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

"""Base classes to run the tests both with the std library and lxml."""
import xml.etree.ElementTree as ET

import pytest

try:  # pragma: no cover
    import lxml

    LXML = True
except ImportError:  # pragma: no cover
    LXML = False

from fastkml import config
from fastkml.validate import get_schema_parser


class StdLibrary:
    """Configure test to run with the standard library."""

    def setup_method(self) -> None:
        """Ensure to always test with the standard library xml ElementTree parser."""
        config.set_etree_implementation(ET)
        config.set_default_namespaces()


@pytest.mark.skipif(not LXML, reason="lxml not installed")
class Lxml:
    """
    Configure test to run with lxml.

    Use this mixin as the first base class in the test classes.
    """

    def setup_method(self) -> None:
        """Ensure to always test with the lxml parse."""
        config.set_etree_implementation(lxml.etree)
        config.set_default_namespaces()
        get_schema_parser()
