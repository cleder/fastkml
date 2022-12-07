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
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

import fastkml.atom as atom
import fastkml.config as config
import fastkml.gx as gx
from fastkml.base import _BaseObject
from fastkml.data import ExtendedData
from fastkml.data import Schema
from fastkml.geometry import Geometry
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.styles import _StyleSelector
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.types import Element
from fastkml.views import Camera
from fastkml.views import LookAt

logger = logging.getLogger(__name__)


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
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        styles: Optional[List[Style]] = None,
        style_url: Optional[str] = None,
        extended_data: None = None,
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        self.name = name
        self.description = description
        self.style_url = style_url
        self._styles = []
        if styles:
            for style in styles:
                self.append_style(style)
        self.extended_data = extended_data

    @property
    def style_url(self) -> Optional[str]:
        """Returns the url only, not a full StyleUrl object.
        if you need the full StyleUrl object use _style_url"""
        if isinstance(self._style_url, StyleUrl):
            return self._style_url.url

    @style_url.setter
    def style_url(self, styleurl: Union[str, StyleUrl, None]) -> None:
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
    def time_stamp(self):
        """This just returns the datetime portion of the timestamp"""
        if self._timestamp is not None:
            return self._timestamp.timestamp[0]

    @time_stamp.setter
    def time_stamp(self, dt):
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

    def append_style(self, style: Union[Style, StyleMap]) -> None:
        """append a style to the feature"""
        if isinstance(style, _StyleSelector):
            self._styles.append(style)
        else:
            raise TypeError

    def styles(self) -> Iterator[Union[Style, StyleMap]]:
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

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.name:
            name = config.etree.SubElement(element, f"{self.ns}name")
            name.text = self.name
        if self.description:
            description = config.etree.SubElement(element, f"{self.ns}description")
            description.text = self.description
        if (self.camera is not None) and (self.look_at is not None):
            raise ValueError("Either Camera or LookAt can be defined, not both")
        if self.camera is not None:
            element.append(self._camera.etree_element())
        elif self.look_at is not None:
            element.append(self._look_at.etree_element())
        visibility = config.etree.SubElement(element, f"{self.ns}visibility")
        visibility.text = str(self.visibility)
        if self.isopen:
            isopen = config.etree.SubElement(element, f"{self.ns}open")
            isopen.text = str(self.isopen)
        if self._style_url is not None:
            element.append(self._style_url.etree_element())
        for style in self.styles():
            element.append(style.etree_element())
        if self.snippet:
            snippet = config.etree.SubElement(element, f"{self.ns}Snippet")
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
            address = config.etree.SubElement(element, f"{self.ns}address")
            address.text = self._address
        if self._phone_number is not None:
            phone_number = config.etree.SubElement(element, f"{self.ns}phoneNumber")
            phone_number.text = self._phone_number
        return element

    def from_element(self, element: Element) -> None:
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


class Icon(_BaseObject):
    """
    Represents an <Icon> element used in Overlays.

    Defines an image associated with an Icon style or overlay.
    The required <href> child element defines the location
    of the image to be used as the overlay or as the icon for the placemark.
    This location can either be on a local file system or a remote web server.
    The <gx:x>, <gx:y>, <gx:w>, and <gx:h> elements are used to select one
    icon from an image that contains multiple icons
    (often referred to as an icon palette).
    """

    __name__ = "Icon"

    _href = None
    _refresh_mode: str = None
    _refresh_interval = None
    _view_refresh_mode = None
    _view_refresh_time = None
    _view_bound_scale = None
    _view_format = None
    _http_query = None

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        href: Optional[str] = None,
        refresh_mode: Optional[str] = None,
        refresh_interval: Optional[float] = None,
        view_refresh_mode: Optional[str] = None,
        view_refresh_time: Optional[float] = None,
        view_bound_scale: Optional[float] = None,
        view_format: Optional[str] = None,
        http_query: Optional[str] = None,
    ) -> None:
        """Initialize the KML Icon Object."""
        super().__init__(ns=ns, id=id, target_id=target_id)
        self._href = href
        self._refresh_mode = refresh_mode
        self._refresh_interval = refresh_interval
        self._view_refresh_mode = view_refresh_mode
        self._view_refresh_time = view_refresh_time
        self._view_bound_scale = view_bound_scale
        self._view_format = view_format
        self._http_query = http_query

    @property
    def href(self) -> Optional[str]:
        """An HTTP address or a local file specification used to load an icon."""
        return self._href

    @href.setter
    def href(self, href) -> None:
        if isinstance(href, str):
            self._href = href
        elif href is None:
            self._href = None
        else:
            raise ValueError

    @property
    def refresh_mode(self) -> Optional[str]:
        """
        Specifies a time-based refresh mode.

        Can be one of the following:
          - onChange - refresh when the file is loaded and whenever the Link
            parameters change (the default).
          - onInterval - refresh every n seconds (specified in <refreshInterval>).
          - onExpire - refresh the file when the expiration time is reached.
        """
        return self._refresh_mode

    @refresh_mode.setter
    def refresh_mode(self, refresh_mode) -> None:
        if isinstance(refresh_mode, str):
            self._refresh_mode = refresh_mode
        elif refresh_mode is None:
            self._refresh_mode = None
        else:
            raise ValueError

    @property
    def refresh_interval(self) -> Optional[float]:
        """Indicates to refresh the file every n seconds."""
        return self._refresh_interval

    @refresh_interval.setter
    def refresh_interval(self, refresh_interval: Optional[float]) -> None:
        if isinstance(refresh_interval, float):
            self._refresh_interval = refresh_interval
        elif refresh_interval is None:
            self._refresh_interval = None
        else:
            raise ValueError

    @property
    def view_refresh_mode(self):
        """
        Specifies how the link is refreshed when the "camera" changes.

        Can be one of the following:
         - never (default) - Ignore changes in the view.
           Also ignore <viewFormat> parameters, if any.
         - onStop - Refresh the file n seconds after movement stops,
           where n is specified in <viewRefreshTime>.
         - onRequest - Refresh the file only when the user explicitly requests it.
           (For example, in Google Earth, the user right-clicks and selects Refresh
            in the Context menu.)
          - onRegion - Refresh the file when the Region becomes active.
        """
        return self._view_refresh_mode

    @view_refresh_mode.setter
    def view_refresh_mode(self, view_refresh_mode):
        if isinstance(view_refresh_mode, str):
            self._view_refresh_mode = view_refresh_mode
        elif view_refresh_mode is None:
            self._view_refresh_mode = None
        else:
            raise ValueError

    @property
    def view_refresh_time(self):
        """
        After camera movement stops, specifies the number of seconds to
        wait before refreshing the view.
        """
        return self._view_refresh_time

    @view_refresh_time.setter
    def view_refresh_time(self, view_refresh_time: Optional[float]):
        if isinstance(view_refresh_time, float):
            self._view_refresh_time = view_refresh_time
        elif view_refresh_time is None:
            self._view_refresh_time = None
        else:
            raise ValueError

    @property
    def view_bound_scale(self) -> Optional[float]:
        """
        Scales the BBOX parameters before sending them to the server.

        A value less than 1 specifies to use less than the full view (screen).
        A value greater than 1 specifies to fetch an area that extends beyond
        the edges of the current view.
        """
        return self._view_bound_scale

    @view_bound_scale.setter
    def view_bound_scale(self, view_bound_scale: Optional[float]) -> None:
        if isinstance(view_bound_scale, float):
            self._view_bound_scale = view_bound_scale
        elif view_bound_scale is None:
            self._view_bound_scale = None
        else:
            raise ValueError

    @property
    def view_format(self):
        """
        Specifies the format of the query string that is appended to the
        Link's <href> before the file is fetched.
        (If the <href> specifies a local file, this element is ignored.)

        This information matches the Web Map Service (WMS) bounding box specification.
        If you specify an empty <viewFormat> tag, no information is appended to the
        query string.
        You can also specify a custom set of viewing parameters to add to the query
        string. If you supply a format string, it is used instead of the BBOX
        information. If you also want the BBOX information, you need to add those
        parameters along with the custom parameters.
        You can use any of the following parameters in your format string:
         - [lookatLon], [lookatLat] - longitude and latitude of the point that
           <LookAt> is viewing
         - [lookatRange], [lookatTilt], [lookatHeading] - values used by the
           <LookAt> element (see descriptions of <range>, <tilt>, and <heading>
           in <LookAt>)
         - [lookatTerrainLon], [lookatTerrainLat], [lookatTerrainAlt] - point on the
           terrain in degrees/meters that <LookAt> is viewing
         - [cameraLon], [cameraLat], [cameraAlt] - degrees/meters of the eyepoint for
           the camera
         - [horizFov], [vertFov] - horizontal, vertical field of view for the camera
         - [horizPixels], [vertPixels] - size in pixels of the 3D viewer
         - [terrainEnabled] - indicates whether the 3D viewer is showing terrain (1)
           or not (0)
        """
        return self._view_format

    @view_format.setter
    def view_format(self, view_format):
        if isinstance(view_format, str):
            self._view_format = view_format
        elif view_format is None:
            self._view_format = None
        else:
            raise ValueError

    @property
    def http_query(self):
        """
        Appends information to the query string, based on the parameters specified.

        The following parameters are supported:
         - [clientVersion]
         - [kmlVersion]
         - [clientName]
         - [language]
        """
        return self._http_query

    @http_query.setter
    def http_query(self, http_query):
        if isinstance(http_query, str):
            self._http_query = http_query
        elif http_query is None:
            self._http_query = None
        else:
            raise ValueError

    def etree_element(self) -> Element:
        element = super().etree_element()

        if self._href:
            href = config.etree.SubElement(element, f"{self.ns}href")
            href.text = self._href
        if self._refresh_mode:
            refresh_mode = config.etree.SubElement(element, f"{self.ns}refreshMode")
            refresh_mode.text = self._refresh_mode
        if self._refresh_interval:
            refresh_interval = config.etree.SubElement(
                element, f"{self.ns}refreshInterval"
            )
            refresh_interval.text = str(self._refresh_interval)
        if self._view_refresh_mode:
            view_refresh_mode = config.etree.SubElement(
                element, f"{self.ns}viewRefreshMode"
            )
            view_refresh_mode.text = self._view_refresh_mode
        if self._view_refresh_time:
            view_refresh_time = config.etree.SubElement(
                element, f"{self.ns}viewRefreshTime"
            )
            view_refresh_time.text = str(self._view_refresh_time)
        if self._view_bound_scale:
            view_bound_scale = config.etree.SubElement(
                element, f"{self.ns}viewBoundScale"
            )
            view_bound_scale.text = str(self._view_bound_scale)
        if self._view_format:
            view_format = config.etree.SubElement(element, f"{self.ns}viewFormat")
            view_format.text = self._view_format
        if self._http_query:
            http_query = config.etree.SubElement(element, f"{self.ns}httpQuery")
            http_query.text = self._http_query

        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)

        href = element.find(f"{self.ns}href")
        if href is not None:
            self.href = href.text

        refresh_mode = element.find(f"{self.ns}refreshMode")
        if refresh_mode is not None:
            self.refresh_mode = refresh_mode.text

        refresh_interval = element.find(f"{self.ns}refreshInterval")
        if refresh_interval is not None:
            try:
                self.refresh_interval = float(refresh_interval.text)
            except ValueError:
                self.refresh_interval = None

        view_refresh_mode = element.find(f"{self.ns}viewRefreshMode")
        if view_refresh_mode is not None:
            self.view_refresh_mode = view_refresh_mode.text

        view_refresh_time = element.find(f"{self.ns}viewRefreshTime")
        if view_refresh_time is not None:
            try:
                self.view_refresh_time = float(view_refresh_time.text)
            except ValueError:
                self.view_refresh_time = None

        view_bound_scale = element.find(f"{self.ns}viewBoundScale")
        if view_bound_scale is not None:
            try:
                self.view_bound_scale = float(view_bound_scale.text)
            except ValueError:
                self.view_bound_scale = None

        view_format = element.find(f"{self.ns}viewFormat")
        if view_format is not None:
            self.view_format = view_format.text

        http_query = element.find(f"{self.ns}httpQuery")
        if http_query is not None:
            self.http_query = http_query.text


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
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        styles: Optional[List[Style]] = None,
        style_url: Optional[str] = None,
        features: None = None,
    ) -> None:
        super().__init__(
            ns=ns,
            id=id,
            target_id=target_id,
            name=name,
            description=description,
            styles=styles,
            style_url=style_url,
        )
        self._features = features or []

    def features(self) -> Iterator[_Feature]:
        """iterate over features"""
        for feature in self._features:
            if isinstance(feature, (Folder, Placemark, Document, _Overlay)):
                yield feature
            else:
                raise TypeError(
                    "Features must be instances of "
                    "(Folder, Placemark, Document, Overlay)"
                )

    def etree_element(self) -> Element:
        element = super().etree_element()
        for feature in self.features():
            element.append(feature.etree_element())
        return element

    def append(self, kmlobj: _Feature) -> None:
        """append a feature"""
        if isinstance(kmlobj, (Folder, Placemark, Document, _Overlay)):
            self._features.append(kmlobj)
        else:
            raise TypeError(
                "Features must be instances of "
                "(Folder, Placemark, Document, Overlay)"
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
    # values. The order of expression is alphaOverlay, blue, green, red
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
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        styles: None = None,
        style_url: Optional[str] = None,
        icon: Optional[Icon] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            id=id,
            target_id=target_id,
            name=name,
            description=description,
            styles=styles,
            style_url=style_url,
        )
        self._icon = icon

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
    def icon(self, value):
        if isinstance(value, Icon):
            self._icon = value
        elif value is None:
            self._icon = None
        else:
            raise ValueError

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self._color:
            color = config.etree.SubElement(element, f"{self.ns}color")
            color.text = self._color
        if self._draw_order:
            draw_order = config.etree.SubElement(element, f"{self.ns}drawOrder")
            draw_order.text = self._draw_order
        if self._icon:
            element.append(self._icon.etree_element())
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        color = element.find(f"{self.ns}color")
        if color is not None:
            self.color = color.text
        draw_order = element.find(f"{self.ns}drawOrder")
        if draw_order is not None:
            self.draw_order = draw_order.text
        icon = element.find(f"{self.ns}Icon")
        if icon is not None:
            s = Icon(self.ns)
            s.from_element(icon)
            self._icon = s


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

    _left_fow = None
    # Angle, in degrees, between the camera's viewing direction and the left side
    # of the view volume.

    _right_fov = None
    # Angle, in degrees, between the camera's viewing direction and the right side
    # of the view volume.

    _bottom_fov = None
    # Angle, in degrees, between the camera's viewing direction and the bottom side
    # of the view volume.

    _top_fov = None
    # Angle, in degrees, between the camera's viewing direction and the top side
    # of the view volume.

    _near = None
    # Measurement in meters along the viewing direction from the camera viewpoint
    # to the PhotoOverlay shape.

    _tile_size = "256"
    # Size of the tiles, in pixels. Tiles must be square, and <tileSize> must
    # be a power of 2. A tile size of 256 (the default) or 512 is recommended.
    # The original image is divided into tiles of this size, at varying resolutions.

    _max_width = None
    # Width in pixels of the original image.

    _max_height = None
    # Height in pixels of the original image.

    _grid_origin = None
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
    def left_fov(self):
        return self._left_fow

    @left_fov.setter
    def left_fov(self, value):
        if isinstance(value, (str, int, float)):
            self._left_fow = str(value)
        elif value is None:
            self._left_fow = None
        else:
            raise ValueError

    @property
    def right_fov(self):
        return self._right_fov

    @right_fov.setter
    def right_fov(self, value):
        if isinstance(value, (str, int, float)):
            self._right_fov = str(value)
        elif value is None:
            self._right_fov = None
        else:
            raise ValueError

    @property
    def bottom_fov(self):
        return self._bottom_fov

    @bottom_fov.setter
    def bottom_fov(self, value):
        if isinstance(value, (str, int, float)):
            self._bottom_fov = str(value)
        elif value is None:
            self._bottom_fov = None
        else:
            raise ValueError

    @property
    def top_fov(self):
        return self._top_fov

    @top_fov.setter
    def top_fov(self, value):
        if isinstance(value, (str, int, float)):
            self._top_fov = str(value)
        elif value is None:
            self._top_fov = None
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
    def tile_size(self):
        return self._tile_size

    @tile_size.setter
    def tile_size(self, value):
        if isinstance(value, (str, int, float)):
            self._tile_size = str(value)
        elif value is None:
            self._tile_size = None
        else:
            raise ValueError

    @property
    def max_width(self):
        return self._max_width

    @max_width.setter
    def max_width(self, value):
        if isinstance(value, (str, int, float)):
            self._max_width = str(value)
        elif value is None:
            self._max_width = None
        else:
            raise ValueError

    @property
    def max_height(self):
        return self._max_height

    @max_height.setter
    def max_height(self, value):
        if isinstance(value, (str, int, float)):
            self._max_height = str(value)
        elif value is None:
            self._max_height = None
        else:
            raise ValueError

    @property
    def grid_origin(self):
        return self._grid_origin

    @grid_origin.setter
    def grid_origin(self, value):
        if value in ("lowerLeft", "upperLeft"):
            self._grid_origin = str(value)
        elif value is None:
            self._grid_origin = None
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

    def view_volume(self, left_fov, right_fov, bottom_fov, top_fov, near):
        self.left_fov = left_fov
        self.right_fov = right_fov
        self.bottom_fov = bottom_fov
        self.top_fov = top_fov
        self.near = near

    def image_pyramid(self, tile_size, max_width, max_height, grid_origin):
        self.tile_size = tile_size
        self.max_width = max_width
        self.max_height = max_height
        self.grid_origin = grid_origin

    def etree_element(self):
        element = super().etree_element()
        if self._rotation:
            rotation = config.etree.SubElement(element, f"{self.ns}rotation")
            rotation.text = self._rotation
        if all(
            [
                self._left_fow,
                self._right_fov,
                self._bottom_fov,
                self._top_fov,
                self._near,
            ]
        ):
            view_volume = config.etree.SubElement(element, f"{self.ns}ViewVolume")
            left_fov = config.etree.SubElement(view_volume, f"{self.ns}leftFov")
            left_fov.text = self._left_fow
            right_fov = config.etree.SubElement(view_volume, f"{self.ns}rightFov")
            right_fov.text = self._right_fov
            bottom_fov = config.etree.SubElement(view_volume, f"{self.ns}bottomFov")
            bottom_fov.text = self._bottom_fov
            top_fov = config.etree.SubElement(view_volume, f"{self.ns}topFov")
            top_fov.text = self._top_fov
            near = config.etree.SubElement(view_volume, f"{self.ns}near")
            near.text = self._near
        if all([self._tile_size, self._max_width, self._max_height, self._grid_origin]):
            image_pyramid = config.etree.SubElement(element, f"{self.ns}ImagePyramid")
            tile_size = config.etree.SubElement(image_pyramid, f"{self.ns}tileSize")
            tile_size.text = self._tile_size
            max_width = config.etree.SubElement(image_pyramid, f"{self.ns}maxWidth")
            max_width.text = self._max_width
            max_height = config.etree.SubElement(image_pyramid, f"{self.ns}maxHeight")
            max_height.text = self._max_height
            grid_origin = config.etree.SubElement(image_pyramid, f"{self.ns}gridOrigin")
            grid_origin.text = self._grid_origin
        return element

    def from_element(self, element):
        super().from_element(element)
        rotation = element.find(f"{self.ns}rotation")
        if rotation is not None:
            self.rotation = rotation.text
        view_volume = element.find(f"{self.ns}ViewVolume")
        if view_volume is not None:
            left_fov = view_volume.find(f"{self.ns}leftFov")
            if left_fov is not None:
                self.left_fov = left_fov.text
            right_fov = view_volume.find(f"{self.ns}rightFov")
            if right_fov is not None:
                self.right_fov = right_fov.text
            bottom_fov = view_volume.find(f"{self.ns}bottomFov")
            if bottom_fov is not None:
                self.bottom_fov = bottom_fov.text
            top_fov = view_volume.find(f"{self.ns}topFov")
            if top_fov is not None:
                self.top_fov = top_fov.text
            near = view_volume.find(f"{self.ns}near")
            if near is not None:
                self.near = near.text
        image_pyramid = element.find(f"{self.ns}ImagePyramid")
        if image_pyramid is not None:
            tile_size = image_pyramid.find(f"{self.ns}tileSize")
            if tile_size is not None:
                self.tile_size = tile_size.text
            max_width = image_pyramid.find(f"{self.ns}maxWidth")
            if max_width is not None:
                self.max_width = max_width.text
            max_height = image_pyramid.find(f"{self.ns}maxHeight")
            if max_height is not None:
                self.max_height = max_height.text
            grid_origin = image_pyramid.find(f"{self.ns}gridOrigin")
            if grid_origin is not None:
                self.grid_origin = grid_origin.text
        point = element.find(f"{self.ns}Point")
        if point is not None:
            self.point = point.text
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

    def lat_lon_box(
        self, north: int, south: int, east: int, west: int, rotation: int = 0
    ) -> None:
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
        if -180 <= float(west) <= 180:
            self.west = west
        else:
            raise ValueError
        if -180 <= float(rotation) <= 180:
            self.rotation = rotation
        else:
            raise ValueError

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self._altitude:
            altitude = config.etree.SubElement(element, f"{self.ns}altitude")
            altitude.text = self._altitude
            if self._altitude_mode:
                altitude_mode = config.etree.SubElement(
                    element, f"{self.ns}altitudeMode"
                )
                altitude_mode.text = self._altitude_mode
        if all([self._north, self._south, self._east, self._west]):
            lat_lon_box = config.etree.SubElement(element, f"{self.ns}LatLonBox")
            north = config.etree.SubElement(lat_lon_box, f"{self.ns}north")
            north.text = self._north
            south = config.etree.SubElement(lat_lon_box, f"{self.ns}south")
            south.text = self._south
            east = config.etree.SubElement(lat_lon_box, f"{self.ns}east")
            east.text = self._east
            west = config.etree.SubElement(lat_lon_box, f"{self.ns}west")
            west.text = self._west
            if self._rotation:
                rotation = config.etree.SubElement(lat_lon_box, f"{self.ns}rotation")
                rotation.text = self._rotation
        return element

    def from_element(self, element: Element) -> None:
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

    def schemata(self) -> None:
        if self._schemata:
            yield from self._schemata

    def append_schema(self, schema: "Schema") -> None:
        if self._schemata is None:
            self._schemata = []
        if isinstance(schema, Schema):
            self._schemata.append(schema)
        else:
            s = Schema(schema)
            self._schemata.append(s)

    def from_element(self, element: Element) -> None:
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

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self._schemata is not None:
            for schema in self._schemata:
                element.append(schema.etree_element())
        return element

    def get_style_by_url(self, style_url: str) -> Union[Style, StyleMap]:
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

    def from_element(self, element: Element) -> None:
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

    def from_element(self, element: Element) -> None:
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
        logger.debug("Problem with element: %", config.etree.tostring(element))
        # raise ValueError('No geometries found')

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self._geometry is not None:
            element.append(self._geometry.etree_element())
        else:
            logger.error("Object does not have a geometry")
        return element


class KML:
    """represents a KML File"""

    _features = []
    ns = None

    def __init__(self, ns: Optional[str] = None) -> None:
        """The namespace (ns) may be empty ('') if the 'kml:' prefix is
        undesired. Note that all child elements like Document or Placemark need
        to be initialized with empty namespace as well in this case.

        """
        self._features = []

        self.ns = config.KMLNS if ns is None else ns

    def from_string(self, xml_string: str) -> None:
        """create a KML object from a xml string"""
        try:
            element = config.etree.fromstring(
                xml_string, parser=config.etree.XMLParser(huge_tree=True, recover=True)
            )
        except TypeError:
            element = config.etree.XML(xml_string)

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
        groundoverlays = element.findall(f"{ns}GroundOverlay")
        for groundoverlay in groundoverlays:
            feature = GroundOverlay(ns)
            feature.from_element(groundoverlay)
            self.append(feature)
        photo_overlays = element.findall(f"{ns}PhotoOverlay")
        for photo_overlay in photo_overlays:
            feature = PhotoOverlay(ns)
            feature.from_element(photo_overlay)
            self.append(feature)

    def etree_element(self) -> Element:
        # self.ns may be empty, which leads to unprefixed kml elements.
        # However, in this case the xlmns should still be mentioned on the kml
        # element, just without prefix.
        if not self.ns:
            root = config.etree.Element(f"{self.ns}kml")
            root.set("xmlns", config.KMLNS[1:-1])
        else:
            try:
                root = config.etree.Element(
                    f"{self.ns}kml", nsmap={None: self.ns[1:-1]}
                )
            except TypeError:
                root = config.etree.Element(f"{self.ns}kml")
        for feature in self.features():
            root.append(feature.etree_element())
        return root

    def to_string(self, prettyprint: bool = False) -> str:
        """Return the KML Object as serialized xml"""
        try:
            return config.etree.tostring(
                self.etree_element(),
                encoding="UTF-8",
                pretty_print=prettyprint,
            ).decode("UTF-8")
        except TypeError:
            return config.etree.tostring(self.etree_element(), encoding="UTF-8").decode(
                "UTF-8"
            )

    def features(self) -> Iterator[Union[Folder, Document, Placemark]]:
        """iterate over features"""
        for feature in self._features:
            if isinstance(feature, (Document, Folder, Placemark, _Overlay)):

                yield feature
            else:
                raise TypeError(
                    "Features must be instances of "
                    "(Document, Folder, Placemark, Overlay)"
                )

    def append(self, kmlobj: Union[Folder, Document, Placemark]) -> None:
        """append a feature"""

        if isinstance(kmlobj, (Document, Folder, Placemark, _Overlay)):
            self._features.append(kmlobj)
        else:
            raise TypeError(
                "Features must be instances of (Document, Folder, Placemark, Overlay)"
            )


__all__ = [
    "Document",
    "Folder",
    "Icon",
    "PhotoOverlay",
    "GroundOverlay",
    "KML",
    "Placemark",
]
