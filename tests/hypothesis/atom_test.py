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

from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.provisional import urls

import fastkml.atom
import fastkml.enums
from tests.base import Lxml
from tests.base import PyuppsalaNoSchemaValidation
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
        href: str | None,
        rel: str | None,
        type: str | None,
        hreflang: str | None,
        title: str | None,
        length: int | None,
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
        name: str | None,
        uri: str | None,
        email: str | None,
    ) -> None:
        author = fastkml.atom.Author(name=name, uri=uri, email=email)

        assert_repr_roundtrip(author)
        assert_str_roundtrip(author)
        assert_str_roundtrip_terse(author)
        assert_str_roundtrip_verbose(author)


class TestPyuppsala(PyuppsalaNoSchemaValidation, TestLxml):
    # Reusing `TestLxml`'s hypothesis-wrapped test method (rather than
    # duplicating its `@given` strategy and body) makes hypothesis flag
    # `HealthCheck.differing_executors`, since the same underlying test
    # function is now invoked from two classes. That's exactly what's
    # happening here, deliberately, so it's suppressed rather than avoided.
    test_fuzz_link = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_link)
    test_fuzz_author = settings(
        suppress_health_check=[HealthCheck.differing_executors],
    )(TestLxml.test_fuzz_author)
