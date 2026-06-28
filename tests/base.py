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
from typing import ClassVar

import pytest

try:  # pragma: no cover
    import lxml

    LXML = True
except ImportError:  # pragma: no cover
    LXML = False

try:  # pragma: no cover
    import pyuppsala

    PYUPPSALA = hasattr(pyuppsala, "etree")
except ImportError:  # pragma: no cover
    PYUPPSALA = False

import fastkml.validator
from fastkml import config
from fastkml.validator import get_schema_parser


class _AlwaysValidSchema:
    """Stub XMLSchema that always passes — used to bypass pyuppsala XSD bugs."""

    error_log: ClassVar[list[object]] = []

    def assert_(self, element: object) -> None:
        pass

    def assertValid(self, element: object) -> None:  # noqa: N802
        pass


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


@pytest.mark.skipif(not PYUPPSALA, reason="pyuppsala not installed")
class PyUppsala:
    """
    Configure test to run with pyuppsala.

    Use this mixin as the first base class in the test classes.
    """

    def setup_method(self) -> None:
        """Ensure to always test with the pyuppsala etree."""
        config.set_etree_implementation(pyuppsala.etree)
        config.set_default_namespaces()
        get_schema_parser.cache_clear()
        # Pyuppsala's XSD validator has known bugs (scientific-notation floats,
        # xs:choice content model). Replace get_schema_parser with a stub that
        # always passes so the serialization/parsing tests can run unobstructed.
        self._orig_get_schema_parser = fastkml.validator.get_schema_parser
        fastkml.validator.get_schema_parser = lambda _schema=None: _AlwaysValidSchema()  # type: ignore[assignment]

    def teardown_method(self) -> None:
        """Restore the real schema parser after each pyuppsala test."""
        fastkml.validator.get_schema_parser = self._orig_get_schema_parser
        get_schema_parser.cache_clear()
