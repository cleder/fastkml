# Copyright (C) 2021 - 2023 Christian Ledermann
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


from fastkml import kml, containers, features
from tests.base import Lxml
from tests.base import StdLibrary
import pytest


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_document_boolean_visibility(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document targetId="someTargetId">
          <name>Document.kml</name>
          <visibility>true</visibility>
          <open>1</open>
        </Document>
        </kml>"""

        k = kml.KML.class_from_string(doc, strict=False)
        assert k.features[0].visibility
        assert k.features[0].isopen

    def test_document_boolean_open(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document targetId="someTargetId">
          <name>Document.kml</name>
          <visibility>0</visibility>
          <open>false</open>
        </Document>
        </kml>"""

        k = kml.KML.class_from_string(doc, strict=False)
        assert k.features[0].visibility == 0
        assert k.features[0].isopen is False

    def test_document_boolean_visibility_invalid(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document targetId="someTargetId">
          <name>Document.kml</name>
          <visibility>invalid</visibility>
          <open>1</open>
        </Document>
        </kml>"""

        d = kml.KML.class_from_string(doc, strict=False)

        assert d.features[0].visibility is None
        assert d.features[0].isopen

    def test_container_creation(self) -> None:
        container = containers._Container(
            ns="ns",
            id="id",
            target_id="target_id",
            name="name"
        )
        assert container.ns == "ns"
        assert container.name == "name"

    def test_container_feature_append(self) -> None:
        container = containers._Container(
            ns="ns",
            id="id",
            target_id="target_id",
            name="name"
        )
        feature = features._Feature(name="new_feature")
        assert container.append(feature) is None
        with pytest.raises(ValueError):
            container.append(container)

    def test_document_container_get_style_url(self) -> None:
        document = containers.Document(
            name="Document",
            ns="ns",
            style_url="www.styleurl.com"
        )
        assert document.get_style_by_url(style_url="www.styleurl.com") is None



class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
