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
"""Test gx SimpleArrayData."""

import typing

from hypothesis import given
from hypothesis import strategies as st

import fastkml
import fastkml.gx_data
import fastkml.types
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import nc_name
from tests.hypothesis.strategies import xml_text


class TestGx(Lxml):
    @given(
        name=st.one_of(st.none(), nc_name()),
        data=st.one_of(
            st.none(),
            st.lists(xml_text().filter(lambda x: x.strip() != "")),
        ),
    )
    def test_fuzz_simple_array_data(
        self,
        name: typing.Optional[str],
        data: typing.Optional[typing.Iterable[str]],
    ) -> None:
        simple_array_data = fastkml.gx_data.SimpleArrayData(
            name=name,
            data=data,
        )

        assert_repr_roundtrip(simple_array_data)
        assert_str_roundtrip(simple_array_data)
        assert_str_roundtrip_terse(simple_array_data)
        assert_str_roundtrip_verbose(simple_array_data)
