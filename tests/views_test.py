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

from fastkml import views
from fastkml.enums import AltitudeMode
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_create_camera(self) -> None:
        """Test the creation of a camera."""
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
        assert camera.to_string()

    def test_camera_read(self) -> None:
        """Test the reading of a camera."""
        camera_xml = (
            '<kml:Camera xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="cam-id" targetId="target-cam-id">'
            "<kml:longitude>60</kml:longitude>"
            "<kml:latitude>50</kml:latitude>"
            "<kml:altitude>40</kml:altitude>"
            "<kml:heading>10</kml:heading>"
            "<kml:tilt>20</kml:tilt>"
            "<kml:roll>30</kml:roll>"
            "<kml:altitudeMode>relativeToGround</kml:altitudeMode>"
            "</kml:Camera>"
        )

        camera = views.Camera.from_string(camera_xml)

        assert camera.heading == 10
        assert camera.tilt == 20
        assert camera.roll == 30
        assert camera.altitude == 40
        assert camera.altitude_mode == AltitudeMode("relativeToGround")
        assert camera.latitude == 50
        assert camera.longitude == 60
        assert camera.id == "cam-id"
        assert camera.target_id == "target-cam-id"

    def test_create_look_at(self) -> None:
        look_at = views.LookAt(
            id="look-at-id",
            target_id="target-look-at-id",
            heading=10,
            tilt=20,
            range=30,
            altitude_mode=AltitudeMode("relativeToGround"),
            latitude=50,
            longitude=60,
        )

        assert look_at.heading == 10
        assert look_at.tilt == 20
        assert look_at.range == 30
        assert look_at.altitude_mode == AltitudeMode("relativeToGround")
        assert look_at.latitude == 50
        assert look_at.longitude == 60
        assert look_at.id == "look-at-id"
        assert look_at.target_id == "target-look-at-id"
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
            "<kml:range>30</kml:range>"
            "</kml:LookAt>"
        )
        look_at = views.LookAt.from_string(look_at_xml)

        assert look_at.heading == 10
        assert look_at.tilt == 20
        assert look_at.range == 30
        assert look_at.altitude_mode == AltitudeMode("relativeToGround")
        assert look_at.latitude == 50
        assert look_at.longitude == 60
        assert look_at.id == "look-at-id"
        assert look_at.target_id == "target-look-at-id"

    def test_region_with_all_optional_parameters(self) -> None:
        """Region object can be initialized with all optional parameters."""
        region = views.Region(
            id="region1",
            lat_lon_alt_box=views.LatLonAltBox(
                north=37.85,
                south=37.80,
                east=-122.35,
                west=-122.40,
                min_altitude=0,
                max_altitude=1000,
                altitude_mode=AltitudeMode.clamp_to_ground,
            ),
            lod=views.Lod(
                min_lod_pixels=256,
                max_lod_pixels=1024,
                min_fade_extent=0,
                max_fade_extent=512,
            ),
        )

        assert region.id == "region1"
        assert region.lat_lon_alt_box.north == 37.85
        assert region.lat_lon_alt_box.south == 37.80
        assert region.lat_lon_alt_box.east == -122.35
        assert region.lat_lon_alt_box.west == -122.40
        assert region.lat_lon_alt_box.min_altitude == 0
        assert region.lat_lon_alt_box.max_altitude == 1000
        assert region.lat_lon_alt_box.altitude_mode == AltitudeMode.clamp_to_ground
        assert region.lod.min_lod_pixels == 256
        assert region.lod.max_lod_pixels == 1024
        assert region.lod.min_fade_extent == 0
        assert region.lod.max_fade_extent == 512
        assert region
        assert bool(region)

    def test_region_read(self) -> None:
        doc = (
            '<kml:Region xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="region1"><kml:LatLonAltBox><kml:north>37.85</kml:north>'
            "<kml:south>37.8</kml:south><kml:east>-122.35</kml:east>"
            "<kml:west>-122.4</kml:west><kml:minAltitude>0</kml:minAltitude>"
            "<kml:maxAltitude>1000</kml:maxAltitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:LatLonAltBox><kml:Lod><kml:minLodPixels>256</kml:minLodPixels>"
            "<kml:maxLodPixels>1024</kml:maxLodPixels>"
            "<kml:minFadeExtent>0</kml:minFadeExtent>"
            "<kml:maxFadeExtent>512</kml:maxFadeExtent></kml:Lod></kml:Region>"
        )

        region = views.Region.from_string(doc)

        assert region.id == "region1"
        assert region.lat_lon_alt_box.north == 37.85
        assert region.lat_lon_alt_box.south == 37.80
        assert region.lat_lon_alt_box.east == -122.35
        assert region.lat_lon_alt_box.west == -122.40
        assert region.lat_lon_alt_box.min_altitude == 0
        assert region.lat_lon_alt_box.max_altitude == 1000
        assert region.lat_lon_alt_box.altitude_mode == AltitudeMode.clamp_to_ground
        assert region.lod.min_lod_pixels == 256
        assert region.lod.max_lod_pixels == 1024
        assert region.lod.min_fade_extent == 0
        assert region.lod.max_fade_extent == 512
        assert region

    def test_initialized_with_empty_lat_lon_alt_box(self) -> None:
        """Region object can be initialized with empty LatLonAltBox object."""
        lat_lon_alt_box = views.LatLonAltBox()

        region = views.Region(lat_lon_alt_box=lat_lon_alt_box)

        assert not region
        assert region.lat_lon_alt_box == lat_lon_alt_box
        assert region.lod is None


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
