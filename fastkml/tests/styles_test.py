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

"""Test the styles classes."""
from typing import NoReturn

import pytest

from fastkml.tests.base import Lxml
from fastkml.tests.base import StdLibrary


@pytest.mark.skip()
class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_style_url(self) -> NoReturn:
        assert None

    def test_style_url_read(self) -> NoReturn:
        assert None

    def test_style_url_roundtrip(self) -> NoReturn:
        assert None

    def test_icon_style(self) -> NoReturn:
        assert None

    def test_icon_style_read(self) -> NoReturn:
        assert None

    def test_icon_style_roundtrip(self):
        assert None

    def test_line_style(self) -> NoReturn:
        assert None

    def test_line_style_read(self) -> NoReturn:
        assert None

    def test_line_style_roundtrip(self) -> NoReturn:
        assert None

    def test_poly_style(self) -> NoReturn:
        assert None

    def test_poly_style_read(self) -> NoReturn:
        assert None

    def test_poly_style_roundtrip(self) -> NoReturn:
        assert None

    def test_label_style(self) -> NoReturn:
        assert None

    def test_label_style_read(self) -> NoReturn:
        assert None

    def test_label_style_roundtrip(self) -> NoReturn:
        assert None

    def test_balloon_style(self) -> NoReturn:
        assert None

    def test_balloon_style_read(self) -> NoReturn:
        assert None

    def test_balloon_style_roundtrip(self) -> NoReturn:
        assert None

    def test_style(self) -> NoReturn:
        assert None

    def test_style_read(self) -> NoReturn:
        assert None

    def test_style_roundtrip(self) -> NoReturn:
        assert None

    def test_stylemap(self) -> NoReturn:
        assert None

    def test_stylemap_read(self) -> NoReturn:
        assert None

    def test_stylemap_roundtrip(self) -> NoReturn:
        assert None


@pytest.mark.skip()
class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
