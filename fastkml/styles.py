# -*- coding: utf-8 -*-
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

"""
Once you've created features within Google Earth and examined the KML
code Google Earth generates, you'll notice how styles are an important
part of how your data is displayed.
"""

import logging
logger = logging.getLogger('fastkml.styles')

import config
from config import etree
from base import _BaseObject




class StyleUrl(_BaseObject):
    """
    URL of a <Style> or <StyleMap> defined in a Document. If the style
    is in the same file, use a # reference. If the style is defined in
    an external file, use a full URL along with # referencing.
    """
    __name__ = 'styleUrl'
    url = None

    def __init__(self, ns=None, id=None, url=None):
        super(StyleUrl, self).__init__(ns, id)
        self.url = url

    def etree_element(self):
        if self.url:
            element = super(StyleUrl, self).etree_element()
            element.text = self.url
            return element
        else:
            raise ValueError('No url given for styleUrl')

    def from_element(self, element):
        super(StyleUrl, self).from_element(element)
        self.url = element.text


class _StyleSelector(_BaseObject):
    """
    This is an abstract element and cannot be used directly in a KML file.
    It is the base type for the <Style> and <StyleMap> elements. The
    StyleMap element selects a style based on the current mode of the
    Placemark. An element derived from StyleSelector is uniquely identified
    by its id and its url.
    """


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
    _styles = None

    def __init__(self, ns=None, id=None, styles = None):
        super(Style, self).__init__(ns, id)
        self._styles = []
        if styles:
            for style in styles:
                self.append_style(style)

    def append_style(self, style):
        if isinstance(style, _ColorStyle):
            self._styles.append(style)
        else:
            raise TypeError

    def styles(self):
        for style in self._styles:
            if isinstance(style, (_ColorStyle, BalloonStyle)):
                yield style
            else:
                raise TypeError

    def from_element(self, element):
        super(Style, self).from_element(element)
        style = element.find('%sIconStyle' %self.ns)
        if style is not None:
            thestyle = IconStyle(self.ns)
            thestyle.from_element(style)
            self.append_style(thestyle)
        style = element.find('%sLineStyle' %self.ns)
        if style is not None:
            thestyle = LineStyle(self.ns)
            thestyle.from_element(style)
            self.append_style(thestyle)
        style = element.find('%sPolyStyle' %self.ns)
        if style is not None:
            thestyle = PolyStyle(self.ns)
            thestyle.from_element(style)
            self.append_style(thestyle)
        style = element.find('%sLabelStyle' %self.ns)
        if style is not None:
            thestyle = LabelStyle(self.ns)
            thestyle.from_element(style)
            self.append_style(thestyle)
        #XXX BalloonStyle

    def etree_element(self):
        element = super(Style, self).etree_element()
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

    def __init__(self, ns=None, id=None, normal=None, highlight=None):
        super(StyleMap, self).__init__(ns, id)
        pass


    def from_element(self, element):
        super(StyleMap, self).from_element(element)
        pairs = element.findall('%sPair' %self.ns)
        for pair in pairs:
            key = pair.find('%skey' %self.ns)
            style = pair.find('%sStyle' %self.ns)
            style_url = pair.find('%sstyleUrl' %self.ns)
            if key.text == "highlight":
                if style is not None:
                    highlight = Style(self.ns)
                    highlight.from_element(style)
                elif style_url is not None:
                    highlight = StyleUrl(self.ns)
                    highlight.from_element(style_url)
                else:
                    raise ValueError
                self.highlight = highlight
            elif key.text == "normal":
                if style is not None:
                    normal = Style(self.ns)
                    normal.from_element(style)
                elif style_url is not None:
                    normal = StyleUrl(self.ns)
                    normal.from_element(style_url)
                else:
                    raise ValueError
                self.normal = normal
            else:
                raise ValueError



    def etree_element(self):
        element = super(StyleMap, self).etree_element()
        if self.normal:
            if isinstance(self.normal, (Style, StyleUrl)):
                pair = etree.SubElement(element, "%sPair" %self.ns)
                key = etree.SubElement(pair, "%skey" %self.ns)
                key.text = 'normal'
                pair.append(self.normal.etree_element())
        if self.highlight:
            if isinstance(self.highlight, (Style, StyleUrl)):
                pair = etree.SubElement(element, "%sPair" %self.ns)
                key = etree.SubElement(pair, "%skey" %self.ns)
                key.text = 'highlight'
                pair.append(self.normal.etree_element())
        return element


class _ColorStyle(_BaseObject):
    """
    abstract element; do not create.
    This is an abstract element and cannot be used directly in a KML file.
    It provides elements for specifying the color and color mode of
    extended style types.
    subclasses are: IconStyle, LabelStyle, LineStyle, PolyStyle
    """
    id = None
    ns = None
    color = None
    # Color and opacity (alpha) values are expressed in hexadecimal notation.
    # The range of values for any one color is 0 to 255 (00 to ff).
    # For alpha, 00 is fully transparent and ff is fully opaque.
    # The order of expression is aabbggrr, where aa=alpha (00 to ff);
    # bb=blue (00 to ff); gg=green (00 to ff); rr=red (00 to ff).

    colorMode = None
    # Values for <colorMode> are normal (no effect) and random.
    # A value of random applies a random linear scale to the base <color>

    def __init__(self, ns=None, id=None, color=None, colorMode=None):
        super(_ColorStyle, self).__init__(ns, id)
        self.color = color
        self.colorMode = colorMode


    def etree_element(self):
        element = super(_ColorStyle, self).etree_element()
        if self.color:
            color = etree.SubElement(element, "%scolor" %self.ns)
            color.text = self.color
        if self.colorMode:
            colorMode = etree.SubElement(element, "%scolorMode" %self.ns)
            colorMode.text = self.colorMode
        return element


    def from_element(self, element):
        if self.ns + self.__name__ != element.tag:
            raise TypeError
        else:
            if element.get('id'):
                self.id = element.get('id')
            colorMode = element.find('%scolorMode' %self.ns)
            if colorMode is not None:
                self.colorMode = colorMode.text
            color = element.find('%scolor' %self.ns)
            if color is not None:
                self.color = color.text

class IconStyle(_ColorStyle):
    """ Specifies how icons for point Placemarks are drawn """
    __name__ = "IconStyle"
    scale = 1.0
    # Resizes the icon. (float)
    heading = None
    # Direction (that is, North, South, East, West), in degrees.
    # Default=0 (North).
    icon_href = None
    # An HTTP address or a local file specification used to load an icon.

    def __init__(self, ns=None, id=None, color=None, colorMode=None,
                scale=1.0, heading=None, icon_href=None):
        super(IconStyle, self).__init__(ns, id, color, colorMode)
        self.scale = scale
        self.heading = heading
        self.icon_href = icon_href

    def etree_element(self):
        element = super(IconStyle, self).etree_element()
        if self.scale is not None:
            scale = etree.SubElement(element, "%sscale" %self.ns)
            scale.text = str(self.scale)
        if self.heading:
            heading = etree.SubElement(element, "%sheading" %self.ns)
            heading.text = str(self.heading)
        if self.icon_href:
            icon = etree.SubElement(element, "%sIcon" %self.ns)
            href = etree.SubElement(icon, "%shref" %self.ns)
            href.text = self.icon_href
        return element

    def from_element(self, element):
        super(IconStyle, self).from_element(element)
        scale = element.find('%sscale' %self.ns)
        if scale is not None:
            self.scale = float(scale.text)
        heading = element.find('%sheading' %self.ns)
        if heading is not None:
            self.heading = float(heading.text)
        icon = element.find('%sIcon' %self.ns)
        if icon is not None:
            href = icon.find('%shref' %self.ns)
            if href is not None:
                self.icon_href = href.text



class LineStyle(_ColorStyle):
    """
    Specifies the drawing style (color, color mode, and line width)
    for all line geometry. Line geometry includes the outlines of
    outlined polygons and the extruded "tether" of Placemark icons
    (if extrusion is enabled).
    """
    __name__ = "LineStyle"
    width = 1
    # Width of the line, in pixels.

    def __init__(self, ns=None, id=None, color=None, colorMode=None,
                width=1):
        super(LineStyle, self).__init__(ns, id, color, colorMode)
        self.width = width

    def etree_element(self):
        element = super(LineStyle, self).etree_element()
        if self.width is not None:
            width = etree.SubElement(element, "%swidth" %self.ns)
            width.text = str(self.width)
        return element

    def from_element(self, element):
        super(LineStyle, self).from_element(element)
        width = element.find('%swidth' %self.ns)
        if width is not None:
            self.width = int(width.text)

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

    def __init__(self, ns=None, id=None, color=None, colorMode=None,
                fill=1, outline=1):
        super(PolyStyle, self).__init__(ns, id, color, colorMode)
        self.fill = fill
        self.outline = outline

    def etree_element(self):
        element = super(PolyStyle, self).etree_element()
        if self.fill is not None:
            fill = etree.SubElement(element, "%sfill" %self.ns)
            fill.text = str(self.fill)
        if self.outline is not None:
            outline = etree.SubElement(element, "%soutline" %self.ns)
            outline.text = str(self.outline)
        return element

    def from_element(self, element):
        super(PolyStyle, self).from_element(element)
        fill = element.find('%sfill' %self.ns)
        if fill is not None:
            self.fill = int(fill.text)
        outline = element.find('%soutline' %self.ns)
        if outline is not None:
            self.outline = int(outline.text)


class LabelStyle(_ColorStyle):
    """
    Specifies how the <name> of a Feature is drawn in the 3D viewer
    """
    __name__ = "LabelStyle"
    scale = 1.0
    # Resizes the label.

    def __init__(self, ns=None, id=None, color=None, colorMode=None,
                scale=1.0):
        super(LabelStyle, self).__init__(ns, id, color, colorMode)
        self.scale = scale

    def etree_element(self):
        element = super(LabelStyle, self).etree_element()
        if self.scale is not None:
            scale = etree.SubElement(element, "%sscale" %self.ns)
            scale.text = str(self.scale)
        return element

    def from_element(self, element):
        super(LabelStyle, self).from_element(element)
        scale = element.find('%sscale' %self.ns)
        if scale is not None:
            self.scale = float(scale.text)

class BalloonStyle(_BaseObject):
    """ Specifies how the description balloon for placemarks is drawn.
        The <bgColor>, if specified, is used as the background color of
        the balloon."""
    pass
