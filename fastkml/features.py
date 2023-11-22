"""
Feature base, Placemark and NetworkLink.

These are the objects that can be added to a KML file.
"""

import logging
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

from fastkml import atom
from fastkml import config
from fastkml import gx
from fastkml.base import _BaseObject
from fastkml.data import ExtendedData
from fastkml.enums import Verbosity
from fastkml.geometry import AnyGeometryType
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.mixins import TimeMixin
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.styles import _StyleSelector
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.types import Element
from fastkml.views import Camera
from fastkml.views import LookAt
from fastkml.views import Region

logger = logging.getLogger(__name__)

KmlGeometry = Union[
    Point,
    LineString,
    LinearRing,
    Polygon,
    MultiGeometry,
    gx.MultiTrack,
    gx.Track,
]


class _Feature(TimeMixin, _BaseObject):
    """
    abstract element; do not create
    subclasses are:
        * Container (Document, Folder)
        * Placemark
        * Overlay
    Not Implemented Yet:
        * NetworkLink.
    """

    name: Optional[str]
    # User-defined text displayed in the 3D viewer as the label for the
    # object (for example, for a Placemark, Folder, or NetworkLink).

    visibility: Optional[bool]
    # Boolean value. Specifies whether the feature is drawn in the 3D
    # viewer when it is initially loaded. In order for a feature to be
    # visible, the <visibility> tag of all its ancestors must also be
    # set to 1.

    isopen: Optional[bool]
    # Boolean value. Specifies whether a Document or Folder appears
    # closed or open when first loaded into the Places panel.
    # 0=collapsed (the default), 1=expanded.

    _atom_author: Optional[atom.Author]
    # KML 2.2 supports new elements for including data about the author
    # and related website in your KML file. This information is displayed
    # in geo search results, both in Earth browsers such as Google Earth,
    # and in other applications such as Google Maps.

    _atom_link: Optional[atom.Link]
    # Specifies the URL of the website containing this KML or KMZ file.

    _address: Optional[str]
    # A string value representing an unstructured address written as a
    # standard street, city, state address, and/or as a postal code.
    # You can use the <address> tag to specify the location of a point
    # instead of using latitude and longitude coordinates.

    _phone_number: Optional[str]
    # A string value representing a telephone number.
    # This element is used by Google Maps Mobile only.

    _snippet: Optional[Union[str, Dict[str, Any]]]
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

    description: Optional[str]
    # User-supplied content that appears in the description balloon.

    _style_url: Optional[Union[Style, StyleMap]]
    # URL of a <Style> or <StyleMap> defined in a Document.
    # If the style is in the same file, use a # reference.
    # If the style is defined in an external file, use a full URL
    # along with # referencing.

    _styles: List[Union[Style, StyleMap]]
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

    _view: Union[Camera, LookAt, None]

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
    extended_data: Optional[ExtendedData]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Union[str, Dict[str, Any]]] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[str] = None,
        styles: Optional[List[Style]] = None,
        region: Optional[Region] = None,
        extended_data: None = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.name = name
        self.description = description
        self.style_url = style_url
        self._styles = []
        self._view = view
        self.visibility = visibility
        self.isopen = isopen
        self.snippet = snippet
        self._atom_author = atom_author
        self._atom_link = atom_link
        self.address = address
        self.phone_number = phone_number
        if styles:
            for style in styles:
                self.append_style(style)
        self.extended_data = extended_data
        self._times = times

    @property
    def style_url(self) -> Optional[str]:
        """
        Returns the url only, not a full StyleUrl object.
        if you need the full StyleUrl object use _style_url.
        """
        if isinstance(self._style_url, StyleUrl):
            return self._style_url.url
        return None

    @style_url.setter
    def style_url(self, styleurl: Union[str, StyleUrl, None]) -> None:
        """You may pass a StyleUrl Object, a string or None."""
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
    def view(self) -> Optional[Union[Camera, LookAt]]:
        return self._view

    @view.setter
    def view(self, camera: Optional[Union[Camera, LookAt]]) -> None:
        self._view = camera

    @property
    def link(self):
        return self._atom_link.href

    @link.setter
    def link(self, url) -> None:
        if isinstance(url, str):
            self._atom_link = atom.Link(href=url)
        elif isinstance(url, atom.Link):
            self._atom_link = url
        elif url is None:
            self._atom_link = None
        else:
            raise TypeError

    @property
    def author(self) -> None:
        if self._atom_author:
            return self._atom_author.name
        return None

    @author.setter
    def author(self, name) -> None:
        if isinstance(name, atom.Author):
            self._atom_author = name
        elif isinstance(name, str):
            if self._atom_author is None:
                self._atom_author = atom.Author(ns=config.ATOMNS, name=name)
            else:
                self._atom_author.name = name
        elif name is None:
            self._atom_author = None
        else:
            raise TypeError

    def append_style(self, style: Union[Style, StyleMap]) -> None:
        """Append a style to the feature."""
        if isinstance(style, _StyleSelector):
            self._styles.append(style)
        else:
            raise TypeError

    def styles(self) -> Iterator[Union[Style, StyleMap]]:
        """Iterate over the styles of this feature."""
        for style in self._styles:
            if isinstance(style, _StyleSelector):
                yield style
            else:
                raise TypeError

    @property
    def snippet(self) -> Optional[Dict[str, Any]]:
        if not self._snippet:
            return None
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
                return None
            return None
        elif isinstance(self._snippet, str):
            return self._snippet
        else:
            msg = "Snippet must be dict of {'text':t, 'maxLines':i} or string"
            raise ValueError(
                msg,
            )

    @snippet.setter
    def snippet(self, snip=None) -> None:
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
            msg = "Snippet must be dict of {'text':t, 'maxLines':i} or string"
            raise ValueError(
                msg,
            )

    @property
    def address(self) -> Optional[str]:
        return self._address

    @address.setter
    def address(self, address: Optional[str]) -> None:
        self._address = address

    @property
    def phone_number(self) -> Optional[str]:
        return self._phone_number

    @phone_number.setter
    def phone_number(self, phone_number: Optional[str]) -> None:
        self._phone_number = phone_number

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.name:
            name = config.etree.SubElement(element, f"{self.ns}name")
            name.text = self.name
        if self.description:
            description = config.etree.SubElement(element, f"{self.ns}description")
            description.text = self.description
        if self._view is not None:
            element.append(self._view.etree_element())
        if self.visibility is not None:
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
        elif self._times is not None:
            element.append(self._times.etree_element())
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

    def from_element(self, element: Element, strict: bool = False) -> None:
        super().from_element(element)
        name = element.find(f"{self.ns}name")
        if name is not None:
            self.name = name.text
        description = element.find(f"{self.ns}description")
        if description is not None:
            self.description = description.text
        visibility = element.find(f"{self.ns}visibility")
        if visibility is not None and visibility.text:
            self.visibility = 1 if visibility.text in ["1", "true"] else 0
        isopen = element.find(f"{self.ns}open")
        if isopen is not None:
            self.isopen = 1 if isopen.text in ["1", "true"] else 0
        styles = element.findall(f"{self.ns}Style")
        for style in styles:
            s = Style.class_from_element(
                ns=self.ns,
                name_spaces=self.name_spaces,
                element=style,
                strict=strict,
            )
            self.append_style(s)
        styles = element.findall(f"{self.ns}StyleMap")
        for style in styles:
            s = StyleMap.class_from_element(
                ns=self.ns,
                name_spaces=self.name_spaces,
                element=style,
                strict=strict,
            )
            self.append_style(s)
        style_url = element.find(f"{self.ns}styleUrl")
        if style_url is not None:
            self._style_url = StyleUrl.class_from_element(
                ns=self.ns,
                name_spaces=self.name_spaces,
                element=style_url,
                strict=strict,
            )
        snippet = element.find(f"{self.ns}Snippet")
        if snippet is not None:
            _snippet = {"text": snippet.text}
            if snippet.get("maxLines"):
                _snippet["maxLines"] = int(snippet.get("maxLines"))
            self.snippet = _snippet
        timespan = element.find(f"{self.ns}TimeSpan")
        if timespan is not None:
            self._timespan = TimeSpan.class_from_element(
                ns=self.ns,
                name_spaces=self.name_spaces,
                element=timespan,
                strict=strict,
            )
        timestamp = element.find(f"{self.ns}TimeStamp")
        if timestamp is not None:
            self._timestamp = TimeStamp.class_from_element(
                ns=self.ns,
                name_spaces=self.name_spaces,
                element=timestamp,
                strict=strict,
            )
        atom_link = element.find(f"{atom.NS}link")
        if atom_link is not None:
            self._atom_link = atom.Link.class_from_element(
                ns=atom.NS,
                name_spaces=self.name_spaces,
                element=atom_link,
                strict=strict,
            )
        atom_author = element.find(f"{atom.NS}author")
        if atom_author is not None:
            self._atom_author = atom.Author.class_from_element(
                ns=atom.NS,
                name_spaces=self.name_spaces,
                element=atom_author,
                strict=strict,
            )
        extended_data = element.find(f"{self.ns}ExtendedData")
        if extended_data is not None:
            self.extended_data = ExtendedData.class_from_element(
                ns=self.ns,
                element=extended_data,
                strict=strict,
            )
        address = element.find(f"{self.ns}address")
        if address is not None:
            self.address = address.text
        phone_number = element.find(f"{self.ns}phoneNumber")
        if phone_number is not None:
            self.phone_number = phone_number.text
        camera = element.find(f"{self.ns}Camera")
        if camera is not None:
            self._view = Camera.class_from_element(
                ns=self.ns,
                element=camera,
                strict=strict,
            )
        lookat = element.find(f"{self.ns}LookAt")
        if lookat is not None:
            self._view = LookAt.class_from_element(
                ns=self.ns,
                element=lookat,
                strict=strict,
            )


class Placemark(_Feature):
    """
    A Placemark is a Feature with associated Geometry.
    In Google Earth, a Placemark appears as a list item in the Places
    panel. A Placemark with a Point has an icon associated with it that
    marks a point on the Earth in the 3D viewer.
    """

    __name__ = "Placemark"
    _geometry = None

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        styles: Optional[List[Style]] = None,
        style_url: Optional[str] = None,
        extended_data: None = None,
        geometry: Optional[KmlGeometry] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            description=description,
            styles=styles,
            style_url=style_url,
            extended_data=extended_data,
        )
        self._geometry = geometry

    @property
    def geometry(self) -> Optional[AnyGeometryType]:
        if self._geometry is not None:
            return self._geometry.geometry
        return None

    def from_element(self, element: Element, strict=False) -> None:
        super().from_element(element)
        point = element.find(f"{self.ns}Point")
        if point is not None:
            self._geometry = Point.class_from_element(
                ns=self.ns,
                element=point,
                strict=strict,
            )
            return
        line = element.find(f"{self.ns}LineString")
        if line is not None:
            self._geometry = LineString.class_from_element(
                ns=self.ns,
                element=line,
                strict=strict,
            )
            return
        polygon = element.find(f"{self.ns}Polygon")
        if polygon is not None:
            self._geometry = Polygon.class_from_element(
                ns=self.ns,
                element=polygon,
                strict=strict,
            )
            return
        linearring = element.find(f"{self.ns}LinearRing")
        if linearring is not None:
            self._geometry = LinearRing.class_from_element(
                ns=self.ns,
                element=linearring,
                strict=strict,
            )
            return
        multigeometry = element.find(f"{self.ns}MultiGeometry")
        if multigeometry is not None:
            self._geometry = MultiGeometry.class_from_element(
                ns=self.ns,
                element=multigeometry,
                strict=strict,
            )
            return
        track = element.find(f"{self.ns}Track")
        if track is not None:
            self._geometry = gx.Track.class_from_element(
                ns=config.GXNS,
                element=track,
                strict=strict,
            )
            return
        multitrack = element.find(f"{self.ns}MultiTrack")
        if multitrack is not None:
            self._geometry = gx.MultiTrack.class_from_element(
                ns=config.GXNS,
                element=multitrack,
                strict=strict,
            )
            return
        logger.warning("No geometries found")
        logger.debug("Problem with element: %", config.etree.tostring(element))

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self._geometry is not None:
            element.append(self._geometry.etree_element())
        else:
            logger.error("Object does not have a geometry")
        return element


class NetworkLink(_Feature):
    __name__ = "NetworkLink"
    _nlink = None

    def __init__(
        self,
        ns=None,
        id=None,
        name=None,
        description=None,
        styles=None,
        styleUrl=None,
    ):
        super().__init__(ns, id, name, description, styles, styleUrl)

    @property
    def link(self):
        return self._nlink.href

    @link.setter
    def link(self, url):
        if isinstance(url, basestring):
            self._nlink = atom.Link(href=url)
        elif isinstance(url, Link):
            self._nlink = url
        elif url is None:
            self._nlink = None
        else:
            raise TypeError

    def etree_element(self):
        element = super().etree_element()
        if self._nlink is not None:
            element.append(self._nlink.etree_element())
        return element

    def from_element(self, element):
        super(_Feature, self).from_element(element)
        name = element.find(f"{self.ns}name")
        if name is not None:
            self.name = name.text
        id = element.find(f"{self.ns}id")
        if id is not None:
            self.id = id.text
        visibility = element.find(f"{self.ns}visibility")
        if visibility is not None:
            self.visibility = visibility.text

        link = element.find(f"{self.ns}Link")
        if link is not None:
            s = Link()
            s.from_element(link)
            self._nlink = s
