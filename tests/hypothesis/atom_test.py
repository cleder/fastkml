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
Property-based tests for Link and Author classes using Hypothesis.

This module implements fuzz testing to verify the serialization/deserialization
roundtrip and string representation of Link and Author classes under various
input conditions.
"""

import typing

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml
import fastkml.enums
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.common import assert_str_roundtrip_terse
from tests.hypothesis.common import assert_str_roundtrip_verbose
from tests.hypothesis.strategies import href_langs
from tests.hypothesis.strategies import media_types
from tests.hypothesis.strategies import xml_text


class TestLxml(Lxml):

    @given(
        href=urls(),
        rel=st.one_of(st.none(), xml_text()),
        type=st.one_of(st.none(), media_types()),
        hreflang=st.one_of(st.none(), href_langs()),
        title=st.one_of(st.none(), xml_text()),
        length=st.one_of(st.none(), st.integers()),
    )
    def test_fuzz_link(
        self,
        href: typing.Optional[str],
        rel: typing.Optional[str],
        type: typing.Optional[str],
        hreflang: typing.Optional[str],
        title: typing.Optional[str],
        length: typing.Optional[int],
    ) -> None:
        link = fastkml.atom.Link(
            href=href,
            rel=rel,
            type=type,
            hreflang=hreflang,
            title=title,
            length=length,
        )

        assert_repr_roundtrip(link)
        assert_str_roundtrip(link)
        assert_str_roundtrip_terse(link)
        assert_str_roundtrip_verbose(link)

    @given(
        name=st.one_of(st.none(), xml_text()),
        uri=st.one_of(st.none(), urls()),
        email=st.one_of(st.none(), st.emails()),
    )
    def test_fuzz_author(
        self,
        name: typing.Optional[str],
        uri: typing.Optional[str],
        email: typing.Optional[str],
    ) -> None:
        author = fastkml.atom.Author(name=name, uri=uri, email=email)

        assert_repr_roundtrip(author)
        assert_str_roundtrip(author)
        assert_str_roundtrip_terse(author)
        assert_str_roundtrip_verbose(author)
