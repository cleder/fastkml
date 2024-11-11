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

import pygeoif.types
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.atom
import fastkml.data
import fastkml.enums
import fastkml.features
import fastkml.gx
import fastkml.links
import fastkml.styles
import fastkml.views
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import geometries
from tests.hypothesis.strategies import kml_datetimes
from tests.hypothesis.strategies import lat_lon_alt_boxes
from tests.hypothesis.strategies import lods
from tests.hypothesis.strategies import nc_name
from tests.hypothesis.strategies import styles
from tests.hypothesis.strategies import track_items
from tests.hypothesis.strategies import xml_text


class TestLxml(Lxml):
    @given(
        text=st.one_of(st.none(), xml_text(min_size=1)),
        max_lines=st.one_of(
            st.none(),
            st.integers(min_value=0, max_value=2_147_483_647),
        ),
    )
    def test_fuzz_snippet(
        self,
        text: typing.Optional[str],
        max_lines: typing.Optional[int],
    ) -> None:
        snippet = fastkml.features.Snippet(text=text, max_lines=max_lines)

        assert_repr_roundtrip(snippet)
        assert_str_roundtrip(snippet)
        assert_str_roundtrip_terse(snippet)
        assert_str_roundtrip_verbose(snippet)

    @given(
        geometry=st.one_of(
            st.none(),
            geometries(),
        ),
    )
    def test_fuzz_placemark_geometry_only(
        self,
        geometry: typing.Union[
            pygeoif.types.GeoType,
            pygeoif.types.GeoCollectionType,
            None,
        ],
    ) -> None:
        placemark = fastkml.Placemark(
            geometry=geometry,
        )

        assert_repr_roundtrip(placemark)
        assert_str_roundtrip(placemark)
        assert_str_roundtrip_terse(placemark)
        assert_str_roundtrip_verbose(placemark)

    @given(
        view=st.one_of(
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
        times=st.one_of(
            st.builds(
                fastkml.TimeStamp,
                timestamp=kml_datetimes(),
            ),
            st.builds(
                fastkml.TimeSpan,
                begin=kml_datetimes(),
                end=kml_datetimes(),
            ),
        ),
        region=st.one_of(
            st.none(),
            st.builds(
                fastkml.views.Region,
                lat_lon_alt_box=lat_lon_alt_boxes(),
                lod=lods(),
            ),
        ),
    )
    def test_fuzz_placemark_view_times(
        self,
        view: typing.Union[fastkml.Camera, fastkml.LookAt, None],
        times: typing.Union[fastkml.TimeSpan, fastkml.TimeStamp, None],
        region: typing.Optional[fastkml.views.Region],
    ) -> None:
        placemark = fastkml.Placemark(
            view=view,
            times=times,
            region=region,
        )

        assert_repr_roundtrip(placemark)
        assert_str_roundtrip(placemark)
        assert_str_roundtrip_terse(placemark)
        assert_str_roundtrip_verbose(placemark)

    @given(
        address=st.one_of(
            st.none(),
            xml_text(min_size=1).filter(lambda x: x.strip() != ""),
        ),
        phone_number=st.one_of(
            st.none(),
            xml_text(min_size=1).filter(lambda x: x.strip() != ""),
        ),
        snippet=st.one_of(
            st.none(),
            st.builds(
                fastkml.features.Snippet,
                text=xml_text(min_size=1, max_size=256).filter(
                    lambda x: x.strip() != "",
                ),
                max_lines=st.integers(min_value=1, max_value=20),
            ),
        ),
        description=st.one_of(st.none(), xml_text()),
    )
    def test_fuzz_placemark_str(
        self,
        address: typing.Optional[str],
        phone_number: typing.Optional[str],
        snippet: typing.Optional[fastkml.features.Snippet],
        description: typing.Optional[str],
    ) -> None:
        placemark = fastkml.Placemark(
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
        )

        assert_repr_roundtrip(placemark)
        assert_str_roundtrip(placemark)
        assert_str_roundtrip_terse(placemark)
        assert_str_roundtrip_verbose(placemark)

    @given(
        id=st.one_of(st.none(), nc_name()),
        target_id=st.one_of(st.none(), nc_name()),
        name=st.one_of(st.none(), xml_text()),
        visibility=st.one_of(st.none(), st.booleans()),
        isopen=st.one_of(st.none(), st.booleans()),
        atom_link=st.one_of(
            st.none(),
            st.builds(
                fastkml.atom.Link,
                href=urls(),
            ),
        ),
        atom_author=st.one_of(
            st.none(),
            st.builds(
                fastkml.atom.Author,
                name=xml_text(min_size=1, max_size=256).filter(
                    lambda x: x.strip() != "",
                ),
            ),
        ),
    )
    def test_fuzz_placemark_atom(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        name: typing.Optional[str],
        visibility: typing.Optional[bool],
        isopen: typing.Optional[bool],
        atom_link: typing.Optional[fastkml.atom.Link],
        atom_author: typing.Optional[fastkml.atom.Author],
    ) -> None:
        placemark = fastkml.Placemark(
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
        )

        assert_repr_roundtrip(placemark)
        assert_str_roundtrip(placemark)
        assert_str_roundtrip_terse(placemark)
        assert_str_roundtrip_verbose(placemark)

    @given(
        kml_geometry=st.one_of(
            st.builds(
                fastkml.gx.Track,
                altitude_mode=st.sampled_from(fastkml.enums.AltitudeMode),
                track_items=st.lists(
                    track_items(),
                    min_size=1,
                    max_size=5,
                ),
            ),
            st.builds(
                fastkml.gx.MultiTrack,
                altitude_mode=st.one_of(
                    st.sampled_from(fastkml.enums.AltitudeMode),
                ),
                tracks=st.lists(
                    st.builds(
                        fastkml.gx.Track,
                        track_items=st.lists(
                            track_items(),
                            min_size=1,
                            max_size=3,
                        ),
                    ),
                    min_size=1,
                    max_size=3,
                ),
            ),
        ),
    )
    def test_fuzz_placemark_gx_track(
        self,
        kml_geometry: typing.Union[
            fastkml.gx.Track,
            fastkml.gx.MultiTrack,
        ],
    ) -> None:
        placemark = fastkml.Placemark(
            kml_geometry=kml_geometry,
        )

        assert_repr_roundtrip(placemark)
        assert_str_roundtrip(placemark)
        assert_str_roundtrip_terse(placemark)
        assert_str_roundtrip_verbose(placemark)

    @given(
        extended_data=st.builds(
            fastkml.ExtendedData,
            elements=st.tuples(
                st.builds(
                    fastkml.data.Data,
                    name=xml_text().filter(lambda x: x.strip() != ""),
                    value=xml_text().filter(lambda x: x.strip() != ""),
                    display_name=st.one_of(st.none(), xml_text()),
                ),
                st.builds(
                    fastkml.SchemaData,
                    schema_url=urls(),
                    data=st.lists(
                        st.builds(
                            fastkml.data.SimpleData,
                            name=xml_text().filter(lambda x: x.strip() != ""),
                            value=xml_text().filter(lambda x: x.strip() != ""),
                        ),
                        min_size=1,
                        max_size=3,
                    ),
                ),
            ),
        ),
    )
    def test_fuzz_placemark_extended_data(
        self,
        extended_data: typing.Optional[fastkml.ExtendedData],
    ) -> None:
        placemark = fastkml.Placemark(
            extended_data=extended_data,
        )

        assert_repr_roundtrip(placemark)
        assert_str_roundtrip(placemark)
        assert_str_roundtrip_terse(placemark)
        assert_str_roundtrip_verbose(placemark)

    @given(
        style_url=st.one_of(
            st.none(),
            st.builds(
                fastkml.StyleUrl,
                url=urls(),
            ),
        ),
        styles=st.one_of(
            st.none(),
            st.tuples(
                st.builds(
                    fastkml.Style,
                    styles=st.lists(
                        styles(),
                        min_size=1,
                        max_size=1,
                    ),
                ),
                st.builds(
                    fastkml.styles.StyleMap,
                    pairs=st.tuples(
                        st.builds(
                            fastkml.styles.Pair,
                            key=st.just(fastkml.enums.PairKey.normal),
                            style=st.one_of(
                                st.builds(
                                    fastkml.StyleUrl,
                                    url=urls(),
                                ),
                                st.builds(
                                    fastkml.Style,
                                    styles=st.lists(
                                        styles(),
                                        min_size=1,
                                        max_size=1,
                                    ),
                                ),
                            ),
                        ),
                        st.builds(
                            fastkml.styles.Pair,
                            key=st.just(fastkml.enums.PairKey.highlight),
                            style=st.one_of(
                                st.builds(
                                    fastkml.StyleUrl,
                                    url=urls(),
                                ),
                                st.builds(
                                    fastkml.Style,
                                    styles=st.lists(
                                        styles(),
                                        min_size=1,
                                        max_size=1,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
    def test_fuzz_placemark_styles(
        self,
        style_url: typing.Optional[fastkml.StyleUrl],
        styles: typing.Optional[
            typing.Iterable[typing.Union[fastkml.Style, fastkml.StyleMap]]
        ],
    ) -> None:
        placemark = fastkml.Placemark(
            style_url=style_url,
            styles=styles,
        )

        assert_repr_roundtrip(placemark)
        assert_str_roundtrip(placemark)
        assert_str_roundtrip_terse(placemark)
        assert_str_roundtrip_verbose(placemark)

    @given(
        refresh_visibility=st.one_of(st.none(), st.booleans()),
        fly_to_view=st.one_of(st.none(), st.booleans()),
        link=st.one_of(
            st.none(),
            st.builds(
                fastkml.links.Link,
                href=urls(),
            ),
        ),
    )
    def test_network_link(
        self,
        refresh_visibility: typing.Optional[bool],
        fly_to_view: typing.Optional[bool],
        link: typing.Optional[fastkml.links.Link],
    ) -> None:
        """Test NetworkLink object with optional parameters."""
        network_link = fastkml.features.NetworkLink(
            refresh_visibility=refresh_visibility,
            fly_to_view=fly_to_view,
            link=link,
        )

        assert network_link.refresh_visibility == refresh_visibility
        assert network_link.fly_to_view == fly_to_view
        assert network_link.link == link

        assert_repr_roundtrip(network_link)
        assert_str_roundtrip(network_link)
        assert_str_roundtrip_terse(network_link)
        assert_str_roundtrip_verbose(network_link)
