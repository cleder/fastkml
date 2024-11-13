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

import itertools
import typing

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml.containers
import fastkml.data
import fastkml.features
import fastkml.links
import fastkml.overlays
import fastkml.views
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import nc_name


class TestLxml(Lxml):
    @given(
        features_tuple=st.tuples(
            st.lists(
                st.builds(
                    fastkml.containers.Document,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.containers.Folder,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.features.Placemark,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.overlays.GroundOverlay,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.overlays.PhotoOverlay,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.features.NetworkLink,
                    link=st.builds(
                        fastkml.links.Link,
                        href=urls(),
                    ),
                ),
            ),
        ),
    )
    def test_fuzz_folder(
        self,
        features_tuple: typing.Tuple[typing.Iterable[fastkml.features._Feature]],
    ) -> None:
        features = itertools.chain(*features_tuple)
        folder = fastkml.containers.Folder(
            features=features,
        )

        assert_repr_roundtrip(folder)
        assert_str_roundtrip(folder)
        assert_str_roundtrip_terse(folder)
        assert_str_roundtrip_verbose(folder)

    @given(
        features_tuple=st.tuples(
            st.lists(
                st.builds(
                    fastkml.containers.Document,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.containers.Folder,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.features.Placemark,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.overlays.GroundOverlay,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.overlays.PhotoOverlay,
                ),
            ),
            st.lists(
                st.builds(
                    fastkml.features.NetworkLink,
                    link=st.builds(
                        fastkml.links.Link,
                        href=urls(),
                    ),
                ),
            ),
        ),
        schemata=st.lists(
            st.builds(
                fastkml.data.Schema,
                id=nc_name(),
            ),
            max_size=1,
        ),
    )
    def test_fuzz_document(
        self,
        features_tuple: typing.Tuple[typing.Iterable[fastkml.features._Feature]],
        schemata: typing.Iterable[fastkml.data.Schema],
    ) -> None:
        features: typing.Iterable[fastkml.features._Feature] = itertools.chain(
            *features_tuple,
        )
        document = fastkml.containers.Document(
            features=features,
            schemata=schemata,
        )

        assert_repr_roundtrip(document)
        assert_str_roundtrip(document)
        assert_str_roundtrip_terse(document)
        assert_str_roundtrip_verbose(document)
