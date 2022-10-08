# Copyright (C) 2012 - 2022  Christian Ledermann
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

"""
Once you've created features within Google Earth and examined the KML
code Google Earth generates, you'll notice how styles are an important
part of how your data is displayed.
"""

import logging
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from typing_extensions import TypedDict

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.types import Element

logger = logging.getLogger(__name__)


class StyleUrl(_BaseObject):
    """
    URL of a <Style> or <StyleMap> defined in a Document. If the style
    is in the same file, use a # reference. If the style is defined in
    an external file, use a full URL along with # referencing.
    """

    __name__ = "styleUrl"
    url = None

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        self.url = url

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.url:
            element.text = self.url
        else:
            logger.warning("StyleUrl is missing required url.")
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        self.url = element.text


class _StyleSelector(_BaseObject):
    """
    This is an abstract element and cannot be used directly in a KML file.
    It is the base type for the <Style> and <StyleMap> elements. The
    StyleMap element selects a style based on the current mode of the
    Placemark. An element derived from StyleSelector is uniquely identified
    by its id and its url.
    """


class _ColorStyle(_BaseObject):
    """
    abstract element; do not create.
    This is an abstract element and cannot be used directly in a KML file.
    It provides elements for specifying the color and color mode of
    extended style types.
    subclasses are: IconStyle, LabelStyle, LineStyle, PolyStyle
    """

    id = None
    color = None
    # Color and opacity (alpha) values are expressed in hexadecimal notation.
    # The range of values for any one color is 0 to 255 (00 to ff).
    # For alpha, 00 is fully transparent and ff is fully opaque.
    # The order of expression is aabbggrr, where aa=alpha (00 to ff);
    # bb=blue (00 to ff); gg=green (00 to ff); rr=red (00 to ff).

    color_mode = None
    # Values for <colorMode> are normal (no effect) and random.
    # A value of random applies a random linear scale to the base <color>

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[str] = None,
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        self.color = color
        self.color_mode = color_mode

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.color:
            color = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}color",
            )
            color.text = self.color
        if self.color_mode:
            color_mode = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}colorMode",
            )
            color_mode.text = self.color_mode
        return element

    def from_element(self, element: Element) -> None:

        super().from_element(element)
        color_mode = element.find(f"{self.ns}colorMode")
        if color_mode is not None:
            self.color_mode = color_mode.text
        color = element.find(f"{self.ns}color")
        if color is not None:
            self.color = color.text


class HotSpot(TypedDict):
    x: float
    y: float
    xunits: str  # pixels, fraction, insetPixels
    yunits: str


class IconStyle(_ColorStyle):
    """Specifies how icons for point Placemarks are drawn"""

    __name__ = "IconStyle"
    scale = 1.0
    # Resizes the icon. (float)
    heading = None
    # Direction (that is, North, South, East, West), in degrees.
    # Default=0 (North).
    icon_href = None
    # An HTTP address or a local file specification used to load an icon.
    hot_spot = None

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[str] = None,
        scale: float = 1.0,
        heading: Optional[float] = None,
        icon_href: Optional[str] = None,
        hot_spot: Optional[HotSpot] = None,
    ) -> None:
        super().__init__(
            ns=ns, id=id, target_id=target_id, color=color, color_mode=color_mode
        )

        self.scale = scale
        self.heading = heading
        self.icon_href = icon_href
        self.hot_spot = hot_spot

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.scale is not None:
            scale = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}scale",
            )
            scale.text = str(self.scale)
        if self.heading is not None:
            heading = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}heading",
            )
            heading.text = str(self.heading)
        if self.icon_href:
            icon = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}Icon",
            )
            href = config.etree.SubElement(  # type: ignore[attr-defined]
                icon,
                f"{self.ns}href",
            )
            href.text = self.icon_href
        if self.hot_spot:
            hot_spot = config.etree.SubElement(  # type: ignore[attr-defined]
                element, f"{self.ns}hotSpot"
            )
            hot_spot.attrib["x"] = str(self.hot_spot["x"])
            hot_spot.attrib["y"] = str(self.hot_spot["y"])
            hot_spot.attrib["xunits"] = str(self.hot_spot["xunits"])
            hot_spot.attrib["yunits"] = str(self.hot_spot["yunits"])
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        scale = element.find(f"{self.ns}scale")
        if scale is not None:
            self.scale = float(scale.text)
        heading = element.find(f"{self.ns}heading")
        if heading is not None:
            self.heading = float(heading.text)
        icon = element.find(f"{self.ns}Icon")
        if icon is not None:
            href = icon.find(f"{self.ns}href")
            if href is not None:
                self.icon_href = href.text
        hot_spot = element.find(f"{self.ns}hotSpot")
        if hot_spot is not None:
            self.hot_spot: HotSpot = {  # type: ignore[no-redef]
                "x": hot_spot.attrib["x"],  # type: ignore[attr-defined]
                "y": hot_spot.attrib["y"],  # type: ignore[attr-defined]
                "xunits": hot_spot.attrib["xunits"],  # type: ignore[attr-defined]
                "yunits": hot_spot.attrib["yunits"],  # type: ignore[attr-defined]
            }


class LineStyle(_ColorStyle):
    """
    Specifies the drawing style (color, color mode, and line width)
    for all line geometry. Line geometry includes the outlines of
    outlined polygons and the extruded "tether" of Placemark icons
    (if extrusion is enabled).
    """

    __name__ = "LineStyle"
    width = 1.0
    # Width of the line, in pixels.

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[str] = None,
        width: Union[int, float] = 1,
    ) -> None:
        super().__init__(
            ns=ns, id=id, target_id=target_id, color=color, color_mode=color_mode
        )
        self.width = width

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.width is not None:
            width = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}width",
            )
            width.text = str(self.width)
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        width = element.find(f"{self.ns}width")
        if width is not None:
            self.width = float(width.text)


class PolyStyle(_ColorStyle):
    """
    Specifies the drawing style for all polygons, including polygon
    extrusions (which look like the walls of buildings) and line
    extrusions (which look like solid fences).
    """

    __name__ = "PolyStyle"
    fill = 1
    # Boolean value. Specifies whether to fill the polygon.
    outline = 1
    # Boolean value. Specifies whether to outline the polygon.
    # Polygon outlines use the current LineStyle.

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[str] = None,
        fill: int = 1,
        outline: int = 1,
    ) -> None:
        super().__init__(
            ns=ns, id=id, target_id=target_id, color=color, color_mode=color_mode
        )
        self.fill = fill
        self.outline = outline

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.fill is not None:
            fill = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}fill",
            )
            fill.text = str(self.fill)
        if self.outline is not None:
            outline = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}outline",
            )
            outline.text = str(self.outline)
        return element

    def from_element(self, element: Element) -> None:
        def strtobool(val: str) -> int:
            val = val.lower()
            if val == "false":
                return 0
            if val == "true":
                return 1
            return int(float(val))

        super().from_element(element)
        fill = element.find(f"{self.ns}fill")
        if fill is not None:
            self.fill = strtobool(fill.text)
        outline = element.find(f"{self.ns}outline")
        if outline is not None:
            self.outline = strtobool(outline.text)


class LabelStyle(_ColorStyle):
    """
    Specifies how the <name> of a Feature is drawn in the 3D viewer.
    """

    __name__ = "LabelStyle"
    scale = 1.0
    # Resizes the label.

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[str] = None,
        scale: float = 1.0,
    ) -> None:
        super().__init__(
            ns=ns, id=id, target_id=target_id, color=color, color_mode=color_mode
        )
        self.scale = scale

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.scale is not None:
            scale = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}scale",
            )
            scale.text = str(self.scale)
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        scale = element.find(f"{self.ns}scale")
        if scale is not None:
            self.scale = float(scale.text)


class BalloonStyle(_BaseObject):
    """Specifies how the description balloon for placemarks is drawn.
    The <bgColor>, if specified, is used as the background color of
    the balloon."""

    __name__ = "BalloonStyle"

    bg_color = None
    # Background color of the balloon (optional). Color and opacity (alpha)
    # values are expressed in hexadecimal notation. The range of values for
    # any one color is 0 to 255 (00 to ff). The order of expression is
    # aabbggrr, where aa=alpha (00 to ff); bb=blue (00 to ff);
    # gg=green (00 to ff); rr=red (00 to ff).
    # For alpha, 00 is fully transparent and ff is fully opaque.
    # For example, if you want to apply a blue color with 50 percent
    # opacity to an overlay, you would specify the following:
    # <bgColor>7fff0000</bgColor>, where alpha=0x7f, blue=0xff, green=0x00,
    # and red=0x00. The default is opaque white (ffffffff).
    # Note: The use of the <color> element within <BalloonStyle> has been
    # deprecated. Use <bgColor> instead.

    text_color = None
    # Foreground color for text. The default is black (ff000000).

    text = None
    # Text displayed in the balloon. If no text is specified, Google Earth
    # draws the default balloon (with the Feature <name> in boldface,
    # the Feature <description>, links for driving directions, a white
    # background, and a tail that is attached to the point coordinates of
    # the Feature, if specified).
    # You can add entities to the <text> tag using the following format to
    # refer to a child element of Feature: $[name], $[description], $[address],
    # $[id], $[Snippet]. Google Earth looks in the current Feature for the
    # corresponding string entity and substitutes that information in the
    # balloon.
    # To include To here - From here driving directions in the balloon,
    # use the $[geDirections] tag. To prevent the driving directions links
    # from appearing in a balloon, include the <text> element with some content
    # or with $[description] to substitute the basic Feature <description>.
    # For example, in the following KML excerpt, $[name] and $[description]
    # fields will be replaced by the <name> and <description> fields found
    # in the Feature elements that use this BalloonStyle:
    # <text>This is $[name], whose description is:<br/>$[description]</text>

    display_mode = None
    # If <displayMode> is default, Google Earth uses the information supplied
    # in <text> to create a balloon . If <displayMode> is hide, Google Earth
    # does not display the balloon. In Google Earth, clicking the List View
    # icon for a Placemark whose balloon's <displayMode> is hide causes
    # Google Earth to fly to the Placemark.

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None,
        text: Optional[str] = None,
        display_mode: Optional[str] = None,
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        self.bg_color = bg_color
        self.text_color = text_color
        self.text = text
        self.display_mode = display_mode

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        bg_color = element.find(f"{self.ns}bgColor")
        if bg_color is not None:
            self.bg_color = bg_color.text
        else:
            bg_color = element.find(f"{self.ns}color")  # type: ignore[unreachable]
            if bg_color is not None:
                self.bg_color = bg_color.text
        text_color = element.find(f"{self.ns}textColor")
        if text_color is not None:
            self.text_color = text_color.text
        text = element.find(f"{self.ns}text")
        if text is not None:
            self.text = text.text
        display_mode = element.find(f"{self.ns}displayMode")
        if display_mode is not None:
            self.display_mode = display_mode.text

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.bg_color is not None:
            elem = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}bgColor",
            )
            elem.text = self.bg_color
        if self.text_color is not None:
            elem = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}textColor",
            )
            elem.text = self.text_color
        if self.text is not None:
            elem = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}text",
            )
            elem.text = self.text
        if self.display_mode is not None:
            elem = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}displayMode",
            )
            elem.text = self.display_mode
        return element


AnyStyle = Union[BalloonStyle, IconStyle, LabelStyle, LineStyle, PolyStyle]


class Style(_StyleSelector):
    """
    A Style defines an addressable style group that can be referenced
    by StyleMaps and Features. Styles affect how Geometry is presented
    in the 3D viewer and how Features appear in the Places panel of the
    List view. Shared styles are collected in a <Document> and must have
    an id defined for them so that they can be referenced by the
    individual Features that use them.
    """

    __name__ = "Style"

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        styles: Optional[Iterable[AnyStyle]] = None,
    ) -> None:
        super().__init__(ns, id, target_id)
        self._styles: List[AnyStyle] = []
        if styles:
            for style in styles:
                self.append_style(style)

    def append_style(
        self,
        style: AnyStyle,
    ) -> None:
        if isinstance(style, (_ColorStyle, BalloonStyle)):
            self._styles.append(style)
        else:
            raise TypeError

    def styles(
        self,
    ) -> Iterator[AnyStyle]:
        for style in self._styles:
            if isinstance(style, (_ColorStyle, BalloonStyle)):
                yield style
            else:
                raise TypeError

    def _get_style(self, element: Element, style_class: Type[AnyStyle]) -> None:
        style = element.find(f"{self.ns}{style_class.__name__}")
        if style is not None:
            thestyle = style_class(self.ns)
            thestyle.from_element(style)
            self.append_style(thestyle)

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        for style in [BalloonStyle, IconStyle, LabelStyle, LineStyle, PolyStyle]:
            self._get_style(element, style)

    def etree_element(self) -> Element:
        element = super().etree_element()
        for style in self.styles():
            element.append(style.etree_element())
        return element


class StyleMap(_StyleSelector):
    """
    A <StyleMap> maps between two different Styles. Typically a
    <StyleMap> element is used to provide separate normal and highlighted
    styles for a placemark, so that the highlighted version appears when
    the user mouses over the icon in Google Earth.
    """

    __name__ = "StyleMap"
    normal = None
    highlight = None

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        normal: Optional[Union[Style, StyleUrl]] = None,
        highlight: Optional[Union[Style, StyleUrl]] = None,
    ) -> None:
        super().__init__(ns, id, target_id)
        self.normal = normal
        self.highlight = highlight

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        pairs = element.findall(f"{self.ns}Pair")
        for pair in pairs:
            key = pair.find(f"{self.ns}key")
            style = pair.find(f"{self.ns}Style")
            style_url = pair.find(f"{self.ns}styleUrl")
            if key.text == "highlight":
                if style is not None:
                    highlight = Style(self.ns)
                    highlight.from_element(style)
                elif style_url is not None:  # type: ignore[unreachable]
                    highlight = StyleUrl(self.ns)
                    highlight.from_element(style_url)
                else:
                    raise ValueError
                self.highlight = highlight
            elif key.text == "normal":
                if style is not None:
                    normal = Style(self.ns)
                    normal.from_element(style)
                elif style_url is not None:  # type: ignore[unreachable]
                    normal = StyleUrl(self.ns)
                    normal.from_element(style_url)
                else:
                    raise ValueError
                self.normal = normal
            else:
                raise ValueError

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.normal and isinstance(self.normal, (Style, StyleUrl)):
            pair = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}Pair",
            )
            key = config.etree.SubElement(  # type: ignore[attr-defined]
                pair,
                f"{self.ns}key",
            )
            key.text = "normal"
            pair.append(self.normal.etree_element())
        if self.highlight and isinstance(self.highlight, (Style, StyleUrl)):
            pair = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}Pair",
            )
            key = config.etree.SubElement(  # type: ignore[attr-defined]
                pair,
                f"{self.ns}key",
            )
            key.text = "highlight"
            pair.append(self.highlight.etree_element())
        return element


__all__ = [
    "BalloonStyle",
    "IconStyle",
    "LabelStyle",
    "LineStyle",
    "PolyStyle",
    "Style",
    "StyleMap",
    "StyleUrl",
]
