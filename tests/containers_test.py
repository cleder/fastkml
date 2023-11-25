# Copyright (C) 2021 - 2023 Christian Ledermann
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

from fastkml import containers
from fastkml import features
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_container_base(self) -> None:
        f = containers._Container(name="A Container")
        # apparently you can add documents to containes
        # d = kml.Document()
        # self.assertRaises(TypeError, f.append, d)
        p = features.Placemark()
        f.append(p)
        pytest.raises(NotImplementedError, f.etree_element)


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
