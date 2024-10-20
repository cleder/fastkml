# Copyright (C) 2021 - 2023  Christian Ledermann
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

from pygeoif import geometry as geo

from fastkml import enums
from fastkml import geometry
from fastkml import links
from fastkml import overlays
from fastkml import views
from fastkml.enums import AltitudeMode
from tests.base import Lxml
from tests.base import StdLibrary


class TestGroundOverlay(StdLibrary):
    pass


class TestGroundOverlayString(StdLibrary):
    def test_default_to_string(self) -> None:
        g = overlays.GroundOverlay()

        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "</kml:GroundOverlay>",
        )
        assert g.to_string() == expected.to_string()

    def test_to_string(self) -> None:
        g = overlays.GroundOverlay()
        icon = links.Icon(href="http://example.com")
        g.icon = icon
        g.draw_order = 1
        g.color = "00010203"

        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:color>00010203</kml:color>"
            "<kml:drawOrder>1</kml:drawOrder>"
            "<kml:Icon>"
            "<kml:href>http://example.com</kml:href>"
            "</kml:Icon>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_int(self) -> None:
        g = overlays.GroundOverlay()
        g.altitude = 123.0

        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123</kml:altitude>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_float(self) -> None:
        g = overlays.GroundOverlay()
        g.altitude = 123.4

        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_invalid(self) -> None:
        g = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude> one two</kml:altitude>"
            "</kml:GroundOverlay>",
            strict=False,
        )

        assert g.altitude is None

    def test_draw_order_from_invalid(self) -> None:
        g = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:drawOrder>nan</kml:drawOrder>"
            "</kml:GroundOverlay>",
            strict=False,
        )

        assert g.draw_order is None

    def test_altitude_from_string(self) -> None:
        g = overlays.GroundOverlay(
            altitude=123.4,
            altitude_mode=AltitudeMode.clamp_to_ground,
        )

        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_mode_absolute(self) -> None:
        g = overlays.GroundOverlay(altitude=123.4, altitude_mode=AltitudeMode.absolute)
        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>absolute</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_latlonbox_no_rotation(self) -> None:
        llb = overlays.LatLonBox(
            ns="{http://www.opengis.net/kml/2.2}",
            north=10.0,
            south=20.0,
            east=30.0,
            west=40.0,
        )
        g = overlays.GroundOverlay(lat_lon_box=llb)

        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:LatLonBox>"
            "<kml:north>10</kml:north>"
            "<kml:south>20</kml:south>"
            "<kml:east>30</kml:east>"
            "<kml:west>40</kml:west>"
            "</kml:LatLonBox>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_latlonbox_rotation(self) -> None:
        llb = overlays.LatLonBox(
            ns="{http://www.opengis.net/kml/2.2}",
            north=10.0,
            south=20.0,
            east=30.0,
            west=40.0,
            rotation=50.0,
        )
        g = overlays.GroundOverlay(lat_lon_box=llb)

        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:LatLonBox>"
            "<kml:north>10</kml:north>"
            "<kml:south>20</kml:south>"
            "<kml:east>30</kml:east>"
            "<kml:west>40</kml:west>"
            "<kml:rotation>50</kml:rotation>"
            "</kml:LatLonBox>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_latlonbox_nswer(self) -> None:
        llb = overlays.LatLonBox(
            ns="{http://www.opengis.net/kml/2.2}",
            north=10.0,
            south=20.0,
            east=30.0,
            west=40.0,
            rotation=50.0,
        )
        g = overlays.GroundOverlay()
        g.lat_lon_box = llb
        expected = overlays.GroundOverlay.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:LatLonBox>"
            "<kml:north>10</kml:north>"
            "<kml:south>20</kml:south>"
            "<kml:east>30</kml:east>"
            "<kml:west>40</kml:west>"
            "<kml:rotation>50</kml:rotation>"
            "</kml:LatLonBox>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()


class TestPhotoOverlay(StdLibrary):
    def test_create_photo_overlay_with_all_optional_parameters(self) -> None:
        """Create a PhotoOverlay object with all optional parameters."""
        photo_overlay = overlays.PhotoOverlay(
            id="photo_overlay_1",
            name="Photo Overlay",
            visibility=True,
            description="This is a photo overlay",
            icon=links.Icon(href="https://example.com/photo.jpg"),
            view=views.LookAt(
                longitude=-122.0822035425683,
                latitude=37.42228990140251,
                altitude=0,
                heading=0,
                tilt=0,
                range=1000,
                altitude_mode=AltitudeMode.clamp_to_ground,
            ),
            point=geometry.Point(
                id="point_1",
                geometry=geo.Point(-122.0822035425683, 37.42228990140251, 0),
            ),
            shape=enums.Shape.rectangle,
            rotation=0,
            view_volume=overlays.ViewVolume(
                left_fov=-60,
                right_fov=60,
                bottom_fov=-45,
                top_fov=45,
                near=1,
            ),
            image_pyramid=overlays.ImagePyramid(
                tile_size=256,
                max_width=2048,
                max_height=2048,
                grid_origin=enums.GridOrigin.lower_left,
            ),
        )
        assert photo_overlay.id == "photo_overlay_1"
        assert photo_overlay.name == "Photo Overlay"
        assert photo_overlay.visibility
        assert photo_overlay.description == "This is a photo overlay"
        assert photo_overlay.shape == enums.Shape.rectangle
        assert photo_overlay.rotation == 0
        assert photo_overlay.view_volume.__bool__() is True
        assert bool(photo_overlay.view_volume)
        assert bool(photo_overlay.image_pyramid)

    def test_read_photo_overlay(self) -> None:
        """Read a PhotoOverlay object from a KML file."""
        doc = (
            '<kml:PhotoOverlay xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="photo_overlay_1"><kml:name>Photo Overlay</kml:name>'
            "<kml:visibility>1</kml:visibility>"
            "<kml:description>This is a photo overlay</kml:description>"
            "<kml:LookAt><kml:longitude>-122.0822035425683</kml:longitude>"
            "<kml:latitude>37.42228990140251</kml:latitude>"
            "<kml:altitude>0</kml:altitude><kml:heading>0</kml:heading>"
            "<kml:tilt>0</kml:tilt><kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "<kml:range>1000</kml:range></kml:LookAt>"
            "<kml:Icon><kml:href>https://example.com/photo.jpg</kml:href></kml:Icon>"
            "<kml:rotation>0</kml:rotation>"
            "<kml:ViewVolume><kml:leftFov>-60</kml:leftFov>"
            "<kml:rightFov>60</kml:rightFov><kml:bottomFov>-45</kml:bottomFov>"
            "<kml:topFov>45</kml:topFov><kml:near>1</kml:near>"
            "</kml:ViewVolume><kml:ImagePyramid><kml:tileSize>256</kml:tileSize>"
            "<kml:maxWidth>2048</kml:maxWidth><kml:maxHeight>2048</kml:maxHeight>"
            "<kml:gridOrigin>lowerLeft</kml:gridOrigin></kml:ImagePyramid>"
            '<kml:Point id="point_1">'
            "<kml:coordinates>-122.082204,37.422290,0.000000</kml:coordinates>"
            "</kml:Point><kml:shape>rectangle</kml:shape></kml:PhotoOverlay>"
        )

        p_overlay = overlays.PhotoOverlay.from_string(doc)

        assert p_overlay.id == "photo_overlay_1"
        assert p_overlay.name == "Photo Overlay"
        assert p_overlay.visibility
        assert p_overlay.description == "This is a photo overlay"
        assert p_overlay.shape == enums.Shape.rectangle
        assert p_overlay.rotation == 0
        assert p_overlay.view.longitude == -122.0822035425683
        assert p_overlay.view.latitude == 37.42228990140251
        assert p_overlay.view.altitude == 0
        assert p_overlay.view.heading == 0
        assert p_overlay.view.tilt == 0
        assert p_overlay.view.range == 1000
        assert p_overlay.view.altitude_mode == AltitudeMode.clamp_to_ground
        assert p_overlay.icon.href == "https://example.com/photo.jpg"
        assert p_overlay.view_volume.left_fov == -60
        assert p_overlay.view_volume.right_fov == 60
        assert p_overlay.view_volume.bottom_fov == -45
        assert p_overlay.view_volume.top_fov == 45
        assert p_overlay.view_volume.near == 1
        assert p_overlay.image_pyramid.tile_size == 256
        assert p_overlay.image_pyramid.max_width == 2048
        assert p_overlay.image_pyramid.max_height == 2048
        assert p_overlay.image_pyramid.grid_origin == enums.GridOrigin.lower_left
        assert p_overlay.point.id == "point_1"
        assert p_overlay.point.geometry.x == -122.082204
        assert p_overlay.point.geometry.y == 37.422290
        assert p_overlay.point.geometry.z == 0

    def test_camera_altitude_int(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        po.view.altitude = 123
        assert po.view.altitude == 123

    def test_camera_altitude_float(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        po.view.altitude = 123.4
        assert po.view.altitude == 123.4

    def test_camera_altitude_string(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        po.view.altitude = 123
        assert po.view.altitude == 123

    def test_camera_altitude_none(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        po.view.altitude = 123
        assert po.view.altitude == 123
        po.view.altitude = None
        assert po.view.altitude is None

    def test_camera_altitude_mode_default(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        assert po.view.altitude_mode == AltitudeMode("relativeToGround")

    def test_camera_altitude_mode_clamp(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        po.view.altitude_mode = AltitudeMode("clampToGround")
        assert po.view.altitude_mode == AltitudeMode("clampToGround")

    def test_camera_altitude_mode_absolute(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        po.view.altitude_mode = "absolute"
        assert po.view.altitude_mode == "absolute"

    def test_camera_initialization(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        po.view = views.Camera(
            longitude=10,
            latitude=20,
            altitude=30,
            heading=40,
            tilt=50,
            roll=60,
        )
        assert po.view.longitude == 10
        assert po.view.latitude == 20
        assert po.view.altitude == 30
        assert po.view.heading == 40
        assert po.view.tilt == 50
        assert po.view.roll == 60
        assert po.view.altitude_mode == AltitudeMode("relativeToGround")


class TestGroundOverlayLxml(Lxml, TestGroundOverlay):
    """Test with lxml."""


class TestGroundOverlayStringLxml(Lxml, TestGroundOverlay):
    """Test with lxml."""


class TestPhotoOverlayLxml(Lxml, TestPhotoOverlay):
    """Test with lxml."""
