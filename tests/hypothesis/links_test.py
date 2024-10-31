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
import typing

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.enums
from fastkml.validate import validate
from tests.base import Lxml
from tests.hypothesis.common import nc_name
from tests.hypothesis.common import query_strings


class TestLxml(Lxml):
    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        href=st.one_of(st.none(), urls()),
        refresh_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.RefreshMode)),
        refresh_interval=st.one_of(
            st.none(),
            st.floats(allow_infinity=False, allow_nan=False),
        ),
        view_refresh_mode=st.one_of(
            st.none(),
            st.sampled_from(fastkml.enums.ViewRefreshMode),
        ),
        view_refresh_time=st.one_of(
            st.none(),
            st.floats(allow_infinity=False, allow_nan=False),
        ),
        view_bound_scale=st.one_of(
            st.none(),
            st.floats(allow_infinity=False, allow_nan=False),
        ),
        view_format=st.one_of(
            st.none(),
            st.text(string.ascii_letters + string.punctuation),
        ),
        http_query=st.one_of(st.none(), query_strings()),
    )
    @settings(deadline=None)
    def test_fuzz_link(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        href: typing.Optional[str],
        refresh_mode: typing.Optional[fastkml.enums.RefreshMode],
        refresh_interval: typing.Optional[float],
        view_refresh_mode: typing.Optional[fastkml.enums.ViewRefreshMode],
        view_refresh_time: typing.Optional[float],
        view_bound_scale: typing.Optional[float],
        view_format: typing.Optional[str],
        http_query: typing.Optional[str],
    ) -> None:
        link = fastkml.Link(
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
