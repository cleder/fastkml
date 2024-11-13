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
"""
Property-based tests for the times module.

These tests use the hypothesis library to generate random input for the
functions under test. The tests are run with pytest.
"""

import typing

from hypothesis import given
from hypothesis import strategies as st

import fastkml
import fastkml.enums
import fastkml.times
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import kml_datetimes
from tests.hypothesis.strategies import nc_name


class TestTimes(Lxml):
    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        timestamp=st.one_of(st.none(), kml_datetimes()),
    )
    def test_fuzz_time_stamp(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        timestamp: typing.Optional[fastkml.times.KmlDateTime],
    ) -> None:
        time_stamp = fastkml.TimeStamp(id=id, target_id=target_id, timestamp=timestamp)

        assert_repr_roundtrip(time_stamp)
        assert_str_roundtrip(time_stamp)
        assert_str_roundtrip_terse(time_stamp)
        assert_str_roundtrip_verbose(time_stamp)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        begin=st.one_of(st.none(), kml_datetimes()),
        end=st.one_of(st.none(), kml_datetimes()),
    )
    def test_fuzz_time_span(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        begin: typing.Optional[fastkml.times.KmlDateTime],
        end: typing.Optional[fastkml.times.KmlDateTime],
    ) -> None:
        time_span = fastkml.TimeSpan(id=id, target_id=target_id, begin=begin, end=end)

        assert_repr_roundtrip(time_span)
        assert_str_roundtrip(time_span)
        assert_str_roundtrip_terse(time_span)
        assert_str_roundtrip_verbose(time_span)
