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
"""Hypothesis tests for the fastkml.model module."""

import typing

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.enums
import fastkml.links
import fastkml.model
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import nc_name


class TestLxml(Lxml):
    @given(
        altitude=st.one_of(
            st.none(),
            st.just(0.0),
            st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != 0),
        ),
        latitude=st.one_of(
            st.none(),
            st.just(0.0),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=-90,
                max_value=90,
            ),
        ),
        longitude=st.one_of(
            st.none(),
            st.just(0.0),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=-180,
                max_value=180,
            ),
        ),
    )
    def test_fuzz_location(
        self,
        altitude: typing.Optional[float],
        latitude: typing.Optional[float],
        longitude: typing.Optional[float],
    ) -> None:
        location = fastkml.model.Location(
            altitude=altitude,
            latitude=latitude,
            longitude=longitude,
        )

        assert_repr_roundtrip(location)
        assert_str_roundtrip(location)
        assert_str_roundtrip_terse(location)
        assert_str_roundtrip_verbose(location)

    @given(
        heading=st.one_of(
            st.none(),
            st.just(0.0),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=-360,
                max_value=360,
            ).filter(lambda x: x != 0),
        ),
        tilt=st.one_of(
            st.none(),
            st.just(0.0),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=0,
                max_value=180,
            ).filter(lambda x: x != 0),
        ),
        roll=st.one_of(
            st.none(),
            st.just(0.0),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=-180,
                max_value=180,
            ).filter(lambda x: x != 0),
        ),
    )
    def test_fuzz_orientation(
        self,
        heading: typing.Optional[float],
        tilt: typing.Optional[float],
        roll: typing.Optional[float],
    ) -> None:
        orientation = fastkml.model.Orientation(heading=heading, tilt=tilt, roll=roll)

        assert_repr_roundtrip(orientation)
        assert_str_roundtrip(orientation)
        assert_str_roundtrip_terse(orientation)
        assert_str_roundtrip_verbose(orientation)

    @given(
        x=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        y=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        z=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
    )
    def test_fuzz_scale(
        self,
        x: typing.Optional[float],
        y: typing.Optional[float],
        z: typing.Optional[float],
    ) -> None:
        scale = fastkml.model.Scale(x=x, y=y, z=z)

        assert_repr_roundtrip(scale)
        assert_str_roundtrip(scale)
        assert_str_roundtrip_terse(scale)
        assert_str_roundtrip_verbose(scale)

    @given(
        target_href=st.one_of(st.none(), urls()),
        source_href=st.one_of(st.none(), urls()),
    )
    def test_fuzz_alias(
        self,
        target_href: typing.Optional[str],
        source_href: typing.Optional[str],
    ) -> None:
        alias = fastkml.model.Alias(target_href=target_href, source_href=source_href)

        assert_repr_roundtrip(alias)
        assert_str_roundtrip(alias)
        assert_str_roundtrip_terse(alias)
        assert_str_roundtrip_verbose(alias)

    @given(
        aliases=st.one_of(
            st.none(),
            st.lists(
                st.builds(
                    fastkml.model.Alias,
                    source_href=urls(),
                    target_href=urls(),
                ),
            ),
        ),
    )
    def test_fuzz_resource_map(
        self,
        aliases: typing.Optional[typing.Iterable[fastkml.model.Alias]],
    ) -> None:
        resource_map = fastkml.model.ResourceMap(aliases=aliases)

        assert_repr_roundtrip(resource_map)
        assert_str_roundtrip(resource_map)
        assert_str_roundtrip_terse(resource_map)
        assert_str_roundtrip_verbose(resource_map)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        altitude_mode=st.one_of(st.none(), st.sampled_from(fastkml.enums.AltitudeMode)),
        location=st.one_of(
            st.none(),
            st.builds(
                fastkml.model.Location,
                altitude=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
                latitude=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=-90,
                    max_value=90,
                ),
                longitude=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=-180,
                    max_value=180,
                ),
            ),
        ),
        orientation=st.one_of(
            st.none(),
            st.builds(
                fastkml.model.Orientation,
                heading=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=-360,
                    max_value=360,
                ).filter(lambda x: x != 0),
                tilt=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=0,
                    max_value=180,
                ).filter(lambda x: x != 0),
                roll=st.floats(
                    allow_nan=False,
                    allow_infinity=False,
                    min_value=-180,
                    max_value=180,
                ).filter(lambda x: x != 0),
            ),
        ),
        scale=st.one_of(
            st.none(),
            st.builds(
                fastkml.model.Scale,
                x=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
                y=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
                z=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 0,
                ),
            ),
        ),
        link=st.one_of(st.none(), st.builds(fastkml.Link, href=urls())),
        resource_map=st.one_of(
            st.none(),
            st.builds(
                fastkml.model.ResourceMap,
                aliases=st.lists(
                    st.builds(
                        fastkml.model.Alias,
                        source_href=urls(),
                        target_href=urls(),
                    ),
                    min_size=1,
                ),
            ),
        ),
    )
    def test_fuzz_model(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        altitude_mode: typing.Optional[fastkml.enums.AltitudeMode],
        location: typing.Optional[fastkml.model.Location],
        orientation: typing.Optional[fastkml.model.Orientation],
        scale: typing.Optional[fastkml.model.Scale],
        link: typing.Optional[fastkml.Link],
        resource_map: typing.Optional[fastkml.model.ResourceMap],
    ) -> None:
        model = fastkml.model.Model(
            id=id,
            target_id=target_id,
            altitude_mode=altitude_mode,
            location=location,
            orientation=orientation,
            scale=scale,
            link=link,
            resource_map=resource_map,
        )

        assert_repr_roundtrip(model)
        assert_str_roundtrip(model)
        assert_str_roundtrip_terse(model)
        assert_str_roundtrip_verbose(model)
