# -*- coding: utf-8 -*-
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
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse  # Python 3
import warnings

# from .geometry import Point, LineString, Polygon
# from .geometry import MultiPoint, MultiLineString, MultiPolygon
# from .geometry import LinearRing
from .geometry import Geometry

from datetime import datetime, date

# note that there are some ISO 8601 timeparsers at pypi
# but in my tests all of them had some errors so we rely on the
# tried and tested dateutil here which is more stable. As a side effect
# we can also parse non ISO compliant dateTimes
import dateutil.parser

import logging
logger = logging.getLogger('fastkml.kml')

from .config import etree

from .base import _BaseObject, _XMLObject

from .styles import StyleUrl, Style, StyleMap, _StyleSelector

import fastkml.atom as atom
# import fastkml.gx as gx
import fastkml.config as config

try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str


class KML(object):
    """ represents a KML File """

    _features = []
    ns = None

    def __init__(self, ns=None):
        """ The namespace (ns) may be empty ('') if the 'kml:' prefix is
        undesired. Note that all child elements like Document or Placemark need
        to be initialized with empty namespace as well in this case.

        """
        self._features = []

        if ns is None:
            self.ns = config.NS
        else:
            self.ns = ns

    def from_string(self, xml_string):
        """ create a KML object from a xml string"""
        if config.LXML:
            element = etree.fromstring(
                xml_string,
                parser=etree.XMLParser(huge_tree=True)
            )
        else:
            element = etree.XML(xml_string)

        if element.tag.endswith('kml'):
            ns = element.tag.rstrip('kml')
            documents = element.findall('%sDocument' % ns)
            for document in documents:
                feature = Document(ns)
                feature.from_element(document)
                self.append(feature)
            folders = element.findall('%sFolder' % ns)
            for folder in folders:
                feature = Folder(ns)
                feature.from_element(folder)
                self.append(feature)
            placemarks = element.findall('%sPlacemark' % ns)
            for placemark in placemarks:
                feature = Placemark(ns)
                feature.from_element(placemark)
                self.append(feature)
        else:
            raise TypeError

    def etree_element(self):
        # self.ns may be empty, which leads to unprefixed kml elements.
        # However, in this case the xlmns should still be mentioned on the kml
        # element, just without prefix.
        if not self.ns:
            root = etree.Element('%skml' % self.ns)
            root.set('xmlns', config.NS[1:-1])
        else:
            if config.LXML:
                root = etree.Element(
                    '%skml' % self.ns,
                    nsmap={None: self.ns[1:-1]}
                )
            else:
                root = etree.Element('%skml' % self.ns)
        for feature in self.features():
            root.append(feature.etree_element())
        return root

    def to_string(self, prettyprint=False):
        """ Return the KML Object as serialized xml """
        if config.LXML and prettyprint:
            return etree.tostring(
                self.etree_element(),
                encoding='utf-8',
                pretty_print=True).decode('UTF-8')
        else:
            return etree.tostring(
                self.etree_element(),
                encoding='utf-8').decode('UTF-8')

    def features(self):
        """ iterate over features """
        for feature in self._features:
            if isinstance(feature, (Document, Folder, Placemark)):
                yield feature
            else:
                raise TypeError(
                    "Features must be instances of "
                    "(Document, Folder, Placemark)"
                )

    def append(self, kmlobj):
        """ append a feature """
        if isinstance(kmlobj, (Document, Folder, Placemark)):
            self._features.append(kmlobj)
        else:
            raise TypeError(
                "Features must be instances of (Document, Folder, Placemark)")


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

    _phoneNumber = None
    # A string value representing a telephone number.
    # This element is used by Google Maps Mobile only.

    _snippet = None    # XXX
    # _snippet is eiter a tuple of a string Snippet.text and an integer
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

    _styleUrl = None
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

    _time_span = None
    # Associates this Feature with a period of time.
    _time_stamp = None
    # Associates this Feature with a point in time.

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
        self, ns=None, id=None, name=None, description=None,
        styles=None, styleUrl=None, extended_data=None
    ):
        super(_Feature, self).__init__(ns, id)
        self.name = name
        self.description = description
        self.styleUrl = styleUrl
        self._styles = []
        if styles:
            for style in styles:
                self.append_style(style)
        self.extended_data = extended_data

    @property
    def styleUrl(self):
        """ Returns the url only, not a full StyleUrl object.
            if you need the full StyleUrl object use _styleUrl """
        if isinstance(self._styleUrl, StyleUrl):
            return self._styleUrl.url

    @styleUrl.setter
    def styleUrl(self, styleurl):
        """ you may pass a StyleUrl Object, a string or None """
        if isinstance(styleurl, StyleUrl):
            self._styleUrl = styleurl
        elif isinstance(styleurl, basestring):
            s = StyleUrl(self.ns, url=styleurl)
            self._styleUrl = s
        elif styleurl is None:
            self._styleUrl = None
        else:
            raise ValueError

    @property
    def timeStamp(self):
        """ This just returns the datetime portion of the timestamp"""
        if self._time_stamp is not None:
            return self._time_stamp.timestamp[0]

    @timeStamp.setter
    def timeStamp(self, dt):
        if dt is None:
            self._time_stamp = None
        else:
            self._time_stamp = TimeStamp(timestamp=dt)
        if self._time_span is not None:
            logger.warn('Setting a TimeStamp, TimeSpan deleted')
            self._time_span = None

    @property
    def begin(self):
        if self._time_span is not None:
            return self._time_span.begin[0]

    @begin.setter
    def begin(self, dt):
        if self._time_span is None:
            self._time_span = TimeSpan(begin=dt)
        else:
            if self._time_span.begin is None:
                self._time_span.begin = [dt, None]
            else:
                self._time_span.begin[0] = dt
        if self._time_stamp is not None:
            logger.warn('Setting a TimeSpan, TimeStamp deleted')
            self._time_stamp = None

    @property
    def end(self):
        if self._time_span is not None:
            return self._time_span.end[0]

    @end.setter
    def end(self, dt):
        if self._time_span is None:
            self._time_span = TimeSpan(end=dt)
        else:
            if self._time_span.end is None:
                self._time_span.end = [dt, None]
            else:
                self._time_span.end[0] = dt
        if self._time_stamp is not None:
            logger.warn('Setting a TimeSpan, TimeStamp deleted')
            self._time_stamp = None

    @property
    def link(self):
        return self._atom_link.href

    @link.setter
    def link(self, url):
        if isinstance(url, basestring):
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
        elif isinstance(name, basestring):
            if self._atom_author is None:
                self._atom_author = atom.Author(name=name)
            else:
                self._atom_author.name = name
        elif name is None:
            self._atom_author = None
        else:
            raise TypeError

    def append_style(self, style):
        """ append a style to the feature """
        if isinstance(style, _StyleSelector):
            self._styles.append(style)
        else:
            raise TypeError

    def styles(self):
        """ iterate over the styles of this feature """
        for style in self._styles:
            if isinstance(style, _StyleSelector):
                yield style
            else:
                raise TypeError

    @property
    def snippet(self):
        if self._snippet:
            if isinstance(self._snippet, dict):
                text = self._snippet.get('text')
                if text:
                    assert (isinstance(text, basestring))
                    max_lines = self._snippet.get('maxLines', None)
                    if max_lines is None:
                        return {'text': text}
                    elif int(max_lines) > 0:
                        # if maxLines <=0 ignore it
                        return {'text': text, 'maxLines': max_lines}
            elif isinstance(self._snippet, basestring):
                return self._snippet
            else:
                raise ValueError(
                    "Snippet must be dict of "
                    "{'text':t, 'maxLines':i} or string"
                )

    @snippet.setter
    def snippet(self, snip=None):
        self._snippet = {}
        if isinstance(snip, dict):
            self._snippet['text'] = snip.get('text')
            max_lines = snip.get('maxLines')
            if max_lines is not None:
                self._snippet['maxLines'] = int(snip['maxLines'])
        elif isinstance(snip, basestring):
            self._snippet['text'] = snip
        elif snip is None:
            self._snippet = None
        else:
            raise ValueError(
                "Snippet must be dict of {'text':t, 'maxLines':i} or string"
            )

    @property
    def address(self):
        if self._address:
            return self._address

    @address.setter
    def address(self, address):
        if isinstance(address, basestring):
            self._address = address
        elif address is None:
            self._address = None
        else:
            raise ValueError

    @property
    def phoneNumber(self):
        if self._phoneNumber:
            return self._phoneNumber

    @phoneNumber.setter
    def phoneNumber(self, phoneNumber):
        if isinstance(phoneNumber, basestring):
            self._phoneNumber = phoneNumber
        elif phoneNumber is None:
            self._phoneNumber = None
        else:
            raise ValueError

    def etree_element(self):
        element = super(_Feature, self).etree_element()
        if self.name:
            name = etree.SubElement(element, "%sname" % self.ns)
            name.text = self.name
        if self.description:
            description = etree.SubElement(element, "%sdescription" % self.ns)
            description.text = self.description
        visibility = etree.SubElement(element, "%svisibility" % self.ns)
        visibility.text = str(self.visibility)
        if self.isopen:
            isopen = etree.SubElement(element, "%sopen" % self.ns)
            isopen.text = str(self.isopen)
        if self._styleUrl is not None:
            element.append(self._styleUrl.etree_element())
        for style in self.styles():
            element.append(style.etree_element())
        if self.snippet:
            snippet = etree.SubElement(element, "%sSnippet" % self.ns)
            if isinstance(self.snippet, basestring):
                snippet.text = self.snippet
            else:
                assert (isinstance(self.snippet['text'], basestring))
                snippet.text = self.snippet['text']
                if self.snippet.get('maxLines'):
                    snippet.set('maxLines', str(self.snippet['maxLines']))
        if (self._time_span is not None) and (self._time_stamp is not None):
            raise ValueError(
                'Either Timestamp or Timespan can be defined, not both'
            )
        elif self._time_span is not None:
            element.append(self._time_span.etree_element())
        elif self._time_stamp is not None:
            element.append(self._time_stamp.etree_element())
        if self._atom_link is not None:
            element.append(self._atom_link.etree_element())
        if self._atom_author is not None:
            element.append(self._atom_author.etree_element())
        if self.extended_data is not None:
            element.append(self.extended_data.etree_element())
        if self._address is not None:
            address = etree.SubElement(element, '%saddress' % self.ns)
            address.text = self._address
        if self._phoneNumber is not None:
            phoneNumber = etree.SubElement(element, '%sphoneNumber' % self.ns)
            phoneNumber.text = self._phoneNumber
        return element

    def from_element(self, element):
        super(_Feature, self).from_element(element)
        name = element.find('%sname' % self.ns)
        if name is not None:
            self.name = name.text
        description = element.find('%sdescription' % self.ns)
        if description is not None:
            self.description = description.text
        visibility = element.find('%svisibility' % self.ns)
        if visibility is not None:
            if visibility.text in ['1', 'true']:
                self.visibility = 1
            else:
                self.visibility = 0
        isopen = element.find('%sopen' % self.ns)
        if isopen is not None:
            if isopen.text in ['1', 'true']:
                self.isopen = 1
            else:
                self.isopen = 0
        styles = element.findall('%sStyle' % self.ns)
        for style in styles:
            s = Style(self.ns)
            s.from_element(style)
            self.append_style(s)
        styles = element.findall('%sStyleMap' % self.ns)
        for style in styles:
            s = StyleMap(self.ns)
            s.from_element(style)
            self.append_style(s)
        style_url = element.find('%sstyleUrl' % self.ns)
        if style_url is not None:
            s = StyleUrl(self.ns)
            s.from_element(style_url)
            self._styleUrl = s
        snippet = element.find('%sSnippet' % self.ns)
        if snippet is not None:
            _snippet = {'text': snippet.text}
            if snippet.get('maxLines'):
                _snippet['maxLines'] = int(snippet.get('maxLines'))
            self.snippet = _snippet
        timespan = element.find('%sTimeSpan' % self.ns)
        if timespan is not None:
            s = TimeSpan(self.ns)
            s.from_element(timespan)
            self._time_span = s
        timestamp = element.find('%sTimeStamp' % self.ns)
        if timestamp is not None:
            s = TimeStamp(self.ns)
            s.from_element(timestamp)
            self._time_stamp = s
        atom_link = element.find('%slink' % atom.NS)
        if atom_link is not None:
            s = atom.Link()
            s.from_element(atom_link)
            self._atom_link = s
        atom_author = element.find('%sauthor' % atom.NS)
        if atom_author is not None:
            s = atom.Author()
            s.from_element(atom_author)
            self._atom_author = s
        extended_data = element.find('%sExtendedData' % self.ns)
        if extended_data is not None:
            x = ExtendedData(self.ns)
            x.from_element(extended_data)
            self.extended_data = x
            # else:
            #    logger.warn(
            #        'arbitrary or typed extended data is not yet supported'
            #    )
        address = element.find('%saddress' % self.ns)
        if address is not None:
            self.address = address.text
        phoneNumber = element.find('%sphoneNumber' % self.ns)
        if phoneNumber is not None:
            self.phoneNumber = phoneNumber.text


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
        self, ns=None, id=None, name=None, description=None,
        styles=None, styleUrl=None
    ):
        super(_Container, self).__init__(
            ns, id, name, description, styles, styleUrl
        )
        self._features = []

    def features(self):
        """ iterate over features """
        for feature in self._features:
            if isinstance(feature, (Folder, Placemark, Document)):
                yield feature
            else:
                raise TypeError(
                    "Features must be instances of "
                    "(Folder, Placemark, Document)"
                )

    def etree_element(self):
        element = super(_Container, self).etree_element()
        for feature in self.features():
            element.append(feature.etree_element())
        return element

    def append(self, kmlobj):
        """ append a feature """
        if isinstance(kmlobj, (Folder, Placemark, Document)):
            self._features.append(kmlobj)
        else:
            raise TypeError(
                "Features must be instances of "
                "(Folder, Placemark, Document)"
            )
        assert(kmlobj != self)


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

    _drawOrder = None
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
        self, ns=None, id=None, name=None, description=None,
        styles=None, styleUrl=None
    ):
        super(_Overlay, self).__init__(
            ns, id, name, description, styles, styleUrl
        )

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if isinstance(color, basestring):
            self._color = color
        elif color is None:
            self._color = None
        else:
            raise ValueError

    @property
    def drawOrder(self):
        return self._drawOrder

    @drawOrder.setter
    def drawOrder(self, value):
        if isinstance(value, (basestring, int, float)):
            self._drawOrder = str(value)
        elif value is None:
            self._drawOrder = None
        else:
            raise ValueError

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, url):
        if isinstance(url, basestring):
            if not url.startswith('<href>'):
                url = '<href>' + url
            if not url.endswith('</href>'):
                url = url + '</href>'
            self._icon = url
        elif url is None:
            self._icon = None
        else:
            raise ValueError

    def etree_element(self):
        element = super(_Overlay, self).etree_element()
        if self._color:
            color = etree.SubElement(element, "%scolor" % self.ns)
            color.text = self._color
        if self._drawOrder:
            drawOrder = etree.SubElement(element, "%sdrawOrder" % self.ns)
            drawOrder.text = self._drawOrder
        if self._icon:
            icon = etree.SubElement(element, "%sicon" % self.ns)
            icon.text = self._icon
        return element

    def from_element(self, element):
        super(_Overlay, self).from_element(element)
        color = element.find('%scolor' % self.ns)
        if color is not None:
            self.color = color.text
        drawOrder = element.find('%sdrawOrder' % self.ns)
        if drawOrder is not None:
            self.drawOrder = drawOrder.text
        icon = element.find('%sicon' % self.ns)
        if icon is not None:
            self.icon = icon.text


class GroundOverlay(_Overlay):
    """
    This element draws an image overlay draped onto the terrain. The <href>
    child of <Icon> specifies the image to be used as the overlay. This file
    can be either on a local file system or on a web server. If this element is
    omitted or contains no <href>, a rectangle is drawn using the color and
    LatLonBox bounds defined by the ground overlay.
    """
    __name__ = 'GroundOverlay'

    _altitude = None
    # Specifies the distance above the earth's surface, in meters, and is
    # interpreted according to the altitude mode.

    _altitudeMode = 'clampToGround'
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
    _latLonQuad = None

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        if isinstance(value, (basestring, int, float)):
            self._altitude = str(value)
        elif value is None:
            self._altitude = None
        else:
            raise ValueError

    @property
    def altitudeMode(self):
        return self._altitudeMode

    @altitudeMode.setter
    def altitudeMode(self, mode):
        if mode in ('clampToGround', 'absolute'):
                self._altitudeMode = str(mode)
        else:
            self._altitudeMode = 'clampToGround'

    @property
    def north(self):
        return self._north

    @north.setter
    def north(self, value):
        if isinstance(value, (basestring, int, float)):
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
        if isinstance(value, (basestring, int, float)):
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
        if isinstance(value, (basestring, int, float)):
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
        if isinstance(value, (basestring, int, float)):
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
        if isinstance(value, (basestring, int, float)):
            self._rotation = str(value)
        elif value is None:
            self._rotation = None
        else:
            raise ValueError

    def latLonBox(self, north, south, east, west, rotation=0):
        # TODO: Check for bounds (0:+/-90 or 0:+/-180 degrees)
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.rotation = rotation

    def etree_element(self):
        element = super(GroundOverlay, self).etree_element()
        if self._altitude:
            altitude = etree.SubElement(element, "%saltitude" % self.ns)
            altitude.text = self._altitude
            if self._altitudeMode:
                altitudeMode = etree.SubElement(
                    element, "%saltitudeMode" % self.ns
                )
                altitudeMode.text = self._altitudeMode
        if all([self._north, self._south, self._east, self._west]):
            latLonBox = etree.SubElement(element, '%slatLonBox' % self.ns)
            north = etree.SubElement(latLonBox, '%snorth' % self.ns)
            north.text = self._north
            south = etree.SubElement(latLonBox, '%ssouth' % self.ns)
            south.text = self._south
            east = etree.SubElement(latLonBox, '%seast' % self.ns)
            east.text = self._east
            west = etree.SubElement(latLonBox, '%swest' % self.ns)
            west.text = self._west
            if self._rotation:
                rotation = etree.SubElement(latLonBox, '%srotation' % self.ns)
                rotation.text = self._rotation

        return element

    def from_element(self, element):
        super(GroundOverlay, self).from_element(element)
        altitude = element.find('%saltitude' % self.ns)
        if altitude is not None:
            self.altitude = altitude.text
        altitudeMode = element.find('%saltitudeMode' % self.ns)
        if altitudeMode is not None:
            self.altitudeMode = altitudeMode.text
        latLonBox = element.find('%slatLonBox' % self.ns)
        if latLonBox is not None:
            north = latLonBox.find('%snorth' % self.ns)
            if north is not None:
                self.north = north.text
            south = latLonBox.find('%ssouth' % self.ns)
            if south is not None:
                self.south = south.text
            east = latLonBox.find('%seast' % self.ns)
            if east is not None:
                self.east = east.text
            west = latLonBox.find('%swest' % self.ns)
            if west is not None:
                self.west = west.text
            rotation = latLonBox.find('%srotation' % self.ns)
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
            for schema in self._schemata:
                yield schema

    def append_schema(self, schema):
        if self._schemata is None:
            self._schemata = []
        if isinstance(schema, Schema):
            self._schemata.append(schema)
        else:
            s = Schema(schema)
            self._schemata.append(s)

    def from_element(self, element):
        super(Document, self).from_element(element)
        folders = element.findall('%sFolder' % self.ns)
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall('%sPlacemark' % self.ns)
        for placemark in placemarks:
            feature = Placemark(self.ns)
            feature.from_element(placemark)
            self.append(feature)
        schemata = element.findall('%sSchema' % self.ns)
        for schema in schemata:
            s = Schema(self.ns, id='default')
            s.from_element(schema)
            self.append_schema(s)

    def etree_element(self):
        element = super(Document, self).etree_element()
        if self._schemata is not None:
            for schema in self._schemata:
                element.append(schema.etree_element())
        return element

    def get_style_by_url(self, styleUrl):
        id = urlparse.urlparse(styleUrl).fragment
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
        super(Folder, self).from_element(element)
        folders = element.findall('%sFolder' % self.ns)
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall('%sPlacemark' % self.ns)
        for placemark in placemarks:
            feature = Placemark(self.ns)
            feature.from_element(placemark)
            self.append(feature)
        documents = element.findall('%sDocument' % self.ns)
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
        super(Placemark, self).from_element(element)
        point = element.find('%sPoint' % self.ns)
        if point is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(point)
            self._geometry = geom
            return
        line = element.find('%sLineString' % self.ns)
        if line is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(line)
            self._geometry = geom
            return
        polygon = element.find('%sPolygon' % self.ns)
        if polygon is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(polygon)
            self._geometry = geom
            return
        linearring = element.find('%sLinearRing' % self.ns)
        if linearring is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(linearring)
            self._geometry = geom
            return
        multigeometry = element.find('%sMultiGeometry' % self.ns)
        if multigeometry is not None:
            geom = Geometry(ns=self.ns)
            geom.from_element(multigeometry)
            self._geometry = geom
            return
        logger.warn('No geometries found')

    def etree_element(self):
        element = super(Placemark, self).etree_element()
        if self._geometry is not None:
            element.append(self._geometry.etree_element())
        else:
            logger.error('Object does not have a geometry')
        return element


class _TimePrimitive(_BaseObject):
    """ The dateTime is defined according to XML Schema time.
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

    RESOLUTIONS = ['gYear', 'gYearMonth', 'date', 'dateTime']

    def get_resolution(self, dt, resolution=None):
        if resolution:
            if resolution not in self.RESOLUTIONS:
                raise ValueError
            else:
                return resolution
        else:
            if isinstance(dt, datetime):
                resolution = 'dateTime'
            elif isinstance(dt, date):
                resolution = 'date'
            else:
                resolution = None
        return resolution

    def parse_str(self, datestr):
        resolution = 'dateTime'
        year = 0
        month = 1
        day = 1
        if len(datestr) == 4:
            resolution = 'gYear'
            year = int(datestr)
            dt = datetime(year, month, day)
        elif len(datestr) == 6:
            resolution = 'gYearMonth'
            year = int(datestr[:4])
            month = int(datestr[-2:])
            dt = datetime(year, month, day)
        elif len(datestr) == 7:
            resolution = 'gYearMonth'
            year = int(datestr.split('-')[0])
            month = int(datestr.split('-')[1])
            dt = datetime(year, month, day)
        elif len(datestr) == 8 or len(datestr) == 10:
            resolution = 'date'
            dt = dateutil.parser.parse(datestr)
        elif len(datestr) > 10:
            resolution = 'dateTime'
            dt = dateutil.parser.parse(datestr)
        else:
            raise ValueError
        return [dt, resolution]

    def date_to_string(self, dt, resolution=None):
        if isinstance(dt, (date, datetime)):
            resolution = self.get_resolution(dt, resolution)
            if resolution == 'gYear':
                return dt.strftime('%Y')
            elif resolution == 'gYearMonth':
                return dt.strftime('%Y-%m')
            elif resolution == 'date':
                if isinstance(dt, datetime):
                    return dt.date().isoformat()
                else:
                    return dt.isoformat()
            elif resolution == 'dateTime':
                return dt.isoformat()


class TimeStamp(_TimePrimitive):
    """ Represents a single moment in time. """
    __name__ = 'TimeStamp'
    timestamp = None

    def __init__(self, ns=None, id=None, timestamp=None, resolution=None):
        super(TimeStamp, self).__init__(ns, id)
        resolution = self.get_resolution(timestamp, resolution)
        self.timestamp = [timestamp, resolution]

    def etree_element(self):
        element = super(TimeStamp, self).etree_element()
        when = etree.SubElement(element, "%swhen" % self.ns)
        when.text = self.date_to_string(*self.timestamp)
        return element

    def from_element(self, element):
        super(TimeStamp, self).from_element(element)
        when = element.find('%swhen' % self.ns)
        if when is not None:
            self.timestamp = self.parse_str(when.text)


class TimeSpan(_TimePrimitive):
    """ Represents an extent in time bounded by begin and end dateTimes.
    """
    __name__ = 'TimeSpan'
    begin = None
    end = None

    def __init__(
        self, ns=None, id=None, begin=None, begin_res=None,
        end=None, end_res=None
    ):
        super(TimeSpan, self).__init__(ns, id)
        if begin:
            resolution = self.get_resolution(begin, begin_res)
            self.begin = [begin, resolution]
        if end:
            resolution = self.get_resolution(end, end_res)
            self.end = [end, resolution]

    def from_element(self, element):
        super(TimeSpan, self).from_element(element)
        begin = element.find('%sbegin' % self.ns)
        if begin is not None:
            self.begin = self.parse_str(begin.text)
        end = element.find('%send' % self.ns)
        if end is not None:
            self.end = self.parse_str(end.text)

    def etree_element(self):
        element = super(TimeSpan, self).etree_element()
        if self.begin is not None:
            text = self.date_to_string(*self.begin)
            if text:
                begin = etree.SubElement(element, "%sbegin" % self.ns)
                begin.text = text
        if self.end is not None:
            text = self.date_to_string(*self.end)
            if text:
                end = etree.SubElement(element, "%send" % self.ns)
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
            raise ValueError('Id is required for schema')
        super(Schema, self).__init__(ns, id)
        self.simple_fields = fields
        self.name = name

    @property
    def simple_fields(self):
        sfs = []
        for simple_field in self._simple_fields:
            if simple_field.get('type') and simple_field.get('name'):
                sfs.append({
                    'type': simple_field['type'],
                    'name': simple_field['name'],
                    'displayName': simple_field.get('displayName')
                })
        return tuple(sfs)

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
            raise ValueError('Fields must be of type list, tuple or dict')

    def append(self, type, name, displayName=None):
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
            'string', 'int', 'uint', 'short', 'ushort',
            'float', 'double', 'bool'
        ]
        if type not in allowed_types:
            raise TypeError(
                "type must be one of ""'string', 'int', 'uint', 'short', "
                "'ushort', 'float', 'double', 'bool'"
            )
        else:
            # TODO explicit type conversion to check for the right type
            pass
        self._simple_fields.append({'type': type, 'name': name,
                                    'displayName': displayName})

    def from_element(self, element):
        super(Schema, self).from_element(element)
        self.name = element.get('name')
        simple_fields = element.findall('%sSimpleField' % self.ns)
        self.simple_fields = None
        for simple_field in simple_fields:
            sfname = simple_field.get('name')
            sftype = simple_field.get('type')
            display_name = simple_field.find('%sdisplayName' % self.ns)
            if display_name is not None:
                sfdisplay_name = display_name.text
            else:
                sfdisplay_name = None
            self.append(sftype, sfname, sfdisplay_name)

    def etree_element(self):
        element = super(Schema, self).etree_element()
        if self.name:
            element.set('name', self.name)
        for simple_field in self.simple_fields:
            sf = etree.SubElement(element, "%sSimpleField" % self.ns)
            sf.set('type', simple_field['type'])
            sf.set('name', simple_field['name'])
            if simple_field.get('displayName'):
                dn = etree.SubElement(sf, "%sdisplayName" % self.ns)
                dn.text = simple_field['displayName']

        return element


class ExtendedData(_XMLObject):
    """ Represents a list of untyped name/value pairs. See docs:

    -> 'Adding Untyped Name/Value Pairs'
       https://developers.google.com/kml/documentation/extendeddata

    """
    __name__ = 'ExtendedData'

    def __init__(self, ns=None, elements=None):
        super(ExtendedData, self).__init__(ns)
        self.elements = elements or []

    def etree_element(self):
        element = super(ExtendedData, self).etree_element()
        for subelement in self.elements:
            element.append(subelement.etree_element())
        return element

    def from_element(self, element):
        super(ExtendedData, self).from_element(element)
        self.elements = []
        untyped_data = element.findall('%sData' % self.ns)
        for ud in untyped_data:
            el = Data(self.ns)
            el.from_element(ud)
            self.elements.append(el)
        typed_data = element.findall('%sSchemaData' % self.ns)
        for sd in typed_data:
            el = SchemaData(self.ns, 'dummy')
            el.from_element(sd)
            self.elements.append(el)


class UntypedExtendedData(ExtendedData):
    def __init__(self, ns=None, elements=None):
        super(UntypedExtendedData, self).__init__(ns, elements)
        warnings.warn(
            "UntypedExtendedData is deprecated use ExtendedData instead",
            DeprecationWarning
        )


class Data(_XMLObject):
    """ Represents an untyped name/value pair with optional display name. """

    __name__ = 'Data'

    def __init__(self, ns=None, name=None, value=None, display_name=None):
        super(Data, self).__init__(ns)

        self.name = name
        self.value = value
        self.display_name = display_name

    def etree_element(self):
        element = super(Data, self).etree_element()
        element.set('name', self.name)
        value = etree.SubElement(element, "%svalue" % self.ns)
        value.text = self.value
        if self.display_name:
            display_name = etree.SubElement(element, "%sdisplayName" % self.ns)
            display_name.text = self.display_name
        return element

    def from_element(self, element):
        super(Data, self).from_element(element)
        self.name = element.get('name')
        self.value = element.find('%svalue' % self.ns).text
        display_name = element.find('%sdisplayName' % self.ns)
        if display_name is not None:
            self.display_name = display_name.text


class UntypedExtendedDataElement(Data):
    def __init__(self, ns=None, name=None, value=None, display_name=None):
        super(UntypedExtendedDataElement, self).__init__(
            ns, name, value, display_name
        )
        warnings.warn(
            "UntypedExtendedDataElement is deprecated use Data instead",
            DeprecationWarning
        )


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
    __name__ = 'SchemaData'
    schema_url = None
    _data = None

    def __init__(self, ns=None, schema_url=None, data=None):
        super(SchemaData, self).__init__(ns)
        if (not isinstance(schema_url, basestring)) or (not schema_url):
            raise ValueError('required parameter schema_url missing')
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
            raise TypeError('data must be of type tuple or list')

    def append_data(self, name, value):
        if isinstance(name, basestring) and name:
            self._data.append({'name': name, 'value': value})
        else:
            raise TypeError('name must be a nonempty string')

    def etree_element(self):
        element = super(SchemaData, self).etree_element()
        element.set('schemaUrl', self.schema_url)
        for data in self.data:
            sd = etree.SubElement(element, "%sSimpleData" % self.ns)
            sd.set('name', data['name'])
            sd.text = data['value']
        return element

    def from_element(self, element):
        super(SchemaData, self).from_element(element)
        self.data = []
        self.schema_url = element.get('schemaUrl')
        simple_data = element.findall('%sSimpleData' % self.ns)
        for sd in simple_data:
            self.append_data(sd.get('name'), sd.text)
