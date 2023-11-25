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

"""Test the kml classes."""
from fastkml import links
from fastkml.enums import RefreshMode
from fastkml.enums import ViewRefreshMode
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_icon(self) -> None:
        """Test the Icon class."""
        icon = links.Icon(
            id="icon-01",
            href="http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
            refresh_mode="onInterval",
            refresh_interval=60,
            view_refresh_mode="onStop",
            view_refresh_time=4,
            view_bound_scale=1.2,
            view_format="BBOX=[bboxWest],[bboxSouth],[bboxEast],[bboxNorth]",
            http_query="clientName=fastkml",
        )

        assert icon.id == "icon-01"
        assert icon.href == "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"
        assert icon.refresh_mode == "onInterval"
        assert icon.refresh_interval == 60
        assert icon.view_refresh_mode == "onStop"
        assert icon.view_refresh_time == 4
        assert icon.view_bound_scale == 1.2
        assert icon.view_format == "BBOX=[bboxWest],[bboxSouth],[bboxEast],[bboxNorth]"
        assert icon.http_query == "clientName=fastkml"

    def test_icon_read(self) -> None:
        """Test the Icon class."""
        icon = links.Icon.class_from_string(
            """
            <kml:Icon xmlns:kml="http://www.opengis.net/kml/2.2" id="icon-01">
            <kml:href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</kml:href>
            <kml:refreshMode>onInterval</kml:refreshMode>
            <kml:refreshInterval>60</kml:refreshInterval>
            <kml:viewRefreshMode>onStop</kml:viewRefreshMode>
            <kml:viewRefreshTime>4</kml:viewRefreshTime>
            <kml:viewBoundScale>1.2</kml:viewBoundScale>
            <kml:viewFormat>BBOX=[bboxWest],[bboxSouth],[bboxEast],[bboxNorth]</kml:viewFormat>
            <kml:httpQuery>clientName=fastkml</kml:httpQuery>
            </kml:Icon>
            """.strip(),
        )

        assert icon.id == "icon-01"
        assert icon.href == "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"
        assert icon.refresh_mode == RefreshMode("onInterval")
        assert icon.refresh_interval == 60
        assert icon.view_refresh_mode == ViewRefreshMode("onStop")
        assert icon.view_refresh_time == 4
        assert icon.view_bound_scale == 1.2
        assert icon.view_format == "BBOX=[bboxWest],[bboxSouth],[bboxEast],[bboxNorth]"
        assert icon.http_query == "clientName=fastkml"

        icon2 = links.Icon.class_from_string(icon.to_string())

        assert icon2.to_string() == icon.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
