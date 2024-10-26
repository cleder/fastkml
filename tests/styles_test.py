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

"""Test the styles classes."""
import pytest

from fastkml import kml
from fastkml import links
from fastkml import styles
from fastkml.enums import ColorMode
from fastkml.enums import DisplayMode
from fastkml.enums import PairKey
from fastkml.enums import Units
from fastkml.exceptions import KMLParseError
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_style_url(self) -> None:
        url = styles.StyleUrl(id="id-0", url="#style-0", target_id="target-0")

        serialized = url.to_string()

        assert '<kml:styleUrl xmlns:kml="http://www.opengis.net/kml/2.2"' in serialized
        assert 'id="id-0"' in serialized
        assert 'targetId="target-0"' in serialized
        assert ">#style-0</kml:styleUrl>" in serialized

    def test_style_url_read(self) -> None:
        url = styles.StyleUrl.from_string(
            '<kml:styleUrl xmlns:kml="http://www.opengis.net/kml/2.2"'
            ' id="id-0" targetId="target-0">#style-0</kml:styleUrl>',
        )

        assert url.id == "id-0"
        assert url.url == "#style-0"
        assert url.target_id == "target-0"

    def test_icon_style(self) -> None:
        icons = styles.IconStyle(
            id="id-0",
            target_id="target-0",
            color="ff0000ff",
            color_mode=ColorMode("random"),
            scale=1.0,
            heading=0,
            icon=links.Icon(href="http://example.com/icon.png"),
        )

        serialized = icons.to_string()

        assert '<kml:IconStyle xmlns:kml="http://www.opengis.net/kml/2.2"' in serialized
        assert 'id="id-0"' in serialized
        assert 'targetId="target-0"' in serialized
        assert "<kml:color>ff0000ff</kml:color>" in serialized
        assert "<kml:colorMode>random</kml:colorMode>" in serialized
        assert "<kml:scale>1.0</kml:scale>" in serialized
        assert "<kml:heading>0</kml:heading>" in serialized
        assert "<kml:Icon>" in serialized
        assert "<kml:href>http://example.com/icon.png</kml:href>" in serialized
        assert "</kml:Icon>" in serialized
        assert "</kml:IconStyle>" in serialized

    def test_icon_style_with_hot_spot(self) -> None:
        icon_style = styles.IconStyle(
            ns="{http://www.opengis.net/kml/2.2}",
            id="id-1",
            target_id="target-1",
            color="ff2200ff",
            color_mode=ColorMode.random,
            scale=5.0,
            heading=20.0,
            icon=links.Icon(
                ns="{http://www.opengis.net/kml/2.2}",
                id="icon-id",
                href="",
            ),
            hot_spot=styles.HotSpot(
                ns="{http://www.opengis.net/kml/2.2}",
                x=0.5,
                y=0.7,
                xunits=Units.fraction,
                yunits=Units.inset_pixels,
            ),
        )

        serialized = icon_style.to_string()

        assert "icon-id" not in serialized
        assert "hotSpot" in serialized
        assert 'x="0.5"' in serialized
        assert 'y="0.7"' in serialized
        assert 'xunits="fraction"' in serialized
        assert 'yunits="insetPixels"' in serialized
        assert "Icon>" not in serialized
        assert "href" not in serialized

    def test_icon_style_read(self) -> None:
        icons = styles.IconStyle.from_string(
            '<kml:IconStyle xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-1" targetId="target-1">'
            "<kml:color>ff2200ff</kml:color><kml:colorMode>random</kml:colorMode>"
            "<kml:scale>5</kml:scale><kml:heading>20</kml:heading><kml:Icon>"
            "<kml:href>http://example.com/icon.png</kml:href></kml:Icon>"
            '<kml:hotSpot x="0.5"  y="0.7" xunits="fraction" yunits="insetPixels"/>'
            "</kml:IconStyle>",
        )

        assert icons.id == "id-1"
        assert icons.target_id == "target-1"
        assert icons.color == "ff2200ff"
        assert icons.color_mode == ColorMode("random")
        assert icons.scale == 5.0
        assert icons.icon.href == "http://example.com/icon.png"
        assert icons.heading == 20.0
        assert icons.hot_spot.x == 0.5
        assert icons.hot_spot.y == 0.7
        assert icons.hot_spot.xunits.value == "fraction"
        assert icons.hot_spot.yunits.value == "insetPixels"

    def test_icon_style_with_hot_spot_enum_relaxed(self) -> None:
        icons = styles.IconStyle.from_string(
            '<kml:IconStyle xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-1" targetId="target-1">'
            "<kml:color>ff2200ff</kml:color><kml:colorMode>random</kml:colorMode>"
            "<kml:scale>5</kml:scale><kml:heading>20</kml:heading><kml:Icon>"
            "<kml:href>http://example.com/icon.png</kml:href></kml:Icon>"
            '<kml:hotSpot x="0.5"  y="0.7" xunits="Fraction" yunits="Insetpixels"/>'
            "</kml:IconStyle>",
            strict=False,
        )
        assert icons.hot_spot.xunits.value == "fraction"
        assert icons.hot_spot.yunits.value == "insetPixels"

    def test_icon_style_with_hot_spot_enum_strict(self) -> None:
        with pytest.raises(KMLParseError):
            styles.IconStyle.from_string(
                '<kml:IconStyle xmlns:kml="http://www.opengis.net/kml/2.2" '
                'id="id-1" targetId="target-1">'
                "<kml:color>ff2200ff</kml:color><kml:colorMode>random</kml:colorMode>"
                "<kml:scale>5</kml:scale><kml:heading>20</kml:heading><kml:Icon>"
                "<kml:href>http://example.com/icon.png</kml:href></kml:Icon>"
                '<kml:hotSpot x="0.5"  y="0.7" xunits="Fraction" yunits="Insetpixels"/>'
                "</kml:IconStyle>",
            )

    def test_line_style(self) -> None:
        lines = styles.LineStyle(
            id="id-0",
            target_id="target-0",
            color="ff0000ff",
            color_mode=ColorMode.normal,
            width=1.2,
        )

        serialized = lines.to_string()

        assert '<kml:LineStyle xmlns:kml="http://www.opengis.net/kml/2.2"' in serialized
        assert 'id="id-0"' in serialized
        assert 'targetId="target-0"' in serialized
        assert "<kml:color>ff0000ff</kml:color>" in serialized
        assert "<kml:colorMode>normal</kml:colorMode>" in serialized
        assert "<kml:width>1.2</kml:width>" in serialized
        assert "</kml:LineStyle>" in serialized

    def test_line_style_read(self) -> None:
        lines = styles.LineStyle.from_string(
            '<kml:LineStyle xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-l0" targetId="target-line">\n'
            "  <kml:color>ffaa00ff</kml:color>\n"
            "  <kml:colorMode>normal</kml:colorMode>\n"
            "  <kml:width>3.0</kml:width>\n"
            "</kml:LineStyle>\n",
        )

        assert lines.id == "id-l0"
        assert lines.target_id == "target-line"
        assert lines.color == "ffaa00ff"
        assert lines.color_mode == ColorMode.normal
        assert lines.width == 3.0

    def test_poly_style(self) -> None:
        ps = styles.PolyStyle(
            id="id-0",
            target_id="target-0",
            color="ff0000ff",
            color_mode=ColorMode.random,
            fill=False,
            outline=True,
        )

        serialized = ps.to_string()

        assert '<kml:PolyStyle xmlns:kml="http://www.opengis.net/kml/2.2"' in serialized
        assert 'id="id-0"' in serialized
        assert 'targetId="target-0"' in serialized
        assert "<kml:color>ff0000ff</kml:color>" in serialized
        assert "<kml:colorMode>random</kml:colorMode>" in serialized
        assert "<kml:fill>0</kml:fill>" in serialized
        assert "<kml:outline>1</kml:outline>" in serialized
        assert "</kml:PolyStyle>" in serialized

    def test_poly_style_read(self) -> None:
        ps = styles.PolyStyle.from_string(
            '<kml:PolyStyle xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-1" targetId="target-1">'
            "<kml:color>ffaabbff</kml:color>"
            "<kml:colorMode>normal</kml:colorMode>"
            "<kml:fill>1</kml:fill>"
            "<kml:outline>0</kml:outline>"
            "</kml:PolyStyle>",
        )

        assert ps.id == "id-1"
        assert ps.target_id == "target-1"
        assert ps.color == "ffaabbff"
        assert ps.color_mode == ColorMode.normal
        assert ps.fill == 1
        assert ps.outline == 0

    def test_label_style(self) -> None:
        ls = styles.LabelStyle(
            id="id-0",
            target_id="target-0",
            color="ff0000ff",
            color_mode=ColorMode.random,
            scale=1.434,
        )

        serialized = ls.to_string()

        assert (
            '<kml:LabelStyle xmlns:kml="http://www.opengis.net/kml/2.2"' in serialized
        )
        assert 'id="id-0"' in serialized
        assert 'targetId="target-0"' in serialized
        assert "<kml:color>ff0000ff</kml:color>" in serialized
        assert "<kml:colorMode>random</kml:colorMode>" in serialized
        assert "<kml:scale>1.434</kml:scale>" in serialized
        assert "</kml:LabelStyle>" in serialized

    def test_label_style_read(self) -> None:
        ls = styles.LabelStyle.from_string(
            '<kml:LabelStyle xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-1" targetId="target-1">'
            "<kml:color>ff001122</kml:color>"
            "<kml:colorMode>normal</kml:colorMode>"
            "<kml:scale>2.2</kml:scale>"
            "</kml:LabelStyle>",
        )

        assert ls.id == "id-1"
        assert ls.target_id == "target-1"
        assert ls.color == "ff001122"
        assert ls.color_mode == ColorMode.normal
        assert ls.scale == 2.2

    def test_balloon_style(self) -> None:
        bs = styles.BalloonStyle(
            id="id-0",
            target_id="target-0",
            bg_color="7fff0000",
            text_color="ff00ff00",
            text="<b>Hello</b>",
            display_mode=DisplayMode.hide,
        )

        serialized = bs.to_string()

        assert (
            '<kml:BalloonStyle xmlns:kml="http://www.opengis.net/kml/2.2"' in serialized
        )
        assert 'id="id-0"' in serialized
        assert 'targetId="target-0">' in serialized
        assert "<kml:bgColor>7fff0000</kml:bgColor>" in serialized
        assert "<kml:textColor>ff00ff00</kml:textColor>" in serialized
        assert "<kml:text>&lt;b&gt;Hello&lt;/b&gt;</kml:text>" in serialized
        assert "<kml:displayMode>hide</kml:displayMode>" in serialized
        assert "</kml:BalloonStyle>" in serialized

    def test_balloon_style_read(self) -> None:
        bs = styles.BalloonStyle.from_string(
            '<kml:BalloonStyle xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-7" targetId="target-6">'
            "<kml:bgColor>7fff1144</kml:bgColor>"
            "<kml:textColor>ff11ff22</kml:textColor>"
            "<kml:text>&lt;b&gt;World&lt;/b&gt;</kml:text>"
            "<kml:displayMode>default</kml:displayMode>"
            "</kml:BalloonStyle>",
        )

        assert bs.id == "id-7"
        assert bs.target_id == "target-6"
        assert bs.bg_color == "7fff1144"
        assert bs.text_color == "ff11ff22"
        assert bs.text == "<b>World</b>"
        assert bs.display_mode == DisplayMode.default

    def test_style(self) -> None:
        icons = styles.IconStyle(
            id="id-i0",
            target_id="target-i0",
            color="ff0000ff",
            color_mode=ColorMode.random,
            scale=1.0,
            heading=0,
            icon=links.Icon(href="http://example.com/icon.png"),
        )
        lines = styles.LineStyle(
            id="id-l0",
            target_id="target-l0",
            color="ff0000ff",
            color_mode=ColorMode.normal,
            width=1.0,
        )
        bs = styles.BalloonStyle(
            id="id-b0",
            target_id="target-b0",
            bg_color="7fff0000",
            text_color="ff00ff00",
            text="<b>Hello</b>",
            display_mode=DisplayMode.hide,
        )
        ls = styles.LabelStyle(
            id="id-a0",
            target_id="target-a0",
            color="ff0000ff",
            color_mode=ColorMode.random,
            scale=1.0,
        )
        ps = styles.PolyStyle(
            id="id-p0",
            target_id="target-p0",
            color="ff0000ff",
            color_mode=ColorMode.random,
            fill=False,
            outline=True,
        )
        style = styles.Style(
            id="id-0",
            target_id="target-0",
            styles=[icons, lines, bs, ls, ps],
        )

        serialized = style.to_string()

        assert '<kml:Style xmlns:kml="http://www.opengis.net/kml/2.2" ' in serialized
        assert 'id="id-0" ' in serialized
        assert 'targetId="target-0">' in serialized
        assert "<kml:IconStyle" in serialized
        assert "<kml:Icon>" in serialized
        assert "</kml:Icon>" in serialized
        assert "</kml:IconStyle>" in serialized
        assert "<kml:LineStyle" in serialized
        assert "<kml:BalloonStyle " in serialized
        assert "<kml:LabelStyle " in serialized
        assert "<kml:PolyStyle " in serialized
        assert "</kml:PolyStyle>" in serialized
        assert "</kml:Style>" in serialized

    def test_style_read(self) -> None:
        style = styles.Style.from_string(
            '<kml:Style xmlns:kml="http://www.opengis.net/kml/2.2" '
            'id="id-0" targetId="target-0">'
            '<kml:IconStyle id="id-i0" targetId="target-i0">'
            "<kml:color>ff0000ff</kml:color>"
            "<kml:colorMode>random</kml:colorMode>"
            "<kml:scale>1.0</kml:scale>"
            "<kml:heading>0</kml:heading>"
            "<kml:Icon>"
            "<kml:href>http://example.com/icon.png</kml:href>"
            "</kml:Icon>"
            "</kml:IconStyle>"
            '<kml:LineStyle id="id-l0" targetId="target-l0">'
            "<kml:color>ff0000ff</kml:color>"
            "<kml:colorMode>normal</kml:colorMode>"
            "<kml:width>1.0</kml:width>"
            "</kml:LineStyle>"
            '<kml:BalloonStyle id="id-b0" targetId="target-b0">'
            "<kml:bgColor>7fff0000</kml:bgColor>"
            "<kml:textColor>ff00ff00</kml:textColor>"
            "<kml:text>&lt;b&gt;Hello&lt;/b&gt;</kml:text>"
            "<kml:displayMode>hide</kml:displayMode>"
            "</kml:BalloonStyle>"
            '<kml:LabelStyle id="id-a0" targetId="target-a0">'
            "<kml:color>ff0000ff</kml:color>"
            "<kml:colorMode>random</kml:colorMode>"
            "<kml:scale>1.0</kml:scale>"
            "</kml:LabelStyle>"
            '<kml:PolyStyle id="id-p0" targetId="target-p0">'
            "<kml:color>ff0000ff</kml:color>"
            "<kml:colorMode>random</kml:colorMode>"
            "<kml:fill>0</kml:fill>"
            "<kml:outline>1</kml:outline>"
            "</kml:PolyStyle>"
            "</kml:Style>",
        )

        assert style.id == "id-0"
        assert style.target_id == "target-0"
        assert isinstance(style.styles[0], styles.BalloonStyle)
        assert style.styles[0].id == "id-b0"
        assert style.styles[0].target_id == "target-b0"
        assert style.styles[0].bg_color == "7fff0000"
        assert style.styles[0].text_color == "ff00ff00"
        assert style.styles[0].text == "<b>Hello</b>"
        assert style.styles[0].display_mode == DisplayMode.hide

        assert isinstance(style.styles[1], styles.IconStyle)
        assert style.styles[1].id == "id-i0"
        assert style.styles[1].target_id == "target-i0"
        assert style.styles[1].color == "ff0000ff"
        assert style.styles[1].color_mode == ColorMode.random
        assert style.styles[1].scale == 1.0
        assert style.styles[1].heading == 0
        assert style.styles[1].icon.href == "http://example.com/icon.png"

        assert isinstance(style.styles[2], styles.LabelStyle)
        assert style.styles[2].id == "id-a0"
        assert style.styles[2].target_id == "target-a0"
        assert style.styles[2].color == "ff0000ff"
        assert style.styles[2].color_mode == ColorMode.random
        assert style.styles[2].scale == 1.0

        assert isinstance(style.styles[3], styles.LineStyle)
        assert style.styles[3].id == "id-l0"
        assert style.styles[3].target_id == "target-l0"
        assert style.styles[3].color == "ff0000ff"
        assert style.styles[3].color_mode == ColorMode.normal
        assert style.styles[3].width == 1.0

        assert isinstance(style.styles[4], styles.PolyStyle)
        assert style.styles[4].id == "id-p0"
        assert style.styles[4].target_id == "target-p0"
        assert style.styles[4].color == "ff0000ff"
        assert style.styles[4].color_mode == ColorMode.random
        assert style.styles[4].fill == 0
        assert style.styles[4].outline == 1

    def test_stylemap(self) -> None:  # noqa: PLR0915
        url = styles.StyleUrl(id="id-0", url="#style-0", target_id="target-0")
        icons = styles.IconStyle(
            id="id-i0",
            target_id="target-i0",
            color="ff0000ff",
            color_mode=ColorMode.random,
            scale=1.0,
            heading=0,
            icon=links.Icon(href="http://example.com/icon.png"),
        )
        lines = styles.LineStyle(
            id="id-l0",
            target_id="target-l0",
            color="ff0000ff",
            color_mode=ColorMode.normal,
            width=1.0,
        )
        bs = styles.BalloonStyle(
            id="id-b0",
            target_id="target-b0",
            bg_color="7fff0000",
            text_color="ff00ff00",
            text="<b>Hello</b>",
            display_mode=DisplayMode.hide,
        )
        ls = styles.LabelStyle(
            id="id-a0",
            target_id="target-a0",
            color="ff0000ff",
            color_mode=ColorMode.random,
            scale=1.0,
        )
        ps = styles.PolyStyle(
            id="id-p0",
            target_id="target-p0",
            color="ff0000ff",
            color_mode=ColorMode.random,
            fill=False,
            outline=True,
        )
        style = styles.Style(
            id="id-0",
            target_id="target-0",
            styles=[icons, lines, bs, ls, ps],
        )
        sm = styles.StyleMap(
            id="id-sm-0",
            target_id="target-sm-0",
            pairs=[
                styles.Pair(key=PairKey.normal, style=url),
                styles.Pair(key=PairKey.highlight, style=style),
            ],
        )

        serialized = sm.to_string()

        assert '<kml:StyleMap xmlns:kml="http://www.opengis.net/kml/2.2" ' in serialized
        assert 'id="id-sm-0"' in serialized
        assert 'targetId="target-sm-0"' in serialized
        assert "<kml:Pair>" in serialized
        assert "<kml:key>normal</kml:key>" in serialized
        assert "<kml:styleUrl " in serialized
        assert "</kml:Pair>" in serialized
        assert "<kml:Pair>" in serialized
        assert "<kml:key>highlight</kml:key>" in serialized
        assert "<kml:Style " in serialized
        assert "<kml:IconStyle " in serialized
        assert "<kml:color>ff0000ff</kml:color>" in serialized
        assert "<kml:colorMode>random</kml:colorMode>" in serialized
        assert "<kml:scale>1.0</kml:scale>" in serialized
        assert "<kml:heading>0</kml:heading>" in serialized
        assert "<kml:Icon>" in serialized
        assert "<kml:href>http://example.com/icon.png</kml:href>" in serialized
        assert "</kml:Icon>" in serialized
        assert "</kml:IconStyle>" in serialized
        assert "<kml:LineStyle " in serialized
        assert "<kml:color>ff0000ff</kml:color>" in serialized
        assert "<kml:colorMode>normal</kml:colorMode>" in serialized
        assert "<kml:width>1.0</kml:width>" in serialized
        assert "</kml:LineStyle>" in serialized
        assert "<kml:BalloonStyle " in serialized
        assert "<kml:bgColor>7fff0000</kml:bgColor>" in serialized
        assert "<kml:textColor>ff00ff00</kml:textColor>" in serialized
        assert "<kml:text>&lt;b&gt;Hello&lt;/b&gt;</kml:text>" in serialized
        assert "<kml:displayMode>hide</kml:displayMode>" in serialized
        assert "</kml:BalloonStyle>" in serialized
        assert "<kml:LabelStyle " in serialized
        assert "<kml:color>ff0000ff</kml:color>" in serialized
        assert "<kml:colorMode>random</kml:colorMode>" in serialized
        assert "<kml:scale>1.0</kml:scale>" in serialized
        assert "</kml:LabelStyle>" in serialized
        assert "<kml:PolyStyle " in serialized
        assert "<kml:color>ff0000ff</kml:color>" in serialized
        assert "<kml:colorMode>random</kml:colorMode>" in serialized
        assert "<kml:fill>0</kml:fill>" in serialized
        assert "<kml:outline>1</kml:outline>" in serialized
        assert "</kml:PolyStyle>" in serialized
        assert "</kml:Style>" in serialized
        assert "</kml:Pair>" in serialized
        assert "</kml:StyleMap>" in serialized

    def test_stylemap_read(self) -> None:
        sm = styles.StyleMap.from_string(
            """
            <kml:StyleMap xmlns:kml="http://www.opengis.net/kml/2.2"
            id="id-sm-0" targetId="target-sm-0">
            <kml:Pair>
                <kml:key>highlight</kml:key>
                <kml:styleUrl id="id-u0" targetId="target-u0">#style-0</kml:styleUrl>
            </kml:Pair>
            <kml:Pair>
                <kml:key>normal</kml:key>
                <kml:Style id="id-0" targetId="target-0">
                    <kml:IconStyle id="id-i0" targetId="target-i0">
                        <kml:color>ff0000ff</kml:color>
                        <kml:colorMode>random</kml:colorMode>
                        <kml:scale>1.0</kml:scale>
                        <kml:heading>0</kml:heading>
                        <kml:Icon>
                            <kml:href>http://example.com/icon.png</kml:href>
                        </kml:Icon>
                    </kml:IconStyle>
                    <kml:LineStyle id="id-l0" targetId="target-l0">
                        <kml:color>ff0000ff</kml:color>
                        <kml:colorMode>normal</kml:colorMode>
                        <kml:width>1.0</kml:width>
                    </kml:LineStyle>
                    <kml:BalloonStyle id="id-b0" targetId="target-b0">
                        <kml:bgColor>7fff0000</kml:bgColor>
                        <kml:textColor>ff00ff00</kml:textColor>
                        <kml:text>&lt;b&gt;Hello&lt;/b&gt;</kml:text>
                        <kml:displayMode>hide</kml:displayMode>
                    </kml:BalloonStyle>
                    <kml:LabelStyle id="id-a0" targetId="target-a0">
                        <kml:color>ff0000ff</kml:color>
                        <kml:colorMode>random</kml:colorMode>
                        <kml:scale>1.0</kml:scale>
                    </kml:LabelStyle>
                    <kml:PolyStyle id="id-p0" targetId="target-p0">
                        <kml:color>ff0000ff</kml:color>
                        <kml:colorMode>random</kml:colorMode>
                        <kml:fill>0</kml:fill>
                        <kml:outline>1</kml:outline>
                    </kml:PolyStyle>
                </kml:Style>
            </kml:Pair>
            </kml:StyleMap>
        """,
        )

        assert sm.id == "id-sm-0"
        assert sm.target_id == "target-sm-0"
        assert sm.normal.id == "id-0"
        assert sm.normal.target_id == "target-0"
        assert sm.highlight.id == "id-u0"
        assert sm.highlight.target_id == "target-u0"

    def test_style_map_none_case(self) -> None:
        sm = styles.StyleMap()

        assert sm.normal is None
        assert sm.highlight is None


class TestStyleUsage:
    def test_create_document_style(self) -> None:
        style = styles.Style(
            styles=[
                styles.PolyStyle(
                    color="7f000000",
                    fill=True,
                    outline=True,
                ),
            ],
        )

        doc = kml.Document(styles=[style])

        doc2 = kml.Document()
        doc2.styles.append(style)

        expected = """
            <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2">
              <kml:visibility/>
                <kml:Style>
                  <kml:PolyStyle>
                    <kml:color>7f000000</kml:color>
                    <kml:fill>1</kml:fill>
                    <kml:outline>1</kml:outline>
                  </kml:PolyStyle>
                </kml:Style>
            </kml:Document>
        """

        doc3 = kml.Document.from_string(expected)

        assert doc.to_string() == doc2.to_string()
        assert doc2.to_string() == doc3.to_string()
        assert doc.to_string() == doc3.to_string()

    def test_create_placemark_style(self) -> None:
        style = styles.Style(
            styles=[
                styles.PolyStyle(
                    color="7f000000",
                    fill=True,
                    outline=True,
                ),
            ],
        )

        place = kml.Placemark(styles=[style])

        place2 = kml.Placemark()
        place2.styles.append(style)

        expected = """
            <kml:Placemark xmlns:kml="http://www.opengis.net/kml/2.2">
                <kml:Style>
                  <kml:PolyStyle>
                    <kml:color>7f000000</kml:color>
                    <kml:fill>1</kml:fill>
                    <kml:outline>1</kml:outline>
                  </kml:PolyStyle>
                </kml:Style>
            </kml:Placemark>
        """

        place3 = kml.Placemark.from_string(expected)
        assert place.to_string() == place2.to_string()
        assert place2.to_string() == place3.to_string()
        assert place.to_string() == place3.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
