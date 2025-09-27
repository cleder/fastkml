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
"""Test Link and Icon."""

import string
from typing import Optional
from typing import Union

import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.enums
from fastkml.validator import validate
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import nc_name
from tests.hypothesis.strategies import query_strings

common_link = {
    "id": st.one_of(st.none(), nc_name()),
    "target_id": st.one_of(st.none(), nc_name()),
    "href": st.one_of(st.none(), urls()),
    "refresh_mode": st.one_of(st.none(), st.sampled_from(fastkml.enums.RefreshMode)),
    "refresh_interval": st.one_of(
        st.none(),
        st.floats(allow_infinity=False, allow_nan=False),
    ),
    "view_refresh_mode": st.one_of(
        st.none(),
        st.sampled_from(fastkml.enums.ViewRefreshMode),
    ),
    "view_refresh_time": st.one_of(
        st.none(),
        st.floats(allow_infinity=False, allow_nan=False),
    ),
    "view_bound_scale": st.one_of(
        st.none(),
        st.floats(allow_infinity=False, allow_nan=False),
    ),
    "view_format": st.one_of(
        st.none(),
        st.text(string.ascii_letters + string.punctuation),
    ),
    "http_query": st.one_of(st.none(), query_strings()),
}


class TestLxml(Lxml):
    @pytest.mark.parametrize("cls", [fastkml.Link, fastkml.Icon])
    @given(**common_link)
    def test_fuzz_link(
        self,
        cls: Union[type[fastkml.Link], type[fastkml.Icon]],
        id: Optional[str],
        target_id: Optional[str],
        href: Optional[str],
        refresh_mode: Optional[fastkml.enums.RefreshMode],
        refresh_interval: Optional[float],
        view_refresh_mode: Optional[fastkml.enums.ViewRefreshMode],
        view_refresh_time: Optional[float],
        view_bound_scale: Optional[float],
        view_format: Optional[str],
        http_query: Optional[str],
    ) -> None:
        link = cls(
            id=id,
            target_id=target_id,
            href=href,
            refresh_mode=refresh_mode,
            refresh_interval=refresh_interval,
            view_refresh_mode=view_refresh_mode,
            view_refresh_time=view_refresh_time,
            view_bound_scale=view_bound_scale,
            view_format=view_format,
            http_query=http_query,
        )
        assert validate(element=link.etree_element())
        assert_repr_roundtrip(link)
        assert_str_roundtrip(link)
        assert_str_roundtrip_terse(link)
        assert_str_roundtrip_verbose(link)
