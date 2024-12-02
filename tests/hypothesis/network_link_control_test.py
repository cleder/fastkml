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
"""Hypothesis tests for the fastkml.network_link_control module."""

import typing

from hypothesis import given
from hypothesis import strategies as st

import fastkml
import fastkml.enums
import fastkml.model
import fastkml.views
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import kml_datetimes
from tests.hypothesis.strategies import xml_text


class TestLxml(Lxml):
    @given(
        min_refresh_period=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != 0),
        ),
        max_session_length=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != -1),
        ),
        cookie=st.one_of(st.none(), xml_text()),
        message=st.one_of(st.none(), xml_text()),
        link_name=st.one_of(st.none(), xml_text()),
        link_description=st.one_of(st.none(), xml_text()),
        link_snippet=st.one_of(st.none(), xml_text()),
        expires=st.one_of(
            st.none(),
            kml_datetimes(),
        ),
        view=st.one_of(
            st.none(),
            st.builds(
                fastkml.views.Camera,
                longitude=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=-180,
                    max_value=180,
                ).filter(lambda x: x != 0),
                latitude=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=-90,
                    max_value=90,
                ).filter(lambda x: x != 0),
                altitude=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
            ),
            st.builds(
                fastkml.views.LookAt,
                longitude=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=-180,
                    max_value=180,
                ).filter(lambda x: x != 0),
                latitude=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=-90,
                    max_value=90,
                ).filter(lambda x: x != 0),
                altitude=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
            ),
        ),
    )
    def test_fuzz_network_link_control(
        self,
        min_refresh_period: typing.Optional[float],
        max_session_length: typing.Optional[float],
        cookie: typing.Optional[str],
        message: typing.Optional[str],
        link_name: typing.Optional[str],
        link_description: typing.Optional[str],
        link_snippet: typing.Optional[str],
        expires: typing.Optional[fastkml.KmlDateTime],
        view: typing.Union[fastkml.Camera, fastkml.LookAt, None],
    ) -> None:
        nlc = fastkml.NetworkLinkControl(
            min_refresh_period=min_refresh_period,
            max_session_length=max_session_length,
            cookie=cookie,
            message=message,
            link_name=link_name,
            link_description=link_description,
            link_snippet=link_snippet,
            expires=expires,
            view=view,
        )

        assert_repr_roundtrip(nlc)
        assert_str_roundtrip(nlc)
        assert_str_roundtrip_terse(nlc)
        assert_str_roundtrip_verbose(nlc)
