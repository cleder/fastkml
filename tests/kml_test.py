# Copyright (C) 2022 -2024  Christian Ledermann
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

"""Test the kml class."""

import pygeoif as geo

from fastkml import features
from fastkml import kml
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_linarring_placemark(self) -> None:
        doc = kml.KML.class_from_string(
            """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
          <LinearRing>
            <coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,0.0</coordinates>
          </LinearRing>
        </Placemark> </kml>""",
        )
        doc2 = kml.KML.class_from_string(doc.to_string())
        assert isinstance(doc.features[0].geometry, geo.LinearRing)
        assert doc.to_string() == doc2.to_string()

    def test_kml(self) -> None:
        """Kml file without contents."""
        k = kml.KML(ns="")
        assert k.features == []
        assert (
            k.to_string().strip().replace(" ", "")
            == '<kmlxmlns="http://www.opengis.net/kml/2.2"/>'
        )
        k2 = kml.KML.class_from_string(k.to_string(), ns="")
        assert k.to_string() == k2.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""

    def test_from_string_with_unbound_prefix(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
            <Placemark>
            <ExtendedData>
            <lc:attachment>image.png</lc:attachment>
            </ExtendedData>
            </Placemark> </kml>"""
        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0], features.Placemark)
