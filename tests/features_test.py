# Copyright (C) 2021 -2023  Christian Ledermann
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

"""Test the kml classes."""
import pytest

from fastkml import features
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_feature_base(self) -> None:
        f = features._Feature(name="A Feature")
        pytest.raises(NotImplementedError, f.etree_element)
        assert f.name == "A Feature"
        assert f.visibility is None
        assert f.isopen is None
        assert f._atom_author is None
        assert f._atom_link is None
        assert f.address is None
        # self.assertEqual(f.phoneNumber, None)
        assert f._snippet is None
        assert f.description is None
        assert f._style_url is None
        assert f._styles == []
        assert f._times is None
        # self.assertEqual(f.region, None)
        # self.assertEqual(f.extended_data, None)

        f.__name__ = "Feature"
        f.style_url = "#default"
        assert "Feature>" in str(f.to_string())
        assert "#default" in str(f.to_string())

    def test_address_string(self) -> None:
        f = features._Feature()
        address = "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA"
        f.address = address
        assert f.address == address

    def test_address_none(self) -> None:
        f = features._Feature()
        f.address = None
        assert f.address is None

    def test_phone_number_string(self) -> None:
        f = features._Feature()
        f.phone_number = "+1-234-567-8901"
        assert f.phone_number == "+1-234-567-8901"

    def test_phone_number_none(self) -> None:
        f = features._Feature()
        f.phone_number = None
        assert f.phone_number is None


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
