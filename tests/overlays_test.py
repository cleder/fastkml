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
    def test_altitude_int(self) -> None:
        go = overlays.GroundOverlay()

        go.altitude = 123
        assert go.altitude == "123"

    def test_altitude_float(self) -> None:
        go = overlays.GroundOverlay()

        go.altitude = 123.4
        assert go.altitude == "123.4"

    def test_altitude_string(self) -> None:
        go = overlays.GroundOverlay()

        go.altitude = "123"
        assert go.altitude == "123"

    def test_altitude_value_error(self) -> None:
        go = overlays.GroundOverlay()

        with pytest.raises(ValueError):
            go.altitude = object()

    def test_altitude_none(self) -> None:
        go = overlays.GroundOverlay()

        go.altitude = "123"
        assert go.altitude == "123"
        go.altitude = None
        assert go.altitude is None

    def test_altitude_mode_default(self) -> None:
        go = overlays.GroundOverlay()

        assert go.altitude_mode == "clampToGround"

    def test_altitude_mode_error(self) -> None:
        go = overlays.GroundOverlay()

        go.altitude_mode = ""
        assert go.altitude_mode == "clampToGround"

    def test_altitude_mode_clamp(self) -> None:
        go = overlays.GroundOverlay()

        go.altitude_mode = "clampToGround"
        assert go.altitude_mode == "clampToGround"

    def test_altitude_mode_absolute(self) -> None:
        go = overlays.GroundOverlay()

        go.altitude_mode = "absolute"
        assert go.altitude_mode == "absolute"

    def test_latlonbox_function(self) -> None:
        go = overlays.GroundOverlay()

        go.lat_lon_box(10, 20, 30, 40, 50)

        assert go.north == "10"
        assert go.south == "20"
        assert go.east == "30"
        assert go.west == "40"
        assert go.rotation == "50"

    def test_latlonbox_string(self) -> None:
        go = overlays.GroundOverlay()

        go.north = "10"
        go.south = "20"
        go.east = "30"
        go.west = "40"
        go.rotation = "50"

        assert go.north == "10"
        assert go.south == "20"
        assert go.east == "30"
        assert go.west == "40"
        assert go.rotation == "50"

    def test_latlonbox_int(self) -> None:
        go = overlays.GroundOverlay()

        go.north = 10
        go.south = 20
        go.east = 30
        go.west = 40
        go.rotation = 50

        assert go.north == "10"
        assert go.south == "20"
        assert go.east == "30"
        assert go.west == "40"
        assert go.rotation == "50"

    def test_latlonbox_float(self) -> None:
        go = overlays.GroundOverlay()
        go.north = 10.0
        go.south = 20.0
        go.east = 30.0
        go.west = 40.0
        go.rotation = 50.0

        assert go.north == "10.0"
        assert go.south == "20.0"
        assert go.east == "30.0"
        assert go.west == "40.0"
        assert go.rotation == "50.0"

    def test_latlonbox_value_error(self) -> None:
        go = overlays.GroundOverlay()
        with pytest.raises(ValueError):
            go.north = object()

        with pytest.raises(ValueError):
            go.south = object()

        with pytest.raises(ValueError):
            go.east = object()

        with pytest.raises(ValueError):
            go.west = object()

        with pytest.raises(ValueError):
            go.rotation = object()

        assert go.north is None
        assert go.south is None
        assert go.east is None
        assert go.west is None
        assert go.rotation is None

    def test_latlonbox_empty_string(self) -> None:
        go = overlays.GroundOverlay()
        go.north = ""
        go.south = ""
        go.east = ""
        go.west = ""
        go.rotation = ""

        assert not go.north
        assert not go.south
        assert not go.east
        assert not go.west
        assert not go.rotation

    def test_latlonbox_none(self) -> None:
        go = overlays.GroundOverlay()
        go.north = None
        go.south = None
        go.east = None
        go.west = None
        go.rotation = None

        assert go.north is None
        assert go.south is None
        assert go.east is None
        assert go.west is None
        assert go.rotation is None


class TestGroundOverlayString(StdLibrary):
    def test_default_to_string(self) -> None:
        g = overlays.GroundOverlay()

        expected = overlays.GroundOverlay()
        expected.from_string(
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

        expected = overlays.GroundOverlay()
        expected.from_string(
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
        g.altitude = 123

        expected = overlays.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_float(self) -> None:
        g = overlays.GroundOverlay()
        g.altitude = 123.4

        expected = overlays.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_string(self) -> None:
        g = overlays.GroundOverlay()
        g.altitude = "123.4"

        expected = overlays.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_mode_absolute(self) -> None:
        g = overlays.GroundOverlay()
        g.altitude = "123.4"
        g.altitude_mode = "absolute"

        expected = overlays.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>absolute</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_mode_unknown_string(self) -> None:
        g = overlays.GroundOverlay()
        g.altitude = "123.4"
        g.altitudeMode = "unknown string"

        expected = overlays.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_mode_value(self) -> None:
        g = overlays.GroundOverlay()
        g.altitude = "123.4"
        g.altitudeMode = 1234

        expected = overlays.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_latlonbox_no_rotation(self) -> None:
        g = overlays.GroundOverlay()
        g.lat_lon_box(10, 20, 30, 40)

        expected = overlays.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:LatLonBox>"
            "<kml:north>10</kml:north>"
            "<kml:south>20</kml:south>"
            "<kml:east>30</kml:east>"
            "<kml:west>40</kml:west>"
            "<kml:rotation>0</kml:rotation>"
            "</kml:LatLonBox>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_latlonbox_rotation(self) -> None:
        g = overlays.GroundOverlay()
        g.lat_lon_box(10, 20, 30, 40, 50)

        expected = overlays.GroundOverlay()
        expected.from_string(
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
        g = overlays.GroundOverlay()
        g.north = 10
        g.south = 20
        g.east = 30
        g.west = 40
        g.rotation = 50

        expected = overlays.GroundOverlay()
        expected.from_string(
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
