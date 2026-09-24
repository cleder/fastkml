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

from collections.abc import Iterable

from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.enums
import fastkml.links
import fastkml.model
from tests.base import Lxml
from tests.base import PyuppsalaNoSchemaValidation
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import nc_name


class TestLxml(Lxml):
    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
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
        id: str | None,
        target_id: str | None,
        altitude: float | None,
        latitude: float | None,
        longitude: float | None,
    ) -> None:
        location = fastkml.model.Location(
            id=id,
            target_id=target_id,
            altitude=altitude,
            latitude=latitude,
            longitude=longitude,
        )

        assert_repr_roundtrip(location)
        assert_str_roundtrip(location)
        assert_str_roundtrip_terse(location)
        assert_str_roundtrip_verbose(location)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
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
        id: str | None,
        target_id: str | None,
        heading: float | None,
        tilt: float | None,
        roll: float | None,
    ) -> None:
        orientation = fastkml.model.Orientation(
            id=id,
            target_id=target_id,
            heading=heading,
            tilt=tilt,
            roll=roll,
        )

        assert_repr_roundtrip(orientation)
        assert_str_roundtrip(orientation)
        assert_str_roundtrip_terse(orientation)
        assert_str_roundtrip_verbose(orientation)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        x=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        y=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
        z=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),
    )
    def test_fuzz_scale(
        self,
        id: str | None,
        target_id: str | None,
        x: float | None,
        y: float | None,
        z: float | None,
    ) -> None:
        scale = fastkml.model.Scale(id=id, target_id=target_id, x=x, y=y, z=z)

        assert_repr_roundtrip(scale)
        assert_str_roundtrip(scale)
        assert_str_roundtrip_terse(scale)
        assert_str_roundtrip_verbose(scale)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        target_href=st.one_of(st.none(), urls()),
        source_href=st.one_of(st.none(), urls()),
    )
    def test_fuzz_alias(
        self,
        id: str | None,
        target_id: str | None,
        target_href: str | None,
        source_href: str | None,
    ) -> None:
        alias = fastkml.model.Alias(
            id=id,
            target_id=target_id,
            target_href=target_href,
            source_href=source_href,
        )

        assert_repr_roundtrip(alias)
        assert_str_roundtrip(alias)
        assert_str_roundtrip_terse(alias)
        assert_str_roundtrip_verbose(alias)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
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
        id: str | None,
        target_id: str | None,
        aliases: Iterable[fastkml.model.Alias] | None,
    ) -> None:
        resource_map = fastkml.model.ResourceMap(
            id=id,
            target_id=target_id,
            aliases=aliases,
        )

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
                    lambda x: x != 1.0,
                ),
                y=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 1.0,
                ),
                z=st.floats(allow_nan=False, allow_infinity=False).filter(
                    lambda x: x != 1.0,
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
        id: str | None,
        target_id: str | None,
        altitude_mode: fastkml.enums.AltitudeMode | None,
        location: fastkml.model.Location | None,
        orientation: fastkml.model.Orientation | None,
        scale: fastkml.model.Scale | None,
        link: fastkml.Link | None,
        resource_map: fastkml.model.ResourceMap | None,
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


class TestPyuppsala(PyuppsalaNoSchemaValidation, TestLxml):
    # Reusing `TestLxml`'s hypothesis-wrapped test methods (rather than
    # duplicating their `@given` strategies and bodies) makes hypothesis flag
    # `HealthCheck.differing_executors`, since the same underlying test
    # function is now invoked from two classes. That's exactly what's
    # happening here, deliberately, so it's suppressed rather than avoided.
    test_fuzz_location = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_location)
    test_fuzz_orientation = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_orientation)
    test_fuzz_scale = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_scale)
    test_fuzz_alias = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_alias)
    test_fuzz_resource_map = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_resource_map)
    test_fuzz_model = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_model)
