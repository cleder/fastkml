# Copyright (C) 2022  Christian Ledermann
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

"""Test the (Abstract)Views classes."""

import datetime

from dateutil.tz import tzutc

from fastkml import times
from fastkml import views
from fastkml.enums import AltitudeMode
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_create_camera(self) -> None:
        """Test the creation of a camera."""
        time_span = times.TimeSpan(
            id="time-span-id",
            begin=times.KmlDateTime(datetime.datetime(2019, 1, 1, tzinfo=tzutc())),
            end=times.KmlDateTime(datetime.datetime(2019, 1, 2, tzinfo=tzutc())),
        )

        camera = views.Camera(
            id="cam-id",
            target_id="target-cam-id",
            heading=10,
            tilt=20,
            roll=30,
            altitude=40,
            altitude_mode=AltitudeMode("relativeToGround"),
            latitude=50,
            longitude=60,
            time_primitive=time_span,
        )

        assert camera.heading == 10
        assert camera.tilt == 20
        assert camera.roll == 30
        assert camera.altitude == 40
        assert camera.altitude_mode == AltitudeMode("relativeToGround")
        assert camera.latitude == 50
        assert camera.longitude == 60
        assert camera.id == "cam-id"
        assert camera.target_id == "target-cam-id"
        assert camera.begin == times.KmlDateTime(
            datetime.datetime(2019, 1, 1, tzinfo=tzutc()),
        )
        assert camera.end == times.KmlDateTime(
            datetime.datetime(2019, 1, 2, tzinfo=tzutc()),
        )
        assert camera.to_string()

    def test_camera_read(self) -> None:
        """Test the reading of a camera."""
        camera_xml = (
            '<kml:Camera xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="cam-id" targetId="target-cam-id">'
            '<kml:TimeSpan id="time-span-id">'
            "<kml:begin>2019-01-01T00:00:00</kml:begin>"
            "<kml:end>2019-01-02T00:00:00</kml:end>"
            "</kml:TimeSpan>"
            "<kml:longitude>60</kml:longitude>"
            "<kml:latitude>50</kml:latitude>"
            "<kml:altitude>40</kml:altitude>"
            "<kml:heading>10</kml:heading>"
            "<kml:tilt>20</kml:tilt>"
            "<kml:roll>30</kml:roll>"
            "<kml:altitudeMode>relativeToGround</kml:altitudeMode>"
            "</kml:Camera>"
        )

        camera = views.Camera.class_from_string(camera_xml)

        assert camera.heading == 10
        assert camera.tilt == 20
        assert camera.roll == 30
        assert camera.altitude == 40
        assert camera.altitude_mode == AltitudeMode("relativeToGround")
        assert camera.latitude == 50
        assert camera.longitude == 60
        assert camera.id == "cam-id"
        assert camera.target_id == "target-cam-id"
        assert camera.begin == times.KmlDateTime(
            datetime.datetime(2019, 1, 1, tzinfo=tzutc()),
        )
        assert camera.end == times.KmlDateTime(
            datetime.datetime(2019, 1, 2, tzinfo=tzutc()),
        )

    def test_create_look_at(self) -> None:
        time_stamp = times.TimeStamp(
            id="time-span-id",
            timestamp=times.KmlDateTime(datetime.datetime(2019, 1, 1, tzinfo=tzutc())),
        )

        look_at = views.LookAt(
            id="look-at-id",
            target_id="target-look-at-id",
            heading=10,
            tilt=20,
            range=30,
            altitude_mode=AltitudeMode("relativeToGround"),
            latitude=50,
            longitude=60,
            time_primitive=time_stamp,
        )

        assert look_at.heading == 10
        assert look_at.tilt == 20
        assert look_at.range == 30
        assert look_at.altitude_mode == AltitudeMode("relativeToGround")
        assert look_at.latitude == 50
        assert look_at.longitude == 60
        assert look_at.id == "look-at-id"
        assert look_at.target_id == "target-look-at-id"
        assert look_at._times.timestamp.dt == datetime.datetime(
            2019,
            1,
            1,
            tzinfo=tzutc(),
        )
        assert look_at.begin is None
        assert look_at.end is None
        assert look_at.to_string()

    def test_look_at_read(self) -> None:
        look_at_xml = (
            '<kml:LookAt xmlns:kml="http://www.opengis.net/kml/2.2" id="look-at-id" '
            'targetId="target-look-at-id">'
            "<kml:longitude>60</kml:longitude>"
            "<kml:latitude>50</kml:latitude>"
            "<kml:heading>10</kml:heading>"
            "<kml:tilt>20</kml:tilt>"
            "<kml:altitudeMode>relativeToGround</kml:altitudeMode>"
            '<kml:TimeStamp id="time-span-id">'
            "<kml:when>2019-01-01T00:00:00</kml:when>"
            "</kml:TimeStamp>"
            "<kml:range>30</kml:range>"
            "</kml:LookAt>"
        )
        look_at = views.LookAt.class_from_string(look_at_xml)

        assert look_at.heading == 10
        assert look_at.tilt == 20
        assert look_at.range == 30
        assert look_at.altitude_mode == AltitudeMode("relativeToGround")
        assert look_at.latitude == 50
        assert look_at.longitude == 60
        assert look_at.id == "look-at-id"
        assert look_at.target_id == "target-look-at-id"
        assert look_at._times.timestamp.dt == datetime.datetime(
            2019,
            1,
            1,
            tzinfo=tzutc(),
        )
        assert look_at.begin is None
        assert look_at.end is None


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
