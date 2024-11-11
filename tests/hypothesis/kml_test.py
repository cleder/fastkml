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

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml.containers
import fastkml.features
import fastkml.kml
import fastkml.links
import fastkml.overlays
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose


class TestLxml(Lxml):
    @given(
        feature=st.one_of(
            st.builds(
                fastkml.containers.Document,
            ),
            st.builds(
                fastkml.containers.Folder,
            ),
            st.builds(
                fastkml.features.Placemark,
            ),
            st.builds(
                fastkml.overlays.GroundOverlay,
            ),
            st.builds(
                fastkml.overlays.PhotoOverlay,
            ),
            st.builds(
                fastkml.features.NetworkLink,
                link=st.builds(
                    fastkml.links.Link,
                    href=urls(),
                ),
            ),
        ),
    )
    def test_fuzz_document(
        self,
        feature: fastkml.features._Feature,
    ) -> None:
        kml = fastkml.kml.KML(
            features=[feature],  # type: ignore[list-item]
        )

        assert_repr_roundtrip(kml)
        assert_str_roundtrip(kml)
        assert_str_roundtrip_terse(kml)
        assert_str_roundtrip_verbose(kml)
