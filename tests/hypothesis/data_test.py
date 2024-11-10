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
"""Property-based tests for the views module."""

import typing
from functools import partial

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.data
import fastkml.enums
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import nc_name
from tests.hypothesis.strategies import xml_text

simple_fields = partial(
    st.builds,
    fastkml.data.SimpleField,
    name=xml_text().filter(lambda x: x.strip() != ""),
    type_=st.one_of(st.sampled_from(fastkml.enums.DataType)),
    display_name=xml_text().filter(lambda x: x.strip() != ""),
)


class TestLxml(Lxml):
    @given(
        name=st.one_of(st.none(), xml_text()),
        type_=st.one_of(st.sampled_from(fastkml.enums.DataType)),
        display_name=st.one_of(st.none(), xml_text()),
    )
    def test_fuzz_simple_field(
        self,
        name: typing.Optional[str],
        type_: typing.Optional[fastkml.enums.DataType],
        display_name: typing.Optional[str],
    ) -> None:
        simple_field = fastkml.data.SimpleField(
            name=name,
            type_=type_,
            display_name=display_name,
        )

        assert_str_roundtrip(simple_field)
        assert_repr_roundtrip(simple_field)
        assert_str_roundtrip_terse(simple_field)
        assert_str_roundtrip_verbose(simple_field)

    @given(
        id=nc_name(),
        name=st.one_of(st.none(), xml_text()),
        fields=st.one_of(st.none(), st.lists(simple_fields())),
    )
    def test_fuzz_schema(
        self,
        id: typing.Optional[str],
        name: typing.Optional[str],
        fields: typing.Optional[typing.Iterable[fastkml.data.SimpleField]],
    ) -> None:
        schema = fastkml.Schema(
            id=id,
            name=name,
            fields=fields,
        )

        assert_str_roundtrip(schema)
        assert_repr_roundtrip(schema)
        assert_str_roundtrip_terse(schema)
        assert_str_roundtrip_verbose(schema)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        name=st.one_of(st.none(), xml_text()),
        value=xml_text().filter(lambda x: x.strip() != ""),
        display_name=st.one_of(st.none(), xml_text()),
    )
    def test_fuzz_data(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        name: typing.Optional[str],
        value: typing.Optional[str],
        display_name: typing.Optional[str],
    ) -> None:
        data = fastkml.Data(
            id=id,
            target_id=target_id,
            name=name,
            value=value,
            display_name=display_name,
        )

        assert_str_roundtrip(data)
        assert_repr_roundtrip(data)
        assert_str_roundtrip_terse(data)
        assert_str_roundtrip_verbose(data)

    @given(
        name=xml_text().filter(lambda x: x.strip() != ""),
        value=xml_text().filter(lambda x: x.strip() != ""),
    )
    def test_fuzz_simple_data(
        self,
        name: typing.Optional[str],
        value: typing.Optional[str],
    ) -> None:
        simple_data = fastkml.data.SimpleData(
            name=name,
            value=value,
        )

        assert_str_roundtrip(simple_data)
        assert_repr_roundtrip(simple_data)
        assert_str_roundtrip_terse(simple_data)
        assert_str_roundtrip_verbose(simple_data)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        schema_url=st.one_of(st.none(), urls()),
        data=st.one_of(
            st.none(),
            st.lists(
                st.builds(
                    fastkml.data.SimpleData,
                    name=xml_text().filter(lambda x: x.strip() != ""),
                    value=xml_text().filter(lambda x: x.strip() != ""),
                ),
            ),
        ),
    )
    def test_fuzz_schema_data(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        schema_url: typing.Optional[str],
        data: typing.Optional[typing.Iterable[fastkml.data.SimpleData]],
    ) -> None:
        schema_data = fastkml.SchemaData(
            id=id,
            target_id=target_id,
            schema_url=schema_url,
            data=data,
        )

        assert_str_roundtrip(schema_data)
        assert_repr_roundtrip(schema_data)
        assert_str_roundtrip_terse(schema_data)
        assert_str_roundtrip_verbose(schema_data)

    @given(
        elements=st.one_of(
            st.none(),
            st.lists(
                st.one_of(
                    st.builds(
                        fastkml.data.Data,
                        name=xml_text().filter(lambda x: x.strip() != ""),
                        value=xml_text().filter(lambda x: x.strip() != ""),
                        display_name=st.one_of(st.none(), xml_text()),
                    ),
                    st.builds(
                        fastkml.SchemaData,
                        schema_url=st.one_of(st.none(), urls()),
                        data=st.lists(
                            st.builds(
                                fastkml.data.SimpleData,
                                name=xml_text().filter(lambda x: x.strip() != ""),
                                value=xml_text().filter(lambda x: x.strip() != ""),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
    def test_fuzz_extended_data(
        self,
        elements: typing.Optional[
            typing.Iterable[typing.Union[fastkml.Data, fastkml.SchemaData]]
        ],
    ) -> None:
        extended_data = fastkml.ExtendedData(
            elements=(
                sorted(elements, key=lambda t: t.__class__.__name__)
                if elements
                else None
            ),
        )

        assert_repr_roundtrip(extended_data)
        assert_str_roundtrip(extended_data)
        assert_str_roundtrip_terse(extended_data)
        assert_str_roundtrip_verbose(extended_data)
