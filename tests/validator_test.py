# Copyright (C) 2024  Christian Ledermann
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
"""Test the validator module."""

from pathlib import Path
from typing import Final

import pytest

from fastkml import atom
from fastkml import config
from fastkml.validator import get_schema_parser
from fastkml.validator import validate
from tests.base import Lxml
from tests.base import StdLibrary

TEST_DIR: Final = Path(__file__).parent


class TestStdLibrary(StdLibrary):
    def setup_method(self) -> None:
        """Invalidate the cache before each test."""
        get_schema_parser.cache_clear()
        super().setup_method()

    def test_validate(self) -> None:
        assert (
            validate(
                file_to_validate=TEST_DIR
                / "ogc_conformance"
                / "data"
                / "kml"
                / "Document-clean.kml",
            )
            is None
        )

    def test_validate_require_element_or_path(self) -> None:
        with pytest.raises(
            ValueError,
            match="^Either element or file_to_validate must be provided.$",
        ):
            validate()

    def test_validate_mutual_exclusive_element_and_path(self) -> None:
        with pytest.raises(
            ValueError,
            match="^Only one of element and file_to_validate can be provided.$",
        ):
            validate(
                element=atom.Link().etree_element(),
                file_to_validate=TEST_DIR / "test.xml",
            )


class TestLxml(Lxml):
    def setup_method(self) -> None:
        """Invalidate the cache before each test."""
        get_schema_parser.cache_clear()
        super().setup_method()

    def test_validate(self) -> None:
        assert validate(
            file_to_validate=TEST_DIR
            / "ogc_conformance"
            / "data"
            / "kml"
            / "Document-clean.kml",
        )

    def test_validate_element(self) -> None:
        link = atom.Link(
            ns="{http://www.w3.org/2005/Atom}",
            href="#here",
            rel="alternate",
            type="text/html",
            hreflang="en",
            title="Title",
            length=3456,
        )
        assert validate(element=link.etree_element())

    def test_validate_invalid_element(self) -> None:
        link = atom.Link(
            ns="{http://www.w3.org/2005/Atom}",
            href="",
            rel="alternate",
            type="text/html",
            hreflang="en",
            title="Title",
            length=3456,
        )

        with pytest.raises(AssertionError):
            validate(element=link.etree_element())

    def test_get_schema_parser(self) -> None:
        path = TEST_DIR / "ogc_conformance" / "data" / "atom-author-link.xsd"
        assert get_schema_parser(path)

    def test_validate_empty_element(self) -> None:
        element = config.etree.Element("kml")
        with pytest.raises(
            AssertionError,
            match=(
                "^Element 'kml': "
                "No matching global declaration available for the validation root.$"
            ),
        ):
            assert validate(element=element)
