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

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.enums
import fastkml.links
import fastkml.styles
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import kml_colors
from tests.hypothesis.strategies import nc_name
from tests.hypothesis.strategies import xml_text


class TestLxml(Lxml):
    @given(
        url=st.one_of(st.none(), urls()),
    )
    def test_fuzz_style_url(
        self,
        url: typing.Optional[str],
    ) -> None:
        style_url = fastkml.StyleUrl(
            url=url,
        )

        assert_repr_roundtrip(style_url)
        assert_str_roundtrip(style_url)
        assert_str_roundtrip_terse(style_url)
        assert_str_roundtrip_verbose(style_url)

    @given(
        x=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        y=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        xunits=st.one_of(st.none(), st.sampled_from(fastkml.enums.Units)),
        yunits=st.one_of(st.none(), st.sampled_from(fastkml.enums.Units)),
    )
    def test_fuzz_hot_spot(
        self,
        x: typing.Optional[float],
        y: typing.Optional[float],
        xunits: typing.Optional[fastkml.enums.Units],
        yunits: typing.Optional[fastkml.enums.Units],
    ) -> None:
        hot_spot = fastkml.styles.HotSpot(
            x=x,
            y=y,
            xunits=xunits,
            yunits=yunits,
        )

        assert_repr_roundtrip(hot_spot)
        assert_str_roundtrip(hot_spot)
        assert_str_roundtrip_terse(hot_spot)
        assert_str_roundtrip_verbose(hot_spot)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        color=st.one_of(st.none(), kml_colors()),
        color_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.ColorMode)),
        scale=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        heading=st.one_of(
            st.none(),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=0,
                max_value=360,
            ),
        ),
        icon=st.one_of(
            st.none(),
            st.builds(
                fastkml.links.Icon,
                href=urls(),
            ),
        ),
        hot_spot=st.one_of(
            st.none(),
            st.builds(
                fastkml.styles.HotSpot,
                x=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
                xunits=st.one_of(st.none(), st.sampled_from(fastkml.enums.Units)),
                y=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
                yunits=st.one_of(st.none(), st.sampled_from(fastkml.enums.Units)),
            ),
        ),
    )
    def test_fuzz_icon_style(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        color: typing.Optional[str],
        color_mode: typing.Optional[fastkml.enums.ColorMode],
        scale: typing.Optional[float],
        heading: typing.Optional[float],
        icon: typing.Optional[fastkml.links.Icon],
        hot_spot: typing.Optional[fastkml.styles.HotSpot],
    ) -> None:
        icon_style = fastkml.IconStyle(
            id=id,
            target_id=target_id,
            color=color,
            color_mode=color_mode,
            scale=scale,
            heading=heading,
            icon=icon,
            hot_spot=hot_spot,
        )

        assert_repr_roundtrip(icon_style)
        assert_str_roundtrip(icon_style)
        assert_str_roundtrip_terse(icon_style)
        # the IconStyle does only allow for simple Icons, thats why
        # assert_str_roundtrip_verbose fails at this time

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        color=st.one_of(st.none(), kml_colors()),
        color_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.ColorMode)),
        width=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False, min_value=0),
        ),
    )
    def test_fuzz_line_style(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        color: typing.Optional[str],
        color_mode: typing.Optional[fastkml.enums.ColorMode],
        width: typing.Optional[float],
    ) -> None:
        line_style = fastkml.LineStyle(
            id=id,
            target_id=target_id,
            color=color,
            color_mode=color_mode,
            width=width,
        )

        assert_repr_roundtrip(line_style)
        assert_str_roundtrip(line_style)
        assert_str_roundtrip_terse(line_style)
        assert_str_roundtrip_verbose(line_style)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        color=st.one_of(st.none(), kml_colors()),
        color_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.ColorMode)),
        fill=st.one_of(st.none(), st.booleans()),
        outline=st.one_of(st.none(), st.booleans()),
    )
    def test_fuzz_poly_style(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        color: typing.Optional[str],
        color_mode: typing.Optional[fastkml.enums.ColorMode],
        fill: typing.Optional[bool],
        outline: typing.Optional[bool],
    ) -> None:
        poly_style = fastkml.PolyStyle(
            id=id,
            target_id=target_id,
            color=color,
            color_mode=color_mode,
            fill=fill,
            outline=outline,
        )

        assert_repr_roundtrip(poly_style)
        assert_str_roundtrip(poly_style)
        assert_str_roundtrip_terse(poly_style)
        assert_str_roundtrip_verbose(poly_style)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        color=st.one_of(st.none(), kml_colors()),
        color_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.ColorMode)),
        scale=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False, min_value=0),
        ),
    )
    def test_fuzz_label_style(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        color: typing.Optional[str],
        color_mode: typing.Optional[fastkml.enums.ColorMode],
        scale: typing.Optional[float],
    ) -> None:
        label_style = fastkml.LabelStyle(
            id=id,
            target_id=target_id,
            color=color,
            color_mode=color_mode,
            scale=scale,
        )

        assert_repr_roundtrip(label_style)
        assert_str_roundtrip(label_style)
        assert_str_roundtrip_terse(label_style)
        assert_str_roundtrip_verbose(label_style)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        bg_color=st.one_of(st.none(), kml_colors()),
        text_color=st.one_of(st.none(), kml_colors()),
        text=st.one_of(st.none(), xml_text()),
        display_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.DisplayMode)),
    )
    def test_fuzz_balloon_style(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        bg_color: typing.Optional[str],
        text_color: typing.Optional[str],
        text: typing.Optional[str],
        display_mode: typing.Optional[fastkml.enums.DisplayMode],
    ) -> None:
        balloon_style = fastkml.BalloonStyle(
            id=id,
            target_id=target_id,
            bg_color=bg_color,
            text_color=text_color,
            text=text,
            display_mode=display_mode,
        )

        assert_repr_roundtrip(balloon_style)
        assert_str_roundtrip(balloon_style)
        assert_str_roundtrip_terse(balloon_style)
        assert_str_roundtrip_verbose(balloon_style)
