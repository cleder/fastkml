# Copyright (C) 2021 - 2022  Christian Ledermann
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

"""Test the Network Link Control classes."""

import datetime

from fastkml.network_link_control import NetworkLinkControl
from fastkml.times import KmlDateTime
from tests.base import StdLibrary
from fastkml import views


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_network_link_control_obj(self) -> None:
        dt = datetime.datetime.now()
        kml_datetime = KmlDateTime(dt=dt)
        view = views.Camera()

        network_control_obj = NetworkLinkControl(
            min_refresh_period=1.1,
            max_session_length=100.1,
            cookie="cookie",
            message="message",
            link_name="link_name",
            link_description="link_description",
            link_snippet="link_snippet",
            expires=kml_datetime,
            view=view
        )

        assert network_control_obj.min_refresh_period == 1.1
        assert network_control_obj.max_session_length == 100.1
        assert network_control_obj.cookie == "cookie"
        assert network_control_obj.message == "message"
        assert network_control_obj.link_name == "link_name"
        assert network_control_obj.link_description == "link_description"
        assert network_control_obj.link_snippet == "link_snippet"
        assert str(network_control_obj.expires) == str(kml_datetime)
        assert str(network_control_obj.view) == str(view)

    def test_network_link_control_kml(self) -> None:
        doc = (
            '<kml:NetworkLinkControl xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:minRefreshPeriod>432000</kml:minRefreshPeriod>"
            "<kml:maxSessionLength>-1</kml:maxSessionLength>"
            "<kml:linkSnippet>A Snippet</kml:linkSnippet>"
            "<kml:expires>2008-05-30</kml:expires>"
            "</kml:NetworkLinkControl>"
        )

        nc = NetworkLinkControl.from_string(doc)

        dt = datetime.date(2008, 5, 30)
        kml_datetime = KmlDateTime(dt=dt)

        nc_obj = NetworkLinkControl(
            min_refresh_period=432000,
            max_session_length=-1,
            link_snippet="A Snippet",
            expires=kml_datetime,
        )

        assert nc == nc_obj
