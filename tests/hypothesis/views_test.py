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

from typing import Optional

from hypothesis import given
from hypothesis import strategies as st

import fastkml
import fastkml.enums
import fastkml.views
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import lat_lon_alt_boxes
from tests.hypothesis.strategies import lods
from tests.hypothesis.strategies import nc_name

common_view = {
    "id": st.one_of(st.none(), nc_name()),
    "target_id": st.one_of(st.none(), nc_name()),
    "longitude": st.one_of(
        st.none(),
        st.floats(
            allow_nan=False,
            allow_infinity=False,
            min_value=-180,
            max_value=180,
        ).filter(lambda x: x != 0),
    ),
    "latitude": st.one_of(
        st.none(),
        st.floats(
            allow_nan=False,
            allow_infinity=False,
            min_value=-90,
            max_value=90,
        ).filter(lambda x: x != 0),
    ),
    "altitude": st.one_of(
        st.none(),
        st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != 0),
    ),
    "heading": st.one_of(
        st.none(),
        st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=360),
    ),
    "tilt": st.one_of(
        st.none(),
        st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=180),
    ),
    "altitude_mode": st.one_of(st.none(), st.sampled_from(fastkml.enums.AltitudeMode)),
}


class TestLxml(Lxml):
    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        min_lod_pixels=st.one_of(st.none(), st.integers()),
        max_lod_pixels=st.one_of(st.none(), st.integers()),
        min_fade_extent=st.one_of(st.none(), st.integers()),
        max_fade_extent=st.one_of(st.none(), st.integers()),
    )
    def test_fuzz_lod(
        self,
        id: Optional[str],
        target_id: Optional[str],
        min_lod_pixels: Optional[int],
        max_lod_pixels: Optional[int],
        min_fade_extent: Optional[int],
        max_fade_extent: Optional[int],
    ) -> None:
        lod = fastkml.views.Lod(
            id=id,
            target_id=target_id,
            min_lod_pixels=min_lod_pixels,
            max_lod_pixels=max_lod_pixels,
            min_fade_extent=min_fade_extent,
            max_fade_extent=max_fade_extent,
        )

        assert_repr_roundtrip(lod)
        assert_str_roundtrip(lod)
        assert_str_roundtrip_terse(lod)
        assert_str_roundtrip_verbose(lod)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        north=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=90),
        ),
        south=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=90),
        ),
        east=st.one_of(
            st.none(),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=0,
                max_value=180,
            ),
        ),
        west=st.one_of(
            st.none(),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=0,
                max_value=180,
            ),
        ),
        min_altitude=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != 0),
        ),
        max_altitude=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != 0),
        ),
        altitude_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.AltitudeMode)),
    )
    def test_fuzz_lat_lon_alt_box(
        self,
        id: Optional[str],
        target_id: Optional[str],
        north: Optional[float],
        south: Optional[float],
        east: Optional[float],
        west: Optional[float],
        min_altitude: Optional[float],
        max_altitude: Optional[float],
        altitude_mode: Optional[fastkml.enums.AltitudeMode],
    ) -> None:
        lat_lon_alt_box = fastkml.views.LatLonAltBox(
            id=id,
            target_id=target_id,
            north=north,
            south=south,
            east=east,
            west=west,
            min_altitude=min_altitude,
            max_altitude=max_altitude,
            altitude_mode=altitude_mode,
        )

        assert_repr_roundtrip(lat_lon_alt_box)
        assert_str_roundtrip(lat_lon_alt_box)
        assert_str_roundtrip_terse(lat_lon_alt_box)
        assert_str_roundtrip_verbose(lat_lon_alt_box)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        lat_lon_alt_box=st.one_of(st.none(), lat_lon_alt_boxes()),
        lod=st.one_of(st.none(), lods()),
    )
    def test_fuzz_region(
        self,
        id: Optional[str],
        target_id: Optional[str],
        lat_lon_alt_box: Optional[fastkml.views.LatLonAltBox],
        lod: Optional[fastkml.views.Lod],
    ) -> None:
        region = fastkml.views.Region(
            id=id,
            target_id=target_id,
            lat_lon_alt_box=lat_lon_alt_box,
            lod=lod,
        )

        assert_repr_roundtrip(region)
        assert_str_roundtrip(region)
        assert_str_roundtrip_terse(region)
        assert_str_roundtrip_verbose(region)

    @given(
        **common_view,
        roll=st.one_of(
            st.none(),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=-180,
                max_value=180,
            ).filter(lambda x: x != 0),
        ),
    )
    def test_fuzz_camera(
        self,
        id: Optional[str],
        target_id: Optional[str],
        longitude: Optional[float],
        latitude: Optional[float],
        altitude: Optional[float],
        heading: Optional[float],
        tilt: Optional[float],
        altitude_mode: Optional[fastkml.enums.AltitudeMode],
        roll: Optional[float],
    ) -> None:
        camera = fastkml.Camera(
            id=id,
            target_id=target_id,
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            heading=heading,
            tilt=tilt,
            roll=roll,
            altitude_mode=altitude_mode,
        )

        assert_repr_roundtrip(camera)
        assert_str_roundtrip(camera)
        assert_str_roundtrip_terse(camera)
        assert_str_roundtrip_verbose(camera)

    @given(
        **common_view,
        range=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != 0),
        ),
    )
    def test_fuzz_look_at(
        self,
        id: Optional[str],
        target_id: Optional[str],
        longitude: Optional[float],
        latitude: Optional[float],
        altitude: Optional[float],
        heading: Optional[float],
        tilt: Optional[float],
        altitude_mode: Optional[fastkml.enums.AltitudeMode],
        range: Optional[float],
    ) -> None:
        look_at = fastkml.LookAt(
            id=id,
            target_id=target_id,
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            heading=heading,
            tilt=tilt,
            range=range,
            altitude_mode=altitude_mode,
        )

        assert_repr_roundtrip(look_at)
        assert_str_roundtrip(look_at)
        assert_str_roundtrip_terse(look_at)
        assert_str_roundtrip_verbose(look_at)
