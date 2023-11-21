# Copyright (C) 2021  Christian Ledermann
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

"""Test the Atom classes."""

from fastkml import atom
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_atom_link_ns(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        link = atom.Link(ns=ns)
        assert link.ns == ns
        assert link.to_string().startswith(
            '<kml:link xmlns:kml="http://www.opengis.net/kml/2.2"',
        )

    def test_atom_link(self) -> None:
        link = atom.Link(
            ns="{http://www.w3.org/2005/Atom}",
            href="#here",
            rel="alternate",
            type="text/html",
            hreflang="en",
            title="Title",
            length=3456,
        )

        serialized = link.to_string()

        assert '<atom:link xmlns:atom="http://www.w3.org/2005/Atom"' in serialized
        assert 'href="#here"' in serialized
        assert 'rel="alternate"' in serialized
        assert 'type="text/html"' in serialized
        assert 'hreflang="en"' in serialized
        assert 'title="Title"' in serialized
        assert 'length="3456"' in serialized

    def test_atom_link_read(self) -> None:
        link = atom.Link.class_from_string(
            '<atom:link xmlns:atom="http://www.w3.org/2005/Atom" '
            'href="#here" rel="alternate" type="text/html" hreflang="en" '
            'title="Title" length="3456" />',
        )
        assert link.href == "#here"
        assert link.rel == "alternate"
        assert link.type == "text/html"
        assert link.hreflang == "en"
        assert link.title == "Title"
        assert link.length == 3456

    def test_atom_link_read_no_href(self) -> None:
        link = atom.Link.class_from_string(
            '<atom:link xmlns:atom="http://www.w3.org/2005/Atom" '
            'rel="alternate" type="text/html" hreflang="en" '
            'title="Title" length="3456" />',
        )
        assert link.href is None

    def test_atom_person_ns(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        p = atom._Person(ns=ns)
        assert p.ns == ns

    def test_atom_author(self) -> None:
        a = atom.Author(
            ns="{http://www.w3.org/2005/Atom}",
            name="Nobody",
            uri="http://localhost",
            email="cl@donotreply.com",
        )

        serialized = a.to_string()
        assert '<atom:author xmlns:atom="http://www.w3.org/2005/Atom">' in serialized
        assert "<atom:name>Nobody</atom:name>" in serialized
        assert "<atom:uri>http://localhost</atom:uri>" in serialized
        assert "<atom:email>cl@donotreply.com</atom:email>" in serialized
        assert "</atom:author>" in serialized

    def test_atom_author_read(self) -> None:
        a = atom.Author.class_from_string(
            '<atom:author xmlns:atom="http://www.w3.org/2005/Atom">'
            "<atom:name>Nobody</atom:name><atom:uri>http://localhost</atom:uri>"
            "<atom:email>cl@donotreply.com</atom:email></atom:author>",
            ns="{http://www.w3.org/2005/Atom}",
        )

        assert a.name == "Nobody"
        assert a.uri == "http://localhost"
        assert a.email == "cl@donotreply.com"

    def test_atom_contributor_read_no_name(self) -> None:
        a = atom.Contributor.class_from_string(
            '<atom:contributor xmlns:atom="http://www.w3.org/2005/Atom">'
            "<atom:uri>http://localhost</atom:uri>"
            "<atom:email>cl@donotreply.com</atom:email></atom:contributor>",
            ns="{http://www.w3.org/2005/Atom}",
        )

        assert a.name is None
        assert a.uri == "http://localhost"
        assert a.email == "cl@donotreply.com"

    def test_atom_contributor_no_name(self) -> None:
        a = atom.Contributor(uri="http://localhost", email="cl@donotreply.com")

        assert a.name is None
        assert "atom:name" not in a.to_string()

    def test_author_roundtrip(self) -> None:
        a = atom.Author(name="Christian Ledermann")
        a.uri = "http://iwlearn.net"
        a.email = "christian@gmail.com"
        a.email = "christian"
        assert "email>" not in str(a.to_string())
        a2 = atom.Author.class_from_string(a.to_string())
        assert a.to_string() == a2.to_string()

    def test_link_roundtrip(self) -> None:
        link = atom.Link(href="http://localhost/", rel="alternate")
        link.title = "Title"
        link.type = "text/html"
        link.hreflang = "en"
        link.length = 4096
        l2 = atom.Link.class_from_string(link.to_string())
        assert link.to_string() == l2.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
