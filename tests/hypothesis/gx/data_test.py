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
"""Test gx SimpleArrayData and SimpleArrayField."""

from collections.abc import Iterable
from typing import Optional

from hypothesis import given
from hypothesis import strategies as st

import fastkml
import fastkml.gx.data
import fastkml.types
from fastkml.enums import DataType
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import nc_name
from tests.hypothesis.strategies import xml_text


class TestLxml(Lxml):
    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        name=st.one_of(st.none(), xml_text()),
        data=st.one_of(st.none(), st.lists(xml_text())),
    )
    def test_fuzz_simple_array_data(
        self,
        id: Optional[str],
        target_id: Optional[str],
        name: Optional[str],
        data: Optional[Iterable[str]],
    ) -> None:
        simple_array_data = fastkml.gx.data.SimpleArrayData(
            id=id,
            target_id=target_id,
            name=name,
            data=data,
        )

        assert_repr_roundtrip(simple_array_data)
        assert_str_roundtrip(simple_array_data)
        assert_str_roundtrip_terse(simple_array_data)
        assert_str_roundtrip_verbose(simple_array_data)

    @given(
        name=st.one_of(st.none(), xml_text()),
        type_=st.one_of(st.none(), st.sampled_from(DataType)),
        display_name=st.one_of(st.none(), xml_text()),
    )
    def test_fuzz_simple_array_field(
        self,
        name: Optional[str],
        type_: Optional[DataType],
        display_name: Optional[str],
    ) -> None:
        simple_array_field = fastkml.gx.data.SimpleArrayField(
            name=name,
            type_=type_,
            display_name=display_name,
        )

        assert_repr_roundtrip(simple_array_field)
        assert_str_roundtrip(simple_array_field)
        assert_str_roundtrip_terse(simple_array_field)
        assert_str_roundtrip_verbose(simple_array_field)
