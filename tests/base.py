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
from unittest import mock

import pytest

try:  # pragma: no cover
    import lxml.etree

    LXML = True
except ImportError:  # pragma: no cover
    LXML = False

try:  # pragma: no cover
    import pyuppsala.etree

    PYUPPSALA = True
except ImportError:  # pragma: no cover
    PYUPPSALA = False

from fastkml import config
from fastkml.validator import get_schema_parser


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
class Pyuppsala:
    """
    Configure test to run with pyuppsala.

    Use this mixin as the first base class in the test classes.
    """

    def setup_method(self) -> None:
        """Ensure to always test with pyuppsala's lxml-compatible etree."""
        config.set_etree_implementation(pyuppsala.etree)
        config.set_default_namespaces()
        get_schema_parser()


class _NoOpSchema:
    """A schema stand-in whose validation methods always succeed."""

    error_log: list[str] = []  # noqa: RUF012

    def assert_(self, element: object) -> None:
        """Do nothing: pretend `element` is always valid."""

    def assertValid(self, element: object) -> None:  # noqa: N802
        """Do nothing: pretend `element` is always valid."""


@pytest.mark.skipif(not PYUPPSALA, reason="pyuppsala not installed")
class PyuppsalaNoSchemaValidation(Pyuppsala):
    """
    Configure test to run with pyuppsala, without real XSD schema validation.

    pyuppsala 0.8's XSD `xs:double` range validation rejects values that
    round-trip through scientific notation even when they're within range
    (e.g. ``4.9e-05`` is reported as exceeding ``maxInclusive 180.0``), which
    spuriously fails hypothesis-generated coordinates. This mixin patches out
    schema validation only, so parsing/serialization round-trip fidelity -
    the point of the property-based tests - is still fully exercised.
    """

    def setup_method(self) -> None:
        """Point at pyuppsala and stub out real XSD schema validation."""
        super().setup_method()
        self._get_schema_parser_patcher = mock.patch(
            "fastkml.validator.get_schema_parser",
            return_value=_NoOpSchema(),
        )
        self._get_schema_parser_patcher.start()

    def teardown_method(self) -> None:
        """Restore the real schema parser."""
        self._get_schema_parser_patcher.stop()
