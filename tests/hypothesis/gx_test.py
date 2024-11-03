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
"""Test gx Track and MultiTrack."""
import datetime
import typing

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.dateutil import timezones
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import points

import fastkml
import fastkml.enums
import fastkml.gx
import fastkml.types
from fastkml.gx import Angle
from fastkml.gx import TrackItem
from fastkml.times import KmlDateTime
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import nc_name

track_items = st.builds(
    TrackItem,
    angle=st.one_of(
        st.one_of(
            st.builds(Angle),
            st.builds(
                Angle,
                heading=st.floats(allow_nan=False, allow_infinity=False),
                roll=st.floats(allow_nan=False, allow_infinity=False),
                tilt=st.floats(allow_nan=False, allow_infinity=False),
            ),
        ),
    ),
    coord=points(srs=epsg4326),
    when=st.builds(
        KmlDateTime,
        dt=st.datetimes(
            allow_imaginary=False,
            timezones=timezones(),
            min_value=datetime.datetime(2000, 1, 1),  # noqa: DTZ001
            max_value=datetime.datetime(2050, 1, 1),  # noqa: DTZ001
        ),
    ),
)


class TestGx(Lxml):

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        altitude_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.AltitudeMode)),
        track_items=st.one_of(
            st.none(),
            st.lists(
                track_items,
                max_size=1,
            ),
        ),
    )
    def test_fuzz_track_track_items(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        altitude_mode: typing.Optional[fastkml.enums.AltitudeMode],
        track_items: typing.Optional[typing.Iterable[fastkml.gx.TrackItem]],
    ) -> None:
        track = fastkml.gx.Track(
            id=id,
            target_id=target_id,
            altitude_mode=altitude_mode,
            track_items=track_items,
        )

        assert_repr_roundtrip(track)
        assert_str_roundtrip(track)
        assert_str_roundtrip_terse(track)
        assert_str_roundtrip_verbose(track)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        altitude_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.AltitudeMode)),
        tracks=st.one_of(
            st.none(),
            st.lists(
                st.builds(
                    fastkml.gx.Track,
                    altitude_mode=st.one_of(
                        st.none(),
                        st.sampled_from(fastkml.enums.AltitudeMode),
                    ),
                    track_items=st.one_of(
                        st.none(),
                        st.lists(
                            track_items,
                            max_size=1,
                        ),
                    ),
                ),
                max_size=1,
            ),
        ),
        interpolate=st.one_of(st.none(), st.booleans()),
    )
    def test_fuzz_multi_track(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        altitude_mode: typing.Optional[fastkml.enums.AltitudeMode],
        tracks: typing.Optional[typing.Iterable[fastkml.gx.Track]],
        interpolate: typing.Optional[bool],
    ) -> None:
        multi_track = fastkml.gx.MultiTrack(
            id=id,
            target_id=target_id,
            altitude_mode=altitude_mode,
            tracks=tracks,
            interpolate=interpolate,
        )

        assert_repr_roundtrip(multi_track)
        assert_str_roundtrip(multi_track)
        assert_str_roundtrip_terse(multi_track)
        assert_str_roundtrip_verbose(multi_track)
