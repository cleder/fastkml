# Copyright (C) 2021 -2023  Christian Ledermann
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

"""Test the kml classes."""

import pytest
from pygeoif import geometry as geo

from fastkml import atom
from fastkml import features
from fastkml import geometry
from fastkml import links
from fastkml import styles
from fastkml import views
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_feature_base(self) -> None:
        f = features._Feature(name="A Feature")
        assert f.name == "A Feature"
        assert f.visibility is None
        assert f.isopen is None
        assert f.atom_author is None
        assert f.atom_link is None
        assert f.address is None
        assert f.snippet is None
        assert f.description is None
        assert f.styles == []
        assert f.times is None
        assert "_Feature>" in str(f.to_string())

    def test_placemark_geometry_parameter_set(self) -> None:
        """Placemark object can be created with geometry parameter."""
        geometry = geo.Point(10, 20)

        placemark = features.Placemark(geometry=geometry)

        assert placemark.name is None
        assert placemark.description is None
        assert placemark.visibility is None
        assert placemark.geometry == geometry
        assert placemark.style_url is None
        assert "Point" in placemark.to_string()

    def test_placemark_kml_geometry_parameter_set(self) -> None:
        pt = geo.Point(10, 20)
        point = geometry.Point(geometry=pt)

        placemark = features.Placemark(kml_geometry=point)

        assert placemark.geometry == pt

    def test_placemark_geometry_and_kml_geometry_parameter_set(self) -> None:
        pt = geo.Point(10, 20)
        point = geometry.Point(geometry=pt)

        with pytest.raises(
            ValueError,
            match="^You can only specify one of kml_geometry or geometry$",
        ):
            features.Placemark(geometry=pt, kml_geometry=point)

    def test_network_link_with_link_parameter_only(self) -> None:
        """Test NetworkLink object with Link parameter only."""
        network_link = features.NetworkLink(
            link=links.Link(href="http://example.com/kml_file.kml"),
        )

        assert network_link.link.href == "http://example.com/kml_file.kml"
        assert bool(network_link)

    def test_network_link_with_no_link_parameter_only(self) -> None:
        """NetworkLink object with no Link."""
        network_link = features.NetworkLink(link=None)

        assert not bool(network_link)

    def test_network_link_with_optional_parameters(self) -> None:
        """NetworkLink object with optional parameters."""
        network_link = features.NetworkLink(
            name="My NetworkLink",
            visibility=True,
            isopen=False,
            atom_link=atom.Link(href="http://example.com/kml_file.kml"),
            refresh_visibility=True,
            fly_to_view=True,
            link=links.Link(href="http://example.com/kml_file.kml"),
            id="networklink1",
            target_id="target1",
            atom_author=atom.Author(name="John Doe"),
            address="123 Main St",
            phone_number="555-1234",
            snippet=features.Snippet(text="This is a snippet"),
            description="This is a description",
            view=views.LookAt(latitude=37.0, longitude=-122.0, altitude=0.0),
            style_url=styles.StyleUrl(url="#style1"),
            styles=[styles.Style(id="style1")],
        )

        assert network_link.name == "My NetworkLink"
        assert network_link.visibility
        assert not network_link.isopen
        assert network_link.atom_link.href == "http://example.com/kml_file.kml"
        assert network_link.refresh_visibility
        assert network_link.fly_to_view
        assert network_link.link.href == "http://example.com/kml_file.kml"
        assert network_link.id == "networklink1"
        assert network_link.target_id == "target1"
        assert network_link.atom_author.name == "John Doe"
        assert network_link.address == "123 Main St"
        assert network_link.phone_number == "555-1234"
        assert network_link.snippet.text == "This is a snippet"
        assert network_link.description == "This is a description"
        assert network_link.view.latitude == 37.0
        assert network_link.view.longitude == -122.0
        assert network_link.view.altitude == 0.0
        assert network_link.style_url.url == "#style1"
        assert len(network_link.styles) == 1
        assert network_link.styles[0].id == "style1"
        assert bool(network_link)

    def test_network_link_read(self) -> None:
        doc = (
            '<kml:NetworkLink xmlns:atom="http://www.w3.org/2005/Atom" '
            'xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="networklink1" targetId="target1"><kml:name>My NetworkLink</kml:name>'
            "<kml:visibility>1</kml:visibility><kml:open>0</kml:open>"
            '<atom:link href="http://example.com/kml_file.kml" /><atom:author>'
            "<atom:name>John Doe</atom:name></atom:author>"
            "<kml:address>123 Main St</kml:address>"
            "<kml:phoneNumber>555-1234</kml:phoneNumber>"
            "<kml:Snippet>This is a snippet</kml:Snippet>"
            "<kml:description>This is a description</kml:description>"
            "<kml:LookAt><kml:longitude>-122.0</kml:longitude>"
            "<kml:latitude>37.0</kml:latitude><kml:altitude>0.0</kml:altitude>"
            "<kml:altitudeMode>relativeToGround</kml:altitudeMode></kml:LookAt>"
            '<kml:styleUrl>#style1</kml:styleUrl><kml:Style id="style1" />'
            "<kml:refreshVisibility>1</kml:refreshVisibility>"
            "<kml:flyToView>1</kml:flyToView>"
            "<kml:Link><kml:href>http://example.com/kml_file.kml</kml:href></kml:Link>"
            "</kml:NetworkLink>"
        )

        network_link = features.NetworkLink.from_string(doc)

        assert network_link.name == "My NetworkLink"
        assert network_link.visibility
        assert not network_link.isopen
        assert network_link.atom_link.href == "http://example.com/kml_file.kml"
        assert network_link.refresh_visibility
        assert network_link.fly_to_view
        assert network_link.link.href == "http://example.com/kml_file.kml"
        assert network_link.id == "networklink1"
        assert network_link.target_id == "target1"
        assert network_link.atom_author.name == "John Doe"
        assert network_link.address == "123 Main St"
        assert network_link.phone_number == "555-1234"
        assert network_link.snippet.text == "This is a snippet"
        assert network_link.description == "This is a description"
        assert network_link.view.latitude == 37.0
        assert network_link.view.longitude == -122.0
        assert network_link.view.altitude == 0.0
        assert network_link.style_url.url == "#style1"
        assert len(network_link.styles) == 1
        assert network_link.styles[0].id == "style1"
        assert bool(network_link)


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
