# Copyright (C) 2012  Christian Ledermann
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
KML is an open standard officially named the OpenGIS KML Encoding Standard
(OGC KML). It is maintained by the Open Geospatial Consortium, Inc. (OGC).
The complete specification for OGC KML can be found at
http://www.opengeospatial.org/standards/kml/.

The complete XML schema for KML is located at
http://schemas.opengis.net/kml/.

"""
import logging
import urllib.parse as urlparse
from datetime import date
from datetime import datetime

# note that there are some ISO 8601 timeparsers at pypi
# but in my tests all of them had some errors so we rely on the
# tried and tested dateutil here which is more stable. As a side effect
# we can also parse non ISO compliant dateTimes
import dateutil.parser

import fastkml.atom as atom
import fastkml.config as config
import fastkml.gx as gx

from .base import _BaseObject
from .base import _XMLObject
from .config import etree
from .geometry import Geometry
from .styles import Style
from .styles import StyleMap
from .styles import StyleUrl
from .styles import _StyleSelector

logger = logging.getLogger(__name__)


class KML:
    """represents a KML File"""

    _features = []
    ns = None

    def __init__(self, ns=None):
        """The namespace (ns) may be empty ('') if the 'kml:' prefix is
        undesired. Note that all child elements like Document or Placemark need
        to be initialized with empty namespace as well in this case.

        """
        self._features = []

        self.ns = config.KMLNS if ns is None else ns

    def from_string(self, xml_string):
        """create a KML object from a xml string"""
        if config.LXML:
            element = etree.fromstring(
                xml_string, parser=etree.XMLParser(huge_tree=True, recover=True)
            )
        else:
            element = etree.XML(xml_string)

        if not element.tag.endswith("kml"):
            raise TypeError

        ns = element.tag.rstrip("kml")
        documents = element.findall(f"{ns}Document")
        for document in documents:
            feature = Document(ns)
            feature.from_element(document)
            self.append(feature)
        folders = element.findall(f"{ns}Folder")
        for folder in folders:
            feature = Folder(ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall(f"{ns}Placemark")
        for placemark in placemarks:
            feature = Placemark(ns)
            feature.from_element(placemark)
            self.append(feature)
        photo_overlays = element.findall(f"{ns}PhotoOverlay")
        for photo_overlay in photo_overlays:
            feature = PhotoOverlay(ns)
            feature.from_element(photo_overlay)
            self.append(feature)

    def etree_element(self):
        # self.ns may be empty, which leads to unprefixed kml elements.
        # However, in this case the xlmns should still be mentioned on the kml
        # element, just without prefix.
        if not self.ns:
            root = etree.Element(f"{self.ns}kml")
            root.set("xmlns", config.KMLNS[1:-1])
        elif config.LXML:
            root = etree.Element(f"{self.ns}kml", nsmap={None: self.ns[1:-1]})
        else:
            root = etree.Element(f"{self.ns}kml")
        for feature in self.features():
            root.append(feature.etree_element())
        return root

    def to_string(self, prettyprint=False):
        """Return the KML Object as serialized xml"""
        if config.LXML and prettyprint:
            return etree.tostring(
                self.etree_element(), encoding="utf-8", pretty_print=True
            ).decode("UTF-8")
        else:
            return etree.tostring(self.etree_element(), encoding="utf-8").decode(
                "UTF-8"
            )

    def features(self):
        """iterate over features"""
        for feature in self._features:
            if isinstance(
                feature, (Document, Folder, Placemark, GroundOverlay, PhotoOverlay)
            ):
                yield feature
            else:
                raise TypeError(
                    "Features must be instances of "
                    + "(Document, Folder, Placemark, GroundOverlay, PhotoOverlay)"
                )

    def append(self, kmlobj):
        """append a feature"""
        if isinstance(
            kmlobj, (Document, Folder, Placemark,
                     GroundOverlay, PhotoOverlay)
        ):
            self._features.append(kmlobj)
        else:
            raise TypeError(
                "Features must be instances of (Document, Folder, "
                + "Placemark, GroundOverlay, PhotoOverlay)"
            )


class _Feature(_BaseObject):
    """
    abstract element; do not create
    subclasses are:
        * Container (Document, Folder)
        * Placemark
        * Overlay
    Not Implemented Yet:
        * NetworkLink
    """

    name = None
    # User-defined text displayed in the 3D viewer as the label for the
    # object (for example, for a Placemark, Folder, or NetworkLink).

    visibility = 1
    # Boolean value. Specifies whether the feature is drawn in the 3D
    # viewer when it is initially loaded. In order for a feature to be
    # visible, the <visibility> tag of all its ancestors must also be
    # set to 1.

    isopen = 0
    # Boolean value. Specifies whether a Document or Folder appears
    # closed or open when first loaded into the Places panel.
    # 0=collapsed (the default), 1=expanded.

    _atom_author = None
    # KML 2.2 supports new elements for including data about the author
    # and related website in your KML file. This information is displayed
    # in geo search results, both in Earth browsers such as Google Earth,
    # and in other applications such as Google Maps.

    _atom_link = None
    # Specifies the URL of the website containing this KML or KMZ file.

    _address = None
    # A string value representing an unstructured address written as a
    # standard street, city, state address, and/or as a postal code.
    # You can use the <address> tag to specify the location of a point
    # instead of using latitude and longitude coordinates.

    _phone_number = None
    # A string value representing a telephone number.
    # This element is used by Google Maps Mobile only.

    _snippet = None  # XXX
    # _snippet is either a tuple of a string Snippet.text and an integer
    # Snippet.maxLines or a string
    #
    # A short description of the feature. In Google Earth, this
    # description is displayed in the Places panel under the name of the
    # feature. If a Snippet is not supplied, the first two lines of
    # the <description> are used. In Google Earth, if a Placemark
    # contains both a description and a Snippet, the <Snippet> appears
    # beneath the Placemark in the Places panel, and the <description>
    # appears in the Placemark's description balloon. This tag does not
    # support HTML markup. <Snippet> has a maxLines attribute, an integer
    # that specifies the maximum number of lines to display.

    description = None
    # User-supplied content that appears in the description balloon.

    _style_url = None
    # URL of a <Style> or <StyleMap> defined in a Document.
    # If the style is in the same file, use a # reference.
    # If the style is defined in an external file, use a full URL
    # along with # referencing.

    _styles = None
    # One or more Styles and StyleMaps can be defined to customize the
    # appearance of any element derived from Feature or of the Geometry
    # in a Placemark.
    # A style defined within a Feature is called an "inline style" and
    # applies only to the Feature that contains it. A style defined as
    # the child of a <Document> is called a "shared style." A shared
    # style must have an id defined for it. This id is referenced by one
    # or more Features within the <Document>. In cases where a style
    # element is defined both in a shared style and in an inline style
    # for a Feature—that is, a Folder, GroundOverlay, NetworkLink,
    # Placemark, or ScreenOverlay—the value for the Feature's inline
    # style takes precedence over the value for the shared style.

    _timespan = None
    # Associates this Feature with a period of time.
    _timestamp = None
    # Associates this Feature with a point in time.

    _camera = None

    _look_at = None

    # TODO Region = None
    # Features and geometry associated with a Region are drawn only when
    # the Region is active.

    # TODO ExtendedData = None
    # Allows you to add custom data to a KML file. This data can be
    # (1) data that references an external XML schema,
    # (2) untyped data/value pairs, or
    # (3) typed data.
    # A given KML Feature can contain a combination of these types of
    # custom data.
    #
    # (2) is already implemented, see UntypedExtendedData
    #
    # <Metadata> (deprecated in KML 2.2; use <ExtendedData> instead)
    extended_data = None

    def __init__(
        self,
        ns=None,
        id=None,
        name=None,
        description=None,
        styles=None,
        style_url=None,
        extended_data=None,
    ):
        super().__init__(ns, id)
        self.name = name
        self.description = description
        self.style_url = style_url
        self._styles = []
        if styles:
            for style in styles:
                self.append_style(style)
        self.extended_data = extended_data

    @property
    def style_url(self):
        """Returns the url only, not a full StyleUrl object.
        if you need the full StyleUrl object use _style_url"""
        if isinstance(self._style_url, StyleUrl):
            return self._style_url.url

    @style_url.setter
    def style_url(self, styleurl):
        """you may pass a StyleUrl Object, a string or None"""
        if isinstance(styleurl, StyleUrl):
            self._style_url = styleurl
        elif isinstance(styleurl, str):
            s = StyleUrl(self.ns, url=styleurl)
            self._style_url = s
        elif styleurl is None:
            self._style_url = None
        else:
            raise ValueError

    @property
    def timestamp(self):
        """This just returns the datetime portion of the timestamp"""
        if self._timestamp is not None:
            return self._timestamp.timestamp[0]

    @timestamp.setter
    def timestamp(self, dt):
        self._timestamp = None if dt is None else TimeStamp(timestamp=dt)
        if self._timespan is not None:
            logger.warning("Setting a TimeStamp, TimeSpan deleted")
            self._timespan = None

    @property
    def begin(self):
        if self._timespan is not None:
            return self._timespan.begin[0]

    @begin.setter
    def begin(self, dt):
        if self._timespan is None:
            self._timespan = TimeSpan(begin=dt)
        elif self._timespan.begin is None:
            self._timespan.begin = [dt, None]
        else:
            self._timespan.begin[0] = dt
        if self._timestamp is not None:
            logger.warning("Setting a TimeSpan, TimeStamp deleted")
            self._timestamp = None

    @property
    def end(self):
        if self._timespan is not None:
            return self._timespan.end[0]

    @end.setter
    def end(self, dt):
        if self._timespan is None:
            self._timespan = TimeSpan(end=dt)
        elif self._timespan.end is None:
            self._timespan.end = [dt, None]
        else:
            self._timespan.end[0] = dt
        if self._timestamp is not None:
            logger.warning("Setting a TimeSpan, TimeStamp deleted")
            self._timestamp = None

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, camera):
        if isinstance(camera, Camera):
            self._camera = camera

    @property
    def look_at(self):
        return self._look_at

    @look_at.setter
    def look_at(self, look_at):
        if isinstance(look_at, LookAt):
            self._look_at = look_at

    @property
    def link(self):
        return self._atom_link.href

    @link.setter
    def link(self, url):
        if isinstance(url, str):
            self._atom_link = atom.Link(href=url)
        elif isinstance(url, atom.Link):
            self._atom_link = url
        elif url is None:
            self._atom_link = None
        else:
            raise TypeError

    @property
    def author(self):
        if self._atom_author:
            return self._atom_author.name

    @author.setter
    def author(self, name):
        if isinstance(name, atom.Author):
            self._atom_author = name
        elif isinstance(name, str):
            if self._atom_author is None:
                self._atom_author = atom.Author(name=name)
            else:
                self._atom_author.name = name
        elif name is None:
            self._atom_author = None
        else:
            raise TypeError

    def append_style(self, style):
        """append a style to the feature"""
        if isinstance(style, _StyleSelector):
            self._styles.append(style)
        else:
            raise TypeError

    def styles(self):
        """iterate over the styles of this feature"""
        for style in self._styles:
            if isinstance(style, _StyleSelector):
                yield style
            else:
                raise TypeError

    @property
    def snippet(self):
        if not self._snippet:
            return
        if isinstance(self._snippet, dict):
            text = self._snippet.get("text")
            if text:
                assert isinstance(text, str)
                max_lines = self._snippet.get("maxLines", None)
                if max_lines is None:
                    return {"text": text}
                elif int(max_lines) > 0:
                    # if maxLines <=0 ignore it
                    return {"text": text, "maxLines": max_lines}
        elif isinstance(self._snippet, str):
            return self._snippet
        else:
            raise ValueError(
                "Snippet must be dict of "
                "{'text':t, 'maxLines':i} or string"  # noqa: FS003
            )

    @snippet.setter
    def snippet(self, snip=None):
        self._snippet = {}
        if isinstance(snip, dict):
            self._snippet["text"] = snip.get("text")
            max_lines = snip.get("maxLines")
            if max_lines is not None:
                self._snippet["maxLines"] = int(snip["maxLines"])
        elif isinstance(snip, str):
            self._snippet["text"] = snip
        elif snip is None:
            self._snippet = None
        else:
            raise ValueError(
                "Snippet must be dict of "
                "{'text':t, 'maxLines':i} or string"  # noqa: FS003
            )

    @property
    def address(self):
        if self._address:
            return self._address

    @address.setter
    def address(self, address):
        if isinstance(address, str):
            self._address = address
        elif address is None:
            self._address = None
        else:
            raise ValueError

    @property
    def phone_number(self):
        if self._phone_number:
            return self._phone_number

    @phone_number.setter
    def phone_number(self, phone_number):
        if isinstance(phone_number, str):
            self._phone_number = phone_number
        elif phone_number is None:
            self._phone_number = None
        else:
            raise ValueError

    def etree_element(self):
        element = super().etree_element()
        if self.name:
            name = etree.SubElement(element, f"{self.ns}name")
            name.text = self.name
        if self.description:
            description = etree.SubElement(element, f"{self.ns}description")
            description.text = self.description
        if (self.camera is not None) and (self.look_at is not None):
            raise ValueError("Either Camera or LookAt can be defined, not both")
        if self.camera is not None:
            element.append(self._camera.etree_element())
        elif self.look_at is not None:
            element.append(self._look_at.etree_element())
        visibility = etree.SubElement(element, f"{self.ns}visibility")
        visibility.text = str(self.visibility)
        if self.isopen:
            isopen = etree.SubElement(element, f"{self.ns}open")
            isopen.text = str(self.isopen)
        if self._style_url is not None:
            element.append(self._style_url.etree_element())
        for style in self.styles():
            element.append(style.etree_element())
        if self.snippet:
            snippet = etree.SubElement(element, f"{self.ns}Snippet")
            if isinstance(self.snippet, str):
                snippet.text = self.snippet
            else:
                assert isinstance(self.snippet["text"], str)
                snippet.text = self.snippet["text"]
                if self.snippet.get("maxLines"):
                    snippet.set("maxLines", str(self.snippet["maxLines"]))
        if (self._timespan is not None) and (self._timestamp is not None):
            raise ValueError("Either Timestamp or Timespan can be defined, not both")
        elif self._timespan is not None:
            element.append(self._timespan.etree_element())
        elif self._timestamp is not None:
            element.append(self._timestamp.etree_element())
        if self._atom_link is not None:
            element.append(self._atom_link.etree_element())
        if self._atom_author is not None:
            element.append(self._atom_author.etree_element())
        if self.extended_data is not None:
            element.append(self.extended_data.etree_element())
        if self._address is not None:
            address = etree.SubElement(element, f"{self.ns}address")
            address.text = self._address
        if self._phone_number is not None:
            phone_number = etree.SubElement(element, f"{self.ns}phoneNumber")
            phone_number.text = self._phone_number
        return element

    def from_element(self, element):
        super().from_element(element)
        name = element.find(f"{self.ns}name")
        if name is not None:
            self.name = name.text
        description = element.find(f"{self.ns}description")
        if description is not None:
            self.description = description.text
        visibility = element.find(f"{self.ns}visibility")
        if visibility is not None:
            self.visibility = 1 if visibility.text in ["1", "true"] else 0
        isopen = element.find(f"{self.ns}open")
        if isopen is not None:
            self.isopen = 1 if isopen.text in ["1", "true"] else 0
        styles = element.findall(f"{self.ns}Style")
        for style in styles:
            s = Style(self.ns)
            s.from_element(style)
            self.append_style(s)
        styles = element.findall(f"{self.ns}StyleMap")
        for style in styles:
            s = StyleMap(self.ns)
            s.from_element(style)
            self.append_style(s)
        style_url = element.find(f"{self.ns}styleUrl")
        if style_url is not None:
            s = StyleUrl(self.ns)
            s.from_element(style_url)
            self._style_url = s
        snippet = element.find(f"{self.ns}Snippet")
        if snippet is not None:
            _snippet = {"text": snippet.text}
            if snippet.get("maxLines"):
                _snippet["maxLines"] = int(snippet.get("maxLines"))
            self.snippet = _snippet
        timespan = element.find(f"{self.ns}TimeSpan")
        if timespan is not None:
            s = TimeSpan(self.ns)
            s.from_element(timespan)
            self._timespan = s
        timestamp = element.find(f"{self.ns}TimeStamp")
        if timestamp is not None:
            s = TimeStamp(self.ns)
            s.from_element(timestamp)
            self._timestamp = s
        atom_link = element.find(f"{atom.NS}link")
        if atom_link is not None:
            s = atom.Link()
            s.from_element(atom_link)
            self._atom_link = s
        atom_author = element.find(f"{atom.NS}author")
        if atom_author is not None:
            s = atom.Author()
            s.from_element(atom_author)
            self._atom_author = s
        extended_data = element.find(f"{self.ns}ExtendedData")
        if extended_data is not None:
            x = ExtendedData(self.ns)
            x.from_element(extended_data)
            self.extended_data = x
            # else:
            #    logger.warn(
            #        'arbitrary or typed extended data is not yet supported'
            #    )
        address = element.find(f"{self.ns}address")
        if address is not None:
            self.address = address.text
        phone_number = element.find(f"{self.ns}phoneNumber")
        if phone_number is not None:
            self.phone_number = phone_number.text
        camera = element.find(f"{self.ns}Camera")
        if camera is not None:
            s = Camera(self.ns)
            s.from_element(camera)
            self.camera = s

class _Container(_Feature):
    """
    abstract element; do not create
    A Container element holds one or more Features and allows the
    creation of nested hierarchies.
    subclasses are:
    Document,
    Folder
    """

    _features = []

    def __init__(
        self, ns=None, id=None, name=None, description=None, styles=None, style_url=None
    ):
        super().__init__(ns, id, name, description, styles, style_url)
        self._features = []

    def features(self):
        """iterate over features"""
        for feature in self._features:
            if isinstance(feature, (Folder, Placemark, Document)):
                yield feature
            else:
                raise TypeError(
                    "Features must be instances of " "(Folder, Placemark, Document)"
                )

    def etree_element(self):
        element = super().etree_element()
        for feature in self.features():
            element.append(feature.etree_element())
        return element

    def append(self, kmlobj):
        """append a feature"""
        if isinstance(kmlobj, (Folder, Placemark, Document)):
            self._features.append(kmlobj)
        else:
            raise TypeError(
                "Features must be instances of " "(Folder, Placemark, Document)"
            )
        assert kmlobj != self


class _Overlay(_Feature):
    """
    abstract element; do not create

    Base type for image overlays drawn on the planet surface or on the screen

    A Container element holds one or more Features and allows the creation of
    nested hierarchies.
    """

    _color = None
    # Color values expressed in hexadecimal notation, including opacity (alpha)
    # values. The order of expression is alpOverlayha, blue, green, red
    # (AABBGGRR). The range of values for any one color is 0 to 255 (00 to ff).
    # For opacity, 00 is fully transparent and ff is fully opaque.

    _draw_order = None
    # Defines the stacking order for the images in overlapping overlays.
    # Overlays with higher <drawOrder> values are drawn on top of those with
    # lower <drawOrder> values.

    _icon = None
    # Defines the image associated with the overlay. Contains an <href> html
    # tag which defines the location of the image to be used as the overlay.
    # The location can be either on a local file system or on a webserver. If
    # this element is omitted or contains no <href>, a rectangle is drawn using
    # the color and size defined by the ground or screen overlay.

    def __init__(
        self, ns=None, id=None, name=None, description=None, styles=None, style_url=None
    ):
        super().__init__(ns, id, name, description, styles, style_url)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if isinstance(color, str):
            self._color = color
        elif color is None:
            self._color = None
        else:
            raise ValueError

    @property
    def draw_order(self):
        return self._draw_order

    @draw_order.setter
    def draw_order(self, value):
        if isinstance(value, (str, int, float)):
            self._draw_order = str(value)
        elif value is None:
            self._draw_order = None
        else:
            raise ValueError

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, url):
        if isinstance(url, str):
            if not url.startswith("<href>"):
                url = "<href>" + url
            if not url.endswith("</href>"):
                url = url + "</href>"
            self._icon = url
        elif url is None:
            self._icon = None
        else:
            raise ValueError

    def etree_element(self):
        element = super().etree_element()
        if self._color:
            color = etree.SubElement(element, f"{self.ns}color")
            color.text = self._color
        if self._draw_order:
            draw_order = etree.SubElement(element, f"{self.ns}drawOrder")
            draw_order.text = self._draw_order
        if self._icon:
            icon = etree.SubElement(element, f"{self.ns}icon")
            icon.text = self._icon
        return element

    def from_element(self, element):
        super().from_element(element)
        color = element.find(f"{self.ns}color")
        if color is not None:
            self.color = color.text
        draw_order = element.find(f"{self.ns}drawOrder")
        if draw_order is not None:
            self.draw_order = draw_order.text
        icon = element.find(f"{self.ns}icon")
        if icon is not None:
            self.icon = icon.text


class PhotoOverlay(_Overlay):
    """
    The <PhotoOverlay> element allows you to geographically locate a photograph
    on the Earth and to specify viewing parameters for this PhotoOverlay.
    The PhotoOverlay can be a simple 2D rectangle, a partial or full cylinder,
    or a sphere (for spherical panoramas). The overlay is placed at the
    specified location and oriented toward the viewpoint.

    Because <PhotoOverlay> is derived from <Feature>, it can contain one of
    the two elements derived from <AbstractView>—either <Camera> or <LookAt>.
    The Camera (or LookAt) specifies a viewpoint and a viewing direction (also
    referred to as a view vector). The PhotoOverlay is positioned in relation
    to the viewpoint. Specifically, the plane of a 2D rectangular image is
    orthogonal (at right angles to) the view vector. The normal of this
    plane—that is, its front, which is the part
    with the photo—is oriented toward the viewpoint.

    The URL for the PhotoOverlay image is specified in the <Icon> tag,
    which is inherited from <Overlay>. The <Icon> tag must contain an <href>
    element that specifies the image file to use for the PhotoOverlay.
    In the case of a very large image, the <href> is a special URL that
    indexes into a pyramid of images of varying resolutions (see ImagePyramid).
    """

    __name__ = "PhotoOverlay"

    _rotation = None
    # Adjusts how the photo is placed inside the field of view. This element is
    # useful if your photo has been rotated and deviates slightly from a desired
    # horizontal view.

    # - ViewVolume -
    # Defines how much of the current scene is visible. Specifying the field of
    # view is analogous to specifying the lens opening in a physical camera.
    # A small field of view, like a telephoto lens, focuses on a small part of
    # the scene. A large field of view, like a wide-angle lens, focuses on a
    # large part of the scene.

    _leftFov = None
    # Angle, in degrees, between the camera's viewing direction and the left side
    # of the view volume.

    _rightFov = None
    # Angle, in degrees, between the camera's viewing direction and the right side
    # of the view volume.

    _bottomFov = None
    # Angle, in degrees, between the camera's viewing direction and the bottom side
    # of the view volume.

    _topFov = None
    # Angle, in degrees, between the camera's viewing direction and the top side
    # of the view volume.

    _near = None
    # Measurement in meters along the viewing direction from the camera viewpoint
    # to the PhotoOverlay shape.

    _tileSize = "256"
    # Size of the tiles, in pixels. Tiles must be square, and <tileSize> must
    # be a power of 2. A tile size of 256 (the default) or 512 is recommended.
    # The original image is divided into tiles of this size, at varying resolutions.

    _maxWidth = None
    # Width in pixels of the original image.

    _maxHeight = None
    # Height in pixels of the original image.

    _gridOrigin = None
    # Specifies where to begin numbering the tiles in each layer of the pyramid.
    # A value of lowerLeft specifies that row 1, column 1 of each layer is in
    # the bottom left corner of the grid.

    _point = None
    # The <Point> element acts as a <Point> inside a <Placemark> element.
    # It draws an icon to mark the position of the PhotoOverlay.
    # The icon drawn is specified by the <styleUrl> and <StyleSelector> fields,
    # just as it is for <Placemark>.

    _shape = "rectangle"
    # The PhotoOverlay is projected onto the <shape>.
    # The <shape> can be one of the following:
    #   rectangle (default) -
    #       for an ordinary photo
    #   cylinder -
    #       for panoramas, which can be either partial or full cylinders
    #   sphere -
    #       for spherical panoramas

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if isinstance(value, (str, int, float)):
            self._rotation = str(value)
        elif value is None:
            self._rotation = None
        else:
            raise ValueError

    @property
    def leftFov(self):
        return self._leftFov

    @leftFov.setter
    def leftFov(self, value):
        if isinstance(value, (str, int, float)):
            self._leftFov = str(value)
        elif value is None:
            self._leftFov = None
        else:
            raise ValueError

    @property
    def rightFov(self):
        return self._rightFov

    @rightFov.setter
    def rightFov(self, value):
        if isinstance(value, (str, int, float)):
            self._rightFov = str(value)
        elif value is None:
            self._rightFov = None
        else:
            raise ValueError

    @property
    def bottomFov(self):
        return self._bottomFov

    @bottomFov.setter
    def bottomFov(self, value):
        if isinstance(value, (str, int, float)):
            self._bottomFov = str(value)
        elif value is None:
            self._bottomFov = None
        else:
            raise ValueError

    @property
    def topFov(self):
        return self._topFov

    @topFov.setter
    def topFov(self, value):
        if isinstance(value, (str, int, float)):
            self._topFov = str(value)
        elif value is None:
            self._topFov = None
        else:
            raise ValueError

    @property
    def near(self):
        return self._near

    @near.setter
    def near(self, value):
        if isinstance(value, (str, int, float)):
            self._near = str(value)
        elif value is None:
            self._near = None
        else:
            raise ValueError

    @property
    def tileSize(self):
        return self._tileSize

    @tileSize.setter
    def tileSize(self, value):
        if isinstance(value, (str, int, float)):
            self._tileSize = str(value)
        elif value is None:
            self._tileSize = None
        else:
            raise ValueError

    @property
    def maxWidth(self):
        return self._maxWidth

    @maxWidth.setter
    def maxWidth(self, value):
        if isinstance(value, (str, int, float)):
            self._maxWidth = str(value)
        elif value is None:
            self._maxWidth = None
        else:
            raise ValueError

    @property
    def maxHeight(self):
        return self._maxHeight

    @maxHeight.setter
    def maxHeight(self, value):
        if isinstance(value, (str, int, float)):
            self._maxHeight = str(value)
        elif value is None:
            self._maxHeight = None
        else:
            raise ValueError

    @property
    def gridOrigin(self):
        return self._gridOrigin

    @gridOrigin.setter
    def gridOrigin(self, value):
        if value in ("lowerLeft", "upperLeft"):
            self._gridOrigin = str(value)
        elif value is None:
            self._gridOrigin = None
        else:
            raise ValueError

    @property
    def point(self):
        return self._point

    @point.setter
    def point(self, value):
        if isinstance(value, (str, tuple)):
            self._point = str(value)
        else:
            raise ValueError

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        if value in ("rectangle", "cylinder", "sphere"):
            self._shape = str(value)
        elif value is None:
            self._shape = None
        else:
            raise ValueError("Shape must be one of " "rectangle, cylinder, sphere")

    def ViewVolume(self, leftFov, rightFov, bottomFov, topFov, near):
        self.leftFov = leftFov
        self.rightFov = rightFov
        self.bottomFov = bottomFov
        self.topFov = topFov
        self.near = near

    def ImagePyramid(self, tileSize, maxWidth, maxHeight, gridOrigin):
        self.tileSize = tileSize
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.gridOrigin = gridOrigin

    def etree_element(self):
        element = super().etree_element()
        if self._rotation:
            rotation = etree.SubElement(element, f"{self.ns}rotation")
            rotation.text = self._rotation
        if all(
            [self._leftFov, self._rightFov, self._bottomFov, self._topFov, self._near]
        ):
            ViewVolume = etree.SubElement(element, f"{self.ns}ViewVolume")
            leftFov = etree.SubElement(ViewVolume, f"{self.ns}leftFov")
            leftFov.text = self._leftFov
            rightFov = etree.SubElement(ViewVolume, f"{self.ns}rightFov")
            rightFov.text = self._rightFov
            bottomFov = etree.SubElement(ViewVolume, f"{self.ns}bottomFov")
            bottomFov.text = self._bottomFov
            topFov = etree.SubElement(ViewVolume, f"{self.ns}topFov")
            topFov.text = self._topFov
            near = etree.SubElement(ViewVolume, f"{self.ns}near")
            near.text = self._near
        if all([self._tileSize, self._maxWidth, self._maxHeight, self._gridOrigin]):
            ImagePyramid = etree.SubElement(element, f"{self.ns}ImagePyramid")
            tileSize = etree.SubElement(ImagePyramid, f"{self.ns}tileSize")
            tileSize.text = self._tileSize
            maxWidth = etree.SubElement(ImagePyramid, f"{self.ns}maxWidth")
            maxWidth.text = self._maxWidth
            maxHeight = etree.SubElement(ImagePyramid, f"{self.ns}maxHeight")
            maxHeight.text = self._maxHeight
            gridOrigin = etree.SubElement(ImagePyramid, f"{self.ns}gridOrigin")
            gridOrigin.text = self._gridOrigin
        return element

    def from_element(self, element):
        super().from_element(element)
        rotation = element.find(f"{self.ns}rotation")
        if rotation is not None:
            self.rotation = rotation.text
        ViewVolume = element.find(f"{self.ns}ViewVolume")
        if ViewVolume is not None:
            leftFov = ViewVolume.find(f"{self.ns}leftFov")
            if leftFov is not None:
                self.leftFov = leftFov.text
            rightFov = ViewVolume.find(f"{self.ns}rightFov")
            if rightFov is not None:
                self.rightFov = rightFov.text
            bottomFov = ViewVolume.find(f"{self.ns}bottomFov")
            if bottomFov is not None:
                self.bottomFov = bottomFov.text
            topFov = ViewVolume.find(f"{self.ns}topFov")
            if topFov is not None:
                self.topFov = topFov.text
            near = ViewVolume.find(f"{self.ns}near")
            if near is not None:
                self.near = near.text
        ImagePyramid = element.find(f"{self.ns}ImagePyramid")
        if ImagePyramid is not None:
            tileSize = ImagePyramid.find(f"{self.ns}tileSize")
            if tileSize is not None:
                self.tileSize = tileSize.text
            maxWidth = ImagePyramid.find(f"{self.ns}maxWidth")
            if maxWidth is not None:
                self.maxWidth = maxWidth.text
            maxHeight = ImagePyramid.find(f"{self.ns}maxHeight")
            if maxHeight is not None:
                self.maxHeight = maxHeight.text
            gridOrigin = ImagePyramid.find(f"{self.ns}gridOrigin")
            if gridOrigin is not None:
                self.gridOrigin = gridOrigin.text
        Point = element.find(f"{self.ns}Point")
        if Point is not None:
            self.point = Point.text
        shape = element.find(f"{self.ns}shape")
        if shape is not None:
            self.shape = shape.text


class GroundOverlay(_Overlay):
    """
    This element draws an image overlay draped onto the terrain. The <href>
    child of <Icon> specifies the image to be used as the overlay. This file
    can be either on a local file system or on a web server. If this element
    is omitted or contains no <href>, a rectangle is drawn using the color and
    LatLonBox bounds defined by the ground overlay.
    """

    __name__ = "GroundOverlay"

    _altitude = None
    # Specifies the distance above the earth's surface, in meters, and is
    # interpreted according to the altitude mode.

    _altitude_mode = "clampToGround"
    # Specifies how the <altitude> is interpreted. Possible values are:
    #   clampToGround -
    #       (default) Indicates to ignore the altitude specification and drape
    #       the overlay over the terrain.
    #   absolute -
    #       Sets the altitude of the overlay relative to sea level, regardless
    #       of the actual elevation of the terrain beneath the element. For
    #       example, if you set the altitude of an overlay to 10 meters with an
    #       absolute altitude mode, the overlay will appear to be at ground
    #       level if the terrain beneath is also 10 meters above sea level. If
    #       the terrain is 3 meters above sea level, the overlay will appear
    #       elevated above the terrain by 7 meters.

    # - LatLonBox -
    # TODO: Convert this to it's own class?
    # Specifies where the top, bottom, right, and left sides of a bounding box
    # for the ground overlay are aligned. Also, optionally the rotation of the
    # overlay.

    _north = None
    # Specifies the latitude of the north edge of the bounding box, in decimal
    # degrees from 0 to ±90.

    _south = None
    # Specifies the latitude of the south edge of the bounding box, in decimal
    # degrees from 0 to ±90.

    _east = None
    # Specifies the longitude of the east edge of the bounding box, in decimal
    # degrees from 0 to ±180. (For overlays that overlap the meridian of 180°
    # longitude, values can extend beyond that range.)

    _west = None
    # Specifies the longitude of the west edge of the bounding box, in decimal
    # degrees from 0 to ±180. (For overlays that overlap the meridian of 180°
    # longitude, values can extend beyond that range.)

    _rotation = None
    # Specifies a rotation of the overlay about its center, in degrees. Values
    # can be ±180. The default is 0 (north). Rotations are specified in a
    # counterclockwise direction.

    # TODO: <gx:LatLonQuad>
    # Used for nonrectangular quadrilateral ground overlays.
    _lat_lon_quad = None

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        if isinstance(value, (str, int, float)):
            self._altitude = str(value)
        elif value is None:
            self._altitude = None
        else:
            raise ValueError

    @property
    def altitude_mode(self):
        return self._altitude_mode

    @altitude_mode.setter
    def altitude_mode(self, mode):
        if mode in ("clampToGround", "absolute"):
            self._altitude_mode = str(mode)
        else:
            self._altitude_mode = "clampToGround"

    @property
    def north(self):
        return self._north

    @north.setter
    def north(self, value):
        if isinstance(value, (str, int, float)):
            self._north = str(value)
        elif value is None:
            self._north = None
        else:
            raise ValueError

    @property
    def south(self):
        return self._south

    @south.setter
    def south(self, value):
        if isinstance(value, (str, int, float)):
            self._south = str(value)
        elif value is None:
            self._south = None
        else:
            raise ValueError

    @property
    def east(self):
        return self._east

    @east.setter
    def east(self, value):
        if isinstance(value, (str, int, float)):
            self._east = str(value)
        elif value is None:
            self._east = None
        else:
            raise ValueError

    @property
    def west(self):
        return self._west

    @west.setter
    def west(self, value):
        if isinstance(value, (str, int, float)):
            self._west = str(value)
        elif value is None:
            self._west = None
        else:
            raise ValueError

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if isinstance(value, (str, int, float)):
            self._rotation = str(value)
        elif value is None:
            self._rotation = None
        else:
            raise ValueError

    def lat_lon_box(self, north, south, east, west, rotation=0):
        if -90 <= float(north) <= 90:
            self.north = north
        else:
            raise ValueError
        if -90 <= float(south) <= 90:
            self.south = south
        else:
            raise ValueError
        if -180 <= float(east) <= 180:
            self.east = east
        else:
            raise ValueError
        if -180 <= float(east) <= 180:
            self.west = west
        else:
            raise ValueError
        if -180 <= float(east) <= 180:
            self.rotation = rotation
        else:
            raise ValueError

    def etree_element(self):
        element = super().etree_element()
        if self._altitude:
            altitude = etree.SubElement(element, f"{self.ns}altitude")
            altitude.text = self._altitude
            if self._altitude_mode:
                altitude_mode = etree.SubElement(element, f"{self.ns}altitudeMode")
                altitude_mode.text = self._altitude_mode
        if all([self._north, self._south, self._east, self._west]):
            lat_lon_box = etree.SubElement(element, f"{self.ns}LatLonBox")
            north = etree.SubElement(lat_lon_box, f"{self.ns}north")
            north.text = self._north
            south = etree.SubElement(lat_lon_box, f"{self.ns}south")
            south.text = self._south
            east = etree.SubElement(lat_lon_box, f"{self.ns}east")
            east.text = self._east
            west = etree.SubElement(lat_lon_box, f"{self.ns}west")
            west.text = self._west
            if self._rotation:
                rotation = etree.SubElement(lat_lon_box, f"{self.ns}rotation")
                rotation.text = self._rotation
        return element

    def from_element(self, element):
        super().from_element(element)
        altitude = element.find(f"{self.ns}altitude")
        if altitude is not None:
            self.altitude = altitude.text
        altitude_mode = element.find(f"{self.ns}altitudeMode")
        if altitude_mode is not None:
            self.altitude_mode = altitude_mode.text
        lat_lon_box = element.find(f"{self.ns}LatLonBox")
        if lat_lon_box is not None:
            north = lat_lon_box.find(f"{self.ns}north")
            if north is not None:
                self.north = north.text
            south = lat_lon_box.find(f"{self.ns}south")
            if south is not None:
                self.south = south.text
            east = lat_lon_box.find(f"{self.ns}east")
            if east is not None:
                self.east = east.text
            west = lat_lon_box.find(f"{self.ns}west")
            if west is not None:
                self.west = west.text
            rotation = lat_lon_box.find(f"{self.ns}rotation")
            if rotation is not None:
                self.rotation = rotation.text


class Document(_Container):
    """
    A Document is a container for features and styles. This element is
    required if your KML file uses shared styles or schemata for typed
    extended data
    """

    __name__ = "Document"
    _schemata = None

    def schemata(self):
        if self._schemata:
            yield from self._schemata

    def append_schema(self, schema):
        if self._schemata is None:
            self._schemata = []
        if isinstance(schema, Schema):
            self._schemata.append(schema)
        else:
            s = Schema(schema)
            self._schemata.append(s)

    def from_element(self, element):
        super().from_element(element)
        documents = element.findall(f"{self.ns}Document")
        for document in documents:
            feature = Document(self.ns)
            feature.from_element(document)
            self.append(feature)
        folders = element.findall(f"{self.ns}Folder")
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall(f"{self.ns}Placemark")
        for placemark in placemarks:
            feature = Placemark(self.ns)
            feature.from_element(placemark)
            self.append(feature)
        schemata = element.findall(f"{self.ns}Schema")
        for schema in schemata:
            s = Schema(self.ns, id="default")
            s.from_element(schema)
            self.append_schema(s)

    def etree_element(self):
        element = super().etree_element()
        if self._schemata is not None:
            for schema in self._schemata:
                element.append(schema.etree_element())
        return element

    def get_style_by_url(self, style_url):
        id = urlparse.urlparse(style_url).fragment
        for style in self.styles():
            if style.id == id:
                return style


class Folder(_Container):
    """
    A Folder is used to arrange other Features hierarchically
    (Folders, Placemarks, #NetworkLinks, or #Overlays).
    """

    __name__ = "Folder"

    def from_element(self, element):
        super().from_element(element)
        folders = element.findall(f"{self.ns}Folder")
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall(f"{self.ns}Placemark")
        for placemark in placemarks:
            feature = Placemark(self.ns)
            feature.from_element(placemark)
            self.append(feature)
        documents = element.findall(f"{self.ns}Document")
        for document in documents:
            feature = Document(self.ns)
            feature.from_element(document)
            self.append(feature)


class Placemark(_Feature):
    """
    A Placemark is a Feature with associated Geometry.
    In Google Earth, a Placemark appears as a list item in the Places
    panel. A Placemark with a Point has an icon associated with it that
    marks a point on the Earth in the 3D viewer.
    """

    __name__ = "Placemark"
    _geometry = None

    @property
    def geometry(self):
        return self._geometry.geometry

    @geometry.setter
    def geometry(self, geometry):
        if isinstance(geometry, Geometry):
            self._geometry = geometry
        else:
            self._geometry = Geometry(ns=self.ns, geometry=geometry)

    def from_element(self, element):
        super().from_element(element)
        point = element.find(f"{self.ns}Point")
        if point is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(point)
            self._geometry = geom
            return
        line = element.find(f"{self.ns}LineString")
        if line is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(line)
            self._geometry = geom
            return
        polygon = element.find(f"{self.ns}Polygon")
        if polygon is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(polygon)
            self._geometry = geom
            return
        linearring = element.find(f"{self.ns}LinearRing")
        if linearring is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(linearring)
            self._geometry = geom
            return
        multigeometry = element.find(f"{self.ns}MultiGeometry")
        if multigeometry is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(multigeometry)
            self._geometry = geom
            return
        track = element.find(f"{self.ns}Track")
        if track is not None:
            geom = gx.GxGeometry(ns=gx.NS)
            geom.from_element(track)
            self._geometry = geom
            return
        multitrack = element.find(f"{self.ns}MultiTrack")
        if line is not None:
            geom = gx.GxGeometry(ns=gx.NS)
            geom.from_element(multitrack)
            self._geometry = geom
            return
        logger.warning("No geometries found")
        logger.debug("Problem with element: %", etree.tostring(element))
        # raise ValueError('No geometries found')

    def etree_element(self):
        element = super().etree_element()
        if self._geometry is not None:
            element.append(self._geometry.etree_element())
        else:
            logger.error("Object does not have a geometry")
        return element


class _TimePrimitive(_BaseObject):
    """The dateTime is defined according to XML Schema time.
    The value can be expressed as yyyy-mm-ddThh:mm:sszzzzzz, where T is
    the separator between the date and the time, and the time zone is
    either Z (for UTC) or zzzzzz, which represents ±hh:mm in relation to
    UTC. Additionally, the value can be expressed as a date only.

    The precision of the dateTime is dictated by the dateTime value
    which can be one of the following:

    - dateTime gives second resolution
    - date gives day resolution
    - gYearMonth gives month resolution
    - gYear gives year resolution
    """

    RESOLUTIONS = ["gYear", "gYearMonth", "date", "dateTime"]

    def get_resolution(self, dt, resolution=None):
        if resolution:
            if resolution not in self.RESOLUTIONS:
                raise ValueError
            else:
                return resolution
        elif isinstance(dt, datetime):
            resolution = "dateTime"
        elif isinstance(dt, date):
            resolution = "date"
        else:
            resolution = None
        return resolution

    def parse_str(self, datestr):
        resolution = "dateTime"
        year = 0
        month = 1
        day = 1
        if len(datestr) == 4:
            resolution = "gYear"
            year = int(datestr)
            dt = datetime(year, month, day)
        elif len(datestr) == 6:
            resolution = "gYearMonth"
            year = int(datestr[:4])
            month = int(datestr[-2:])
            dt = datetime(year, month, day)
        elif len(datestr) == 7:
            resolution = "gYearMonth"
            year = int(datestr.split("-")[0])
            month = int(datestr.split("-")[1])
            dt = datetime(year, month, day)
        elif len(datestr) in [8, 10]:
            resolution = "date"
            dt = dateutil.parser.parse(datestr)
        elif len(datestr) > 10:
            resolution = "dateTime"
            dt = dateutil.parser.parse(datestr)
        else:
            raise ValueError
        return [dt, resolution]

    def date_to_string(self, dt, resolution=None):
        if isinstance(dt, (date, datetime)):
            resolution = self.get_resolution(dt, resolution)
            if resolution == "gYear":
                return dt.strftime("%Y")
            elif resolution == "gYearMonth":
                return dt.strftime("%Y-%m")
            elif resolution == "date":
                if isinstance(dt, datetime):
                    return dt.date().isoformat()
                else:
                    return dt.isoformat()
            elif resolution == "dateTime":
                return dt.isoformat()


class TimeStamp(_TimePrimitive):
    """Represents a single moment in time."""

    __name__ = "TimeStamp"
    timestamp = None

    def __init__(self, ns=None, id=None, timestamp=None, resolution=None):
        super().__init__(ns, id)
        resolution = self.get_resolution(timestamp, resolution)
        self.timestamp = [timestamp, resolution]

    def etree_element(self):
        element = super().etree_element()
        when = etree.SubElement(element, f"{self.ns}when")
        when.text = self.date_to_string(*self.timestamp)
        return element

    def from_element(self, element):
        super().from_element(element)
        when = element.find(f"{self.ns}when")
        if when is not None:
            self.timestamp = self.parse_str(when.text)


class TimeSpan(_TimePrimitive):
    """Represents an extent in time bounded by begin and end dateTimes."""

    __name__ = "TimeSpan"
    begin = None
    end = None

    def __init__(
        self, ns=None, id=None, begin=None, begin_res=None, end=None, end_res=None
    ):
        super().__init__(ns, id)
        if begin:
            resolution = self.get_resolution(begin, begin_res)
            self.begin = [begin, resolution]
        if end:
            resolution = self.get_resolution(end, end_res)
            self.end = [end, resolution]

    def from_element(self, element):
        super().from_element(element)
        begin = element.find(f"{self.ns}begin")
        if begin is not None:
            self.begin = self.parse_str(begin.text)
        end = element.find(f"{self.ns}end")
        if end is not None:
            self.end = self.parse_str(end.text)

    def etree_element(self):
        element = super().etree_element()
        if self.begin is not None:
            text = self.date_to_string(*self.begin)
            if text:
                begin = etree.SubElement(element, f"{self.ns}begin")
                begin.text = text
        if self.end is not None:
            text = self.date_to_string(*self.end)
            if text:
                end = etree.SubElement(element, f"{self.ns}end")
                end.text = text
        if self.begin == self.end is None:
            raise ValueError("Either begin, end or both must be set")
        # TODO test if end > begin
        return element


class Schema(_BaseObject):
    """
    Specifies a custom KML schema that is used to add custom data to
    KML Features.
    The "id" attribute is required and must be unique within the KML file.
    <Schema> is always a child of <Document>.
    """

    __name__ = "Schema"

    _simple_fields = None
    # The declaration of the custom fields, each of which must specify both the
    # type and the name of this field. If either the type or the name is
    # omitted, the field is ignored.
    name = None

    def __init__(self, ns=None, id=None, name=None, fields=None):
        if id is None:
            raise ValueError("Id is required for schema")
        super().__init__(ns, id)
        self.simple_fields = fields
        self.name = name

    @property
    def simple_fields(self):
        return tuple(
            {
                "type": simple_field["type"],
                "name": simple_field["name"],
                "displayName": simple_field.get("displayName"),
            }
            for simple_field in self._simple_fields
            if simple_field.get("type") and simple_field.get("name")
        )

    @simple_fields.setter
    def simple_fields(self, fields):
        self._simple_fields = []
        if isinstance(fields, dict):
            self.append(**fields)
        elif isinstance(fields, (list, tuple)):
            for field in fields:
                if isinstance(field, (list, tuple)):
                    self.append(*field)
                elif isinstance(field, dict):
                    self.append(**field)
        elif fields is None:
            self._simple_fields = []
        else:
            raise ValueError("Fields must be of type list, tuple or dict")

    def append(self, type, name, display_name=None):
        """
        append a field.
        The declaration of the custom field, must specify both the type
        and the name of this field.
        If either the type or the name is omitted, the field is ignored.

        The type can be one of the following:
            string
            int
            uint
            short
            ushort
            float
            double
            bool

        <displayName>
        The name, if any, to be used when the field name is displayed to
        the Google Earth user. Use the [CDATA] element to escape standard
        HTML markup.
        """
        allowed_types = [
            "string",
            "int",
            "uint",
            "short",
            "ushort",
            "float",
            "double",
            "bool",
        ]
        if type not in allowed_types:
            raise TypeError(
                f"{name} has the type {type} which is invalid. "
                + "The type must be one of "
                + "'string', 'int', 'uint', 'short', "
                + "'ushort', 'float', 'double', 'bool'"
            )
        self._simple_fields.append(
            {"type": type, "name": name, "displayName": display_name}
        )

    def from_element(self, element):
        super().from_element(element)
        self.name = element.get("name")
        simple_fields = element.findall(f"{self.ns}SimpleField")
        self.simple_fields = None
        for simple_field in simple_fields:
            sfname = simple_field.get("name")
            sftype = simple_field.get("type")
            display_name = simple_field.find(f"{self.ns}displayName")
            sfdisplay_name = display_name.text if display_name is not None else None
            self.append(sftype, sfname, sfdisplay_name)

    def etree_element(self):
        element = super().etree_element()
        if self.name:
            element.set("name", self.name)
        for simple_field in self.simple_fields:
            sf = etree.SubElement(element, f"{self.ns}SimpleField")
            sf.set("type", simple_field["type"])
            sf.set("name", simple_field["name"])
            if simple_field.get("displayName"):
                dn = etree.SubElement(sf, f"{self.ns}displayName")
                dn.text = simple_field["displayName"]
        return element


class ExtendedData(_XMLObject):
    """Represents a list of untyped name/value pairs. See docs:

    -> 'Adding Untyped Name/Value Pairs'
       https://developers.google.com/kml/documentation/extendeddata

    """

    __name__ = "ExtendedData"

    def __init__(self, ns=None, elements=None):
        super().__init__(ns)
        self.elements = elements or []

    def etree_element(self):
        element = super().etree_element()
        for subelement in self.elements:
            element.append(subelement.etree_element())
        return element

    def from_element(self, element):
        super().from_element(element)
        self.elements = []
        untyped_data = element.findall(f"{self.ns}Data")
        for ud in untyped_data:
            el = Data(self.ns)
            el.from_element(ud)
            self.elements.append(el)
        typed_data = element.findall(f"{self.ns}SchemaData")
        for sd in typed_data:
            el = SchemaData(self.ns, "dummy")
            el.from_element(sd)
            self.elements.append(el)


class Data(_XMLObject):
    """Represents an untyped name/value pair with optional display name."""

    __name__ = "Data"

    def __init__(self, ns=None, name=None, value=None, display_name=None):
        super().__init__(ns)

        self.name = name
        self.value = value
        self.display_name = display_name

    def etree_element(self):
        element = super().etree_element()
        element.set("name", self.name)
        value = etree.SubElement(element, f"{self.ns}value")
        value.text = self.value
        if self.display_name:
            display_name = etree.SubElement(element, f"{self.ns}displayName")
            display_name.text = self.display_name
        return element

    def from_element(self, element):
        super().from_element(element)
        self.name = element.get("name")
        tmp_value = element.find(f"{self.ns}value")
        if tmp_value is not None:
            self.value = tmp_value.text
        display_name = element.find(f"{self.ns}displayName")
        if display_name is not None:
            self.display_name = display_name.text


class SchemaData(_XMLObject):
    """
    <SchemaData schemaUrl="anyURI">
    This element is used in conjunction with <Schema> to add typed
    custom data to a KML Feature. The Schema element (identified by the
    schemaUrl attribute) declares the custom data type. The actual data
    objects ("instances" of the custom data) are defined using the
    SchemaData element.
    The <schemaURL> can be a full URL, a reference to a Schema ID defined
    in an external KML file, or a reference to a Schema ID defined
    in the same KML file.
    """

    __name__ = "SchemaData"
    schema_url = None
    _data = None

    def __init__(self, ns=None, schema_url=None, data=None):
        super().__init__(ns)
        if (not isinstance(schema_url, str)) or (not schema_url):
            raise ValueError("required parameter schema_url missing")
        self.schema_url = schema_url
        self._data = []
        self.data = data

    @property
    def data(self):
        return tuple(self._data)

    @data.setter
    def data(self, data):
        if isinstance(data, (tuple, list)):
            self._data = []
            for d in data:
                if isinstance(d, (tuple, list)):
                    self.append_data(*d)
                elif isinstance(d, dict):
                    self.append_data(**d)
        elif data is None:
            self._data = []
        else:
            raise TypeError("data must be of type tuple or list")

    def append_data(self, name, value):
        if isinstance(name, str) and name:
            self._data.append({"name": name, "value": value})
        else:
            raise TypeError("name must be a nonempty string")

    def etree_element(self):
        element = super().etree_element()
        element.set("schemaUrl", self.schema_url)
        for data in self.data:
            sd = etree.SubElement(element, f"{self.ns}SimpleData")
            sd.set("name", data["name"])
            sd.text = data["value"]
        return element

    def from_element(self, element):
        super().from_element(element)
        self.data = []
        self.schema_url = element.get("schemaUrl")
        simple_data = element.findall(f"{self.ns}SimpleData")
        for sd in simple_data:
            self.append_data(sd.get("name"), sd.text)


class _AbstractView(_BaseObject):
    """
    This is an abstract element and cannot be used directly in a KML file.
    This element is extended by the <Camera> and <LookAt> elements.
    """

    _gx_timespan = None
    _gx_timestamp = None

    def etree_element(self):
        element = super().etree_element()
        if (self._timespan is not None) and (self._timestamp is not None):
            raise ValueError("Either Timestamp or Timespan can be defined, not both")
        if self._timespan is not None:
            element.append(self._gx_timespan.etree_element())
        elif self._timestamp is not None:
            element.append(self._gx_timestamp.etree_element())
        return element

    @property
    def gx_timestamp(self):
        return self._gx_timestamp

    @gx_timestamp.setter
    def gx_timestamp(self, dt):
        self._gx_timestamp = None if dt is None else TimeStamp(timestamp=dt)
        if self._gx_timestamp is not None:
            logger.warning("Setting a TimeStamp, TimeSpan deleted")
            self._gx_timespan = None

    @property
    def begin(self):
        return self._gx_timespan.begin[0]

    @begin.setter
    def begin(self, dt):
        if self._gx_timespan is None:
            self._gx_timespan = TimeSpan(begin=dt)
        elif self._gx_timespan.begin is None:
            self._gx_timespan.begin = [dt, None]
        else:
            self._gx_timespan.begin[0] = dt
        if self._gx_timestamp is not None:
            logger.warning("Setting a TimeSpan, TimeStamp deleted")
            self._gx_timestamp = None

    @property
    def end(self):
        return self._gx_timespan.end[0]

    @end.setter
    def end(self, dt):
        if self._gx_timespan is None:
            self._gx_timespan = TimeSpan(end=dt)
        elif self._gx_timespan.end is None:
            self._gx_timespan.end = [dt, None]
        else:
            self._gx_timespan.end[0] = dt
        if self._gx_timestamp is not None:
            logger.warning("Setting a TimeSpan, TimeStamp deleted")
            self._gx_timestamp = None

    def from_element(self, element):
        super().from_element(element)
        gx_timespan = element.find(f"{gx.NS}TimeSpan")
        if gx_timespan is not None:
            self._gx_timespan = gx_timespan.text
        gx_timestamp = element.find(f"{gx.NS}TimeStamp")
        if gx_timestamp is not None:
            self._gx_timestamp = gx_timestamp.text

    # TODO: <gx:ViewerOptions>
    # TODO: <gx:horizFov>


class Camera(_AbstractView):
    """
    Defines the virtual camera that views the scene. This element defines
    the position of the camera relative to the Earth's surface as well
    as the viewing direction of the camera. The camera position is defined
    by <longitude>, <latitude>, <altitude>, and either <altitudeMode> or
    <gx:altitudeMode>. The viewing direction of the camera is defined by
    <heading>, <tilt>, and <roll>. <Camera> can be a child element of any
    Feature or of <NetworkLinkControl>. A parent element cannot contain both a
    <Camera> and a <LookAt> at the same time.

    <Camera> provides full six-degrees-of-freedom control over the view,
    so you can position the Camera in space and then rotate it around the
    X, Y, and Z axes. Most importantly, you can tilt the camera view so that
    you're looking above the horizon into the sky.

    <Camera> can also contain a TimePrimitive (<gx:TimeSpan> or <gx:TimeStamp>).
    Time values in Camera affect historical imagery, sunlight, and the display of
    time-stamped features. For more information, read Time with AbstractViews in
    the Time and Animation chapter of the Developer's Guide.
    """

    __name__ = "Camera"

    _longitude = None
    # Longitude of the virtual camera (eye point). Angular distance in degrees,
    # relative to the Prime Meridian. Values west of the Meridian range from
    # −180 to 0 degrees. Values east of the Meridian range from 0 to 180 degrees.

    _latitude = None
    # Latitude of the virtual camera. Degrees north or south of the Equator
    # (0 degrees). Values range from −90 degrees to 90 degrees.

    _altitude = None
    # Distance of the camera from the earth's surface, in meters. Interpreted
    # according to the Camera's <altitudeMode> or <gx:altitudeMode>.

    _heading = None
    # Direction (azimuth) of the camera, in degrees. Default=0 (true North).
    # (See diagram.) Values range from 0 to 360 degrees.

    _tilt = None
    # Rotation, in degrees, of the camera around the X axis. A value of 0
    # indicates that the view is aimed straight down toward the earth (the
    # most common case). A value for 90 for <tilt> indicates that the view
    # is aimed toward the horizon. Values greater than 90 indicate that the
    # view is pointed up into the sky. Values for <tilt> are clamped at +180
    # degrees.

    _roll = None
    # Rotation, in degrees, of the camera around the Z axis. Values range from
    # −180 to +180 degrees.

    _altitude_mode = "relativeToGround"
    # Specifies how the <altitude> specified for the Camera is interpreted.
    # Possible values are as follows:
    #   relativeToGround -
    #       (default) Interprets the <altitude> as a value in meters above the
    #       ground. If the point is over water, the <altitude> will be
    #       interpreted as a value in meters above sea level. See
    #       <gx:altitudeMode> below to specify points relative to the sea floor.
    #   clampToGround -
    #       For a camera, this setting also places the camera relativeToGround,
    #       since putting the camera exactly at terrain height would mean that
    #       the eye would intersect the terrain (and the view would be blocked).
    #   absolute -
    #       Interprets the <altitude> as a value in meters above sea level.

    def __init__(
        self,
        ns=None,
        id=None,
        longitude=None,
        latitude=None,
        altitude=None,
        heading=None,
        tilt=None,
        roll=None,
        altitude_mode="relativeToGround",
    ):
        super().__init__(ns, id)
        self._longitude = longitude
        self._latitude = latitude
        self._altitude = altitude
        self._heading = heading
        self._tilt = tilt
        self._roll = roll
        self._altitude_mode = altitude_mode

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._longitude = str(value)
        elif value is None:
            self._longitude = None
        else:
            raise ValueError

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if isinstance(value, (str, int, float)) and (-90 <= float(value) <= 90):
            self._latitude = str(value)
        elif value is None:
            self._latitude = None
        else:
            raise ValueError

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        if isinstance(value, (str, int, float)):
            self._altitude = str(value)
        elif value is None:
            self._altitude = None
        else:
            raise ValueError

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._heading = str(value)
        elif value is None:
            self._heading = None
        else:
            raise ValueError

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        if isinstance(value, (str, int, float)) and (0 <= float(value) <= 180):
            self._tilt = str(value)
        elif value is None:
            self._tilt = None
        else:
            raise ValueError

    @property
    def roll(self):
        return self._roll

    @roll.setter
    def roll(self, value):
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._roll = str(value)
        elif value is None:
            self._roll = None
        else:
            raise ValueError

    @property
    def altitude_mode(self):
        return self._altitude_mode

    @altitude_mode.setter
    def altitude_mode(self, mode):
        if mode in ("relativeToGround", "clampToGround", "absolute"):
            self._altitude_mode = str(mode)
        else:
            self._altitude_mode = "relativeToGround"
            # raise ValueError(
            #     "altitude_mode must be one of " "relativeToGround,
            #     clampToGround, absolute")

    def from_element(self, element):
        super().from_element(element)
        longitude = element.find(f"{self.ns}longitude")
        if longitude is not None:
            self.longitude = longitude.text
        latitude = element.find(f"{self.ns}latitude")
        if latitude is not None:
            self.latitude = latitude.text
        altitude = element.find(f"{self.ns}altitude")
        if altitude is not None:
            self.altitude = altitude.text
        heading = element.find(f"{self.ns}heading")
        if heading is not None:
            self.heading = heading.text
        tilt = element.find(f"{self.ns}tilt")
        if tilt is not None:
            self.tilt = tilt.text
        roll = element.find(f"{self.ns}roll")
        if roll is not None:
            self.roll = roll.text
        altitude_mode = element.find(f"{self.ns}altitudeMode")
        if altitude_mode is not None:
            self.altitude_mode = altitude_mode.text
        else:
            altitude_mode = element.find(f"{gx.NS}altitudeMode")
            self.altitude_mode = altitude_mode.text

    def etree_element(self):
        element = super().etree_element()
        if self.longitude:
            longitude = etree.SubElement(element, f"{self.ns}longitude")
            longitude.text = self.longitude
        if self.latitude:
            latitude = etree.SubElement(element, f"{self.ns}latitude")
            latitude.text = self.latitude
        if self.altitude:
            altitude = etree.SubElement(element, f"{self.ns}altitude")
            altitude.text = self.altitude
        if self.heading:
            heading = etree.SubElement(element, f"{self.ns}heading")
            heading.text = self.heading
        if self.tilt:
            tilt = etree.SubElement(element, f"{self.ns}tilt")
            tilt.text = self.tilt
        if self.roll:
            roll = etree.SubElement(element, f"{self.ns}roll")
            roll.text = self.roll
        if self.altitude_mode in ("clampedToGround", "relativeToGround", "absolute"):
            altitude_mode = etree.SubElement(element, f"{self.ns}altitudeMode")
        elif self.altitude_mode in ("clampedToSeaFloor", "relativeToSeaFloor"):
            altitude_mode = etree.SubElement(element, f"{gx.NS}altitudeMode")
        altitude_mode.text = self.altitude_mode
        return element


class LookAt(_AbstractView):

    _longitude = None
    # Longitude of the point the camera is looking at. Angular distance in
    # degrees, relative to the Prime Meridian. Values west of the Meridian
    # range from −180 to 0 degrees. Values east of the Meridian range from
    # 0 to 180 degrees.

    _latitude = None
    # Latitude of the point the camera is looking at. Degrees north or south
    # of the Equator (0 degrees). Values range from −90 degrees to 90 degrees.

    _altitude = None
    # Distance from the earth's surface, in meters. Interpreted according to
    # the LookAt's altitude mode.

    _heading = None
    # Direction (that is, North, South, East, West), in degrees. Default=0
    # (North). (See diagram below.) Values range from 0 to 360 degrees.

    _tilt = None
    # Angle between the direction of the LookAt position and the normal to the
    #  surface of the earth. (See diagram below.) Values range from 0 to 90
    # degrees. Values for <tilt> cannot be negative. A <tilt> value of 0
    # degrees indicates viewing from directly above. A <tilt> value of 90
    # degrees indicates viewing along the horizon.

    _range = None
    # Distance in meters from the point specified by <longitude>, <latitude>,
    # and <altitude> to the LookAt position. (See diagram below.)

    _altitude_mode = None
    # Specifies how the <altitude> specified for the LookAt point is
    # interpreted. Possible values are as follows:
    #   clampToGround -
    #       (default) Indicates to ignore the <altitude> specification and
    #       place the LookAt position on the ground.
    #   relativeToGround -
    #       Interprets the <altitude> as a value in meters above the ground.
    #   absolute -
    #       Interprets the <altitude> as a value in meters above sea level.

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if isinstance(value, (str, int, float)) and (-180 <= float(value) <= 180):
            self._longitude = str(value)
        elif value is None:
            self._longitude = None
        else:
            raise ValueError

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if isinstance(value, (str, int, float)) and (-90 <= float(value) <= 90):
            self._latitude = str(value)
        elif value is None:
            self._latitude = None
        else:
            raise ValueError

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        if isinstance(value, (str, int, float)):
            self._altitude = str(value)
        elif value is None:
            self._altitude = None
        else:
            raise ValueError

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        if isinstance(value, (str, int, float)):
            self._heading = str(value)
        elif value is None:
            self._heading = None
        else:
            raise ValueError

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        if isinstance(value, (str, int, float)) and (0 <= float(value) <= 90):
            self._tilt = str(value)
        elif value is None:
            self._tilt = None
        else:
            raise ValueError

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, value):
        if isinstance(value, (str, int, float)):
            self._range = str(value)
        elif value is None:
            self._range = None
        else:
            raise ValueError

    @property
    def altitude_mode(self):
        return self._altitude_mode

    @altitude_mode.setter
    def altitude_mode(self, mode):
        if mode in (
            "relativeToGround",
            "clampToGround",
            "absolute",
            "relativeToSeaFloor",
            "clampToSeaFloor",
        ):
            self._altitude_mode = str(mode)
        else:
            self._altitude_mode = "relativeToGround"
            # raise ValueError(
            #     "altitude_mode must be one of "
            #     + "relativeToGround, clampToGround, absolute,
            #     + relativeToSeaFloor, clampToSeaFloor"
            # )

    def from_element(self, element):
        super().from_element(element)
        longitude = element.find(f"{self.ns}longitude")
        if longitude is not None:
            self.longitude = longitude.text
        latitude = element.find(f"{self.ns}latitude")
        if latitude is not None:
            self.latitude = latitude.text
        altitude = element.find(f"{self.ns}altitude")
        if altitude is not None:
            self.altitude = altitude.text
        heading = element.find(f"{self.ns}heading")
        if heading is not None:
            self.heading = heading.text
        tilt = element.find(f"{self.ns}tilt")
        if tilt is not None:
            self.tilt = tilt.text
        range_var = element.find(f"{self.ns}range")
        if range_var is not None:
            self.range = range_var.text
        altitude_mode = element.find(f"{self.ns}altitudeMode")
        if altitude_mode is not None:
            self.altitude_mode = altitude_mode.text
        else:
            altitude_mode = element.find(f"{gx.NS}altitudeMode")
            self.altitude_mode = altitude_mode.text

    def etree_element(self):
        element = super().etree_element()
        if self.longitude:
            longitude = etree.SubElement(element, f"{self.ns}longitude")
            longitude.text = self._longitude
        if self.latitude:
            latitude = etree.SubElement(element, f"{self.ns}latitude")
            latitude.text = self.latitude
        if self.altitude:
            altitude = etree.SubElement(element, f"{self.ns}altitude")
            altitude.text = self._altitude
        if self.heading:
            heading = etree.SubElement(element, f"{self.ns}heading")
            heading.text = self._heading
        if self.tilt:
            tilt = etree.SubElement(element, f"{self.ns}tilt")
            tilt.text = self._tilt
        if self.range:
            range_var = etree.SubElement(element, f"{self.ns}range")
            range_var.text = self._range
        if self.altitude_mode in ("clampedToGround", "relativeToGround", "absolute"):
            altitude_mode = etree.SubElement(element, f"{self.ns}altitudeMode")
        elif self.altitude_mode in ("clampedToSeaFloor", "relativeToSeaFloor"):
            altitude_mode = etree.SubElement(element, f"{gx.NS}altitudeMode")
        altitude_mode.text = self.altitude_mode
        return element


__all__ = [
    "Data",
    "Document",
    "ExtendedData",
    "Folder",
    "PhotoOverlay",
    "GroundOverlay",
    "KML",
    "Placemark",
    "Schema",
    "SchemaData",
    "TimeSpan",
    "TimeStamp",
    "Camera",
    "LookAt",
]
