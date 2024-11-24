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

import typing

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import points

import fastkml
import fastkml.enums
import fastkml.geometry
import fastkml.overlays
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import xy


class TestLxml(Lxml):
    @given(
        left_fov=st.one_of(st.none(), st.floats(min_value=-180, max_value=180)).filter(
            lambda x: x != 0,
        ),
        right_fov=st.one_of(st.none(), st.floats(min_value=-180, max_value=180)).filter(
            lambda x: x != 0,
        ),
        bottom_fov=st.one_of(st.none(), st.floats(min_value=-90, max_value=90)).filter(
            lambda x: x != 0,
        ),
        top_fov=st.one_of(st.none(), st.floats(min_value=-90, max_value=90)).filter(
            lambda x: x != 0,
        ),
        near=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False),
        ).filter(lambda x: x != 0),
    )
    def test_fuzz_view_volume(
        self,
        left_fov: typing.Optional[float],
        right_fov: typing.Optional[float],
        bottom_fov: typing.Optional[float],
        top_fov: typing.Optional[float],
        near: typing.Optional[float],
    ) -> None:
        view_volume = fastkml.overlays.ViewVolume(
            left_fov=left_fov,
            right_fov=right_fov,
            bottom_fov=bottom_fov,
            top_fov=top_fov,
            near=near,
        )

        assert_repr_roundtrip(view_volume)
        assert_str_roundtrip(view_volume)
        assert_str_roundtrip_terse(view_volume)
        assert_str_roundtrip_verbose(view_volume)

    @given(
        tile_size=st.one_of(st.none(), st.integers(min_value=0, max_value=2**31 - 1)),
        max_width=st.one_of(st.none(), st.integers(min_value=0, max_value=2**31 - 1)),
        max_height=st.one_of(st.none(), st.integers(min_value=0, max_value=2**31 - 1)),
        grid_origin=st.one_of(st.none(), st.sampled_from(fastkml.enums.GridOrigin)),
    )
    def test_fuzz_image_pyramid(
        self,
        tile_size: typing.Optional[int],
        max_width: typing.Optional[int],
        max_height: typing.Optional[int],
        grid_origin: typing.Optional[fastkml.enums.GridOrigin],
    ) -> None:
        image_pyramid = fastkml.overlays.ImagePyramid(
            tile_size=tile_size,
            max_width=max_width,
            max_height=max_height,
            grid_origin=grid_origin,
        )

        assert_repr_roundtrip(image_pyramid)
        assert_str_roundtrip(image_pyramid)
        assert_str_roundtrip_terse(image_pyramid)
        assert_str_roundtrip_verbose(image_pyramid)

    @given(
        north=st.one_of(
            st.none(),
            st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
        ),
        south=st.one_of(
            st.none(),
            st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
        ),
        east=st.one_of(
            st.none(),
            st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
        ),
        west=st.one_of(
            st.none(),
            st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
        ),
        rotation=st.one_of(
            st.none(),
            st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
        ),
    )
    def test_fuzz_lat_lon_box(
        self,
        north: typing.Optional[float],
        south: typing.Optional[float],
        east: typing.Optional[float],
        west: typing.Optional[float],
        rotation: typing.Optional[float],
    ) -> None:
        lat_lon_box = fastkml.overlays.LatLonBox(
            north=north,
            south=south,
            east=east,
            west=west,
            rotation=rotation,
        )

        assert_repr_roundtrip(lat_lon_box)
        assert_str_roundtrip(lat_lon_box)
        assert_str_roundtrip_terse(lat_lon_box)
        assert_str_roundtrip_verbose(lat_lon_box)

    @given(
        rotation=st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
        view_volume=st.one_of(
            st.none(),
            st.builds(
                fastkml.overlays.ViewVolume,
                left_fov=st.floats(min_value=-180, max_value=180).filter(
                    lambda x: x != 0,
                ),
                right_fov=st.floats(min_value=-180, max_value=180).filter(
                    lambda x: x != 0,
                ),
                bottom_fov=st.floats(min_value=-90, max_value=90).filter(
                    lambda x: x != 0,
                ),
                top_fov=st.floats(min_value=-90, max_value=90).filter(lambda x: x != 0),
                near=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
            ),
        ),
        image_pyramid=st.one_of(
            st.none(),
            st.builds(
                fastkml.overlays.ImagePyramid,
                tile_size=st.integers(min_value=0, max_value=2**31 - 1),
                max_width=st.integers(min_value=0, max_value=2**31 - 1),
                max_height=st.integers(min_value=0, max_value=2**31 - 1),
                grid_origin=st.sampled_from(fastkml.enums.GridOrigin),
            ),
        ),
        point=st.one_of(
            st.none(),
            st.builds(
                fastkml.geometry.Point,
                geometry=points(srs=epsg4326),
            ),
        ),
        shape=st.one_of(st.none(), st.sampled_from(fastkml.enums.Shape)),
    )
    def test_fuzz_photo_overlay(
        self,
        rotation: typing.Optional[float],
        view_volume: typing.Optional[fastkml.overlays.ViewVolume],
        image_pyramid: typing.Optional[fastkml.overlays.ImagePyramid],
        point: typing.Optional[fastkml.geometry.Point],
        shape: typing.Optional[fastkml.enums.Shape],
    ) -> None:
        photo_overlay = fastkml.overlays.PhotoOverlay(
            id="photo_overlay1",
            name="photo_overlay",
            rotation=rotation,
            image_pyramid=image_pyramid,
            view_volume=view_volume,
            point=point,
            shape=shape,
        )

        assert_repr_roundtrip(photo_overlay)
        assert_str_roundtrip(photo_overlay)
        assert_str_roundtrip_terse(photo_overlay)
        assert_str_roundtrip_verbose(photo_overlay)

    @given(
        altitude=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != 0),
        ),
        altitude_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.AltitudeMode)),
        lat_lon_box=st.one_of(
            st.none(),
            st.builds(
                fastkml.overlays.LatLonBox,
                north=st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
                south=st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
                east=st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
                west=st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
                rotation=st.floats(min_value=-180, max_value=180).filter(
                    lambda x: x != 0,
                ),
            ),
        ),
    )
    def test_fuzz_ground_overlay(
        self,
        altitude: typing.Optional[float],
        altitude_mode: typing.Optional[fastkml.enums.AltitudeMode],
        lat_lon_box: typing.Optional[fastkml.overlays.LatLonBox],
    ) -> None:
        ground_overlay = fastkml.overlays.GroundOverlay(
            id="ground_overlay1",
            name="ground_overlay",
            altitude=altitude,
            altitude_mode=altitude_mode,
            lat_lon_box=lat_lon_box,
        )

        assert_repr_roundtrip(ground_overlay)
        assert_str_roundtrip(ground_overlay)
        assert_str_roundtrip_terse(ground_overlay)
        assert_str_roundtrip_verbose(ground_overlay)

    @pytest.mark.parametrize(
        "cls",
        [
            fastkml.overlays.OverlayXY,
            fastkml.overlays.RotationXY,
            fastkml.overlays.ScreenXY,
            fastkml.overlays.Size,
        ],
    )
    @given(
        x=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        y=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        x_units=st.one_of(st.none(), st.sampled_from(fastkml.enums.Units)),
        y_units=st.one_of(st.none(), st.sampled_from(fastkml.enums.Units)),
    )
    def test_fuzz_xy(
        self,
        cls: typing.Union[
            typing.Type[fastkml.overlays.OverlayXY],
            typing.Type[fastkml.overlays.RotationXY],
            typing.Type[fastkml.overlays.ScreenXY],
            typing.Type[fastkml.overlays.Size],
        ],
        x: typing.Optional[float],
        y: typing.Optional[float],
        x_units: typing.Optional[fastkml.enums.Units],
        y_units: typing.Optional[fastkml.enums.Units],
    ) -> None:
        xy = cls(x=x, y=y, x_units=x_units, y_units=y_units)

        assert_repr_roundtrip(xy)
        assert_str_roundtrip(xy)
        assert_str_roundtrip_terse(xy)
        assert_str_roundtrip_verbose(xy)

    @given(
        overlay_xy=xy(fastkml.overlays.OverlayXY),
        screen_xy=xy(fastkml.overlays.ScreenXY),
        rotation_xy=xy(fastkml.overlays.RotationXY),
        size=xy(fastkml.overlays.Size),
        rotation=st.floats(min_value=-180, max_value=180).filter(lambda x: x != 0),
    )
    def test_screen_overlay(
        self,
        overlay_xy: typing.Optional[fastkml.overlays.OverlayXY],
        screen_xy: typing.Optional[fastkml.overlays.ScreenXY],
        rotation_xy: typing.Optional[fastkml.overlays.RotationXY],
        size: typing.Optional[fastkml.overlays.Size],
        rotation: typing.Optional[float],
    ) -> None:
        screen_overlay = fastkml.overlays.ScreenOverlay(
            id="screen_overlay1",
            name="screen_overlay",
            overlay_xy=overlay_xy,
            screen_xy=screen_xy,
            rotation_xy=rotation_xy,
            size=size,
            rotation=rotation,
        )

        assert_repr_roundtrip(screen_overlay)
        assert_str_roundtrip(screen_overlay)
        assert_str_roundtrip_terse(screen_overlay)
        assert_str_roundtrip_verbose(screen_overlay)
