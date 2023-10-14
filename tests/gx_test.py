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

"""Test the gx classes."""
from fastkml.gx import GxGeometry
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""


class TestGetGxGeometry(StdLibrary):
    def test_track(self) -> None:
        doc = """<gx:Track xmlns:kml="http://www.opengis.net/kml/2.2"
                xmlns:gx="http://www.google.com/kml/ext/2.2">
            <when>2020-01-01T00:00:00Z</when>
            <when>2020-01-01T00:10:00Z</when>
            <gx:coord>0.000000 0.000000</gx:coord>
            <gx:coord>1.000000 1.000000</gx:coord>
        </gx:Track>"""

        g = GxGeometry()
        g.from_string(doc)
        assert g.geometry.__geo_interface__ == {
            "type": "LineString",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": ((0.0, 0.0), (1.0, 1.0)),
        }

    def test_multitrack(self) -> None:
        doc = """
        <gx:MultiTrack xmlns:kml="http://www.opengis.net/kml/2.2"
            xmlns:gx="http://www.google.com/kml/ext/2.2">
          <gx:Track>
            <when>2020-01-01T00:00:00Z</when>
            <when>2020-01-01T00:10:00Z</when>
            <gx:coord>0.000000 0.000000</gx:coord>
            <gx:coord>1.000000 0.000000</gx:coord>
          </gx:Track>
          <gx:Track>
            <when>2020-01-01T00:10:00Z</when>
            <when>2020-01-01T00:20:00Z</when>
            <gx:coord>0.000000 1.000000</gx:coord>
            <gx:coord>1.000000 1.000000</gx:coord>
          </gx:Track>
        </gx:MultiTrack>
        """

        g = GxGeometry()
        g.from_string(doc)
        assert len(g.geometry) == 2


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""


class TestLxmlGetGxGeometry(Lxml, TestGetGxGeometry):
    """Test with lxml."""
