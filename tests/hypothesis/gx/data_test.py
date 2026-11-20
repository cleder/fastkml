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

from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

import fastkml
import fastkml.gx.data
import fastkml.types
from fastkml.enums import DataType
from tests.base import Lxml
from tests.base import PyuppsalaNoSchemaValidation
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
        id: str | None,
        target_id: str | None,
        name: str | None,
        data: Iterable[str] | None,
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
        name: str | None,
        type_: DataType | None,
        display_name: str | None,
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


class TestPyuppsala(PyuppsalaNoSchemaValidation, TestLxml):
    # Reusing `TestLxml`'s hypothesis-wrapped test methods (rather than
    # duplicating their `@given` strategies and bodies) makes hypothesis flag
    # `HealthCheck.differing_executors`, since the same underlying test
    # function is now invoked from two classes. That's exactly what's
    # happening here, deliberately, so it's suppressed rather than avoided.
    test_fuzz_simple_array_data = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_simple_array_data)
    test_fuzz_simple_array_field = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_simple_array_field)
