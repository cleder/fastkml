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

from collections.abc import Iterable
from functools import partial

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.data
import fastkml.enums
import fastkml.gx.data
from tests.base import Lxml
from tests.base import PyUppsala
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
    type_=st.sampled_from(fastkml.enums.DataType),
    display_name=xml_text().filter(lambda x: x.strip() != ""),
)
simple_array_fields = partial(
    st.builds,
    fastkml.gx.data.SimpleArrayField,
    name=xml_text().filter(lambda x: x.strip() != ""),
    type_=st.sampled_from(fastkml.enums.DataType),
    display_name=xml_text().filter(lambda x: x.strip() != ""),
)
simple_data = partial(
    st.builds,
    fastkml.data.SimpleData,
    name=xml_text().filter(lambda x: x.strip() != ""),
    value=xml_text().filter(lambda x: x.strip() != ""),
)
simple_array_data = partial(
    st.builds,
    fastkml.gx.data.SimpleArrayData,
    name=xml_text().filter(lambda x: x.strip() != ""),
    data=st.lists(xml_text().filter(lambda x: x.strip() != ""), min_size=1),
)


class _Tests:
    @given(
        name=st.one_of(st.none(), xml_text()),
        type_=st.one_of(st.none(), st.sampled_from(fastkml.enums.DataType)),
        display_name=st.one_of(st.none(), xml_text()),
    )
    def test_fuzz_simple_field(
        self,
        name: str | None,
        type_: fastkml.enums.DataType | None,
        display_name: str | None,
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
        array_fields=st.one_of(st.none(), st.lists(simple_array_fields())),
    )
    def test_fuzz_schema(
        self,
        id: str | None,
        name: str | None,
        fields: Iterable[fastkml.data.SimpleField] | None,
        array_fields: Iterable[fastkml.gx.data.SimpleArrayField] | None,
    ) -> None:
        schema = fastkml.Schema(
            id=id,
            name=name,
            fields=fields,
            array_fields=array_fields,
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
        id: str | None,
        target_id: str | None,
        name: str | None,
        value: str | None,
        display_name: str | None,
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
        value=st.one_of(st.none(), xml_text()),
    )
    def test_fuzz_simple_data(
        self,
        name: str | None,
        value: str | None,
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
        data=st.one_of(st.none(), st.lists(simple_data())),
        array_data=st.one_of(st.none(), st.lists(simple_array_data())),
    )
    def test_fuzz_schema_data(
        self,
        id: str | None,
        target_id: str | None,
        schema_url: str | None,
        data: Iterable[fastkml.data.SimpleData] | None,
        array_data: Iterable[fastkml.gx.data.SimpleArrayData] | None,
    ) -> None:
        schema_data = fastkml.SchemaData(
            id=id,
            target_id=target_id,
            schema_url=schema_url,
            data=data,
            array_data=array_data,
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
                        data=st.one_of(st.none(), st.lists(simple_data())),
                        array_data=st.one_of(st.none(), st.lists(simple_array_data())),
                    ),
                ),
            ),
        ),
    )
    def test_fuzz_extended_data(
        self,
        elements: Iterable[fastkml.Data | fastkml.SchemaData] | None,
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


class TestLxml(Lxml, _Tests):
    """Test with lxml."""


class TestPyUppsala(PyUppsala, _Tests):
    """Test with pyuppsala."""
