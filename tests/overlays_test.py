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
import pytest

from fastkml import links
from fastkml import overlays
from fastkml import views
from fastkml.enums import AltitudeMode
from tests.base import Lxml
from tests.base import StdLibrary


class TestBaseOverlay(StdLibrary):
    def test_color_string(self) -> None:
        o = overlays._Overlay(name="An Overlay")
        o.color = "00010203"
        assert o.color == "00010203"

    def test_color_none(self) -> None:
        o = overlays._Overlay(name="An Overlay")
        o.color = "00010203"
        assert o.color == "00010203"
        o.color = None
        assert o.color is None

    def test_draw_order_string(self) -> None:
        o = overlays._Overlay(name="An Overlay")
        o.draw_order = 1
        assert o.draw_order == 1

    def test_draw_order_int(self) -> None:
        o = overlays._Overlay(name="An Overlay")
        o.draw_order = 1
        assert o.draw_order == 1

    def test_draw_order_none(self) -> None:
        o = overlays._Overlay(name="An Overlay")
        o.draw_order = 1
        assert o.draw_order == 1
        o.draw_order = None
        assert o.draw_order is None


class TestGroundOverlay(StdLibrary):
    pass


class TestGroundOverlayString(StdLibrary):
    def test_default_to_string(self) -> None:
        g = overlays.GroundOverlay()

        expected = overlays.GroundOverlay.class_from_string(
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

        expected = overlays.GroundOverlay.class_from_string(
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

        expected = overlays.GroundOverlay.class_from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123</kml:altitude>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_float(self) -> None:
        g = overlays.GroundOverlay()
        g.altitude = 123.4

        expected = overlays.GroundOverlay.class_from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_string(self) -> None:
        g = overlays.GroundOverlay(
            altitude=123.4,
            altitude_mode=AltitudeMode.clamp_to_ground,
        )

        expected = overlays.GroundOverlay.class_from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_mode_absolute(self) -> None:
        g = overlays.GroundOverlay(altitude=123.4, altitude_mode=AltitudeMode.absolute)
        expected = overlays.GroundOverlay.class_from_string(
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

        expected = overlays.GroundOverlay.class_from_string(
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

        expected = overlays.GroundOverlay.class_from_string(
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
        expected = overlays.GroundOverlay.class_from_string(
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

    def test_camera_altitude_value_error(self) -> None:
        po = overlays.PhotoOverlay(view=views.Camera())
        with pytest.raises(ValueError):
            po.view.altitude = object()

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


class TestBaseOverlayLxml(Lxml, TestBaseOverlay):
    """Test with lxml."""


class TestGroundOverlayLxml(Lxml, TestGroundOverlay):
    """Test with lxml."""


class TestGroundOverlayStringLxml(Lxml, TestGroundOverlay):
    """Test with lxml."""


class TestPhotoOverlayLxml(Lxml, TestPhotoOverlay):
    """Test with lxml."""
