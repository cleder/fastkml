"""
Feature base, Placemark and NetworkLink.

These are the objects that can be added to a KML file.
"""

import logging
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Iterable
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
from fastkml.links import Link
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


@dataclass(frozen=True)
class Snippet:
    text: str
    max_lines: Optional[int] = None


class _Feature(TimeMixin, _BaseObject):
    """
    abstract element; do not create
    subclasses are:
        * Container (Document, Folder)
        * Placemark
        * Overlay
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

    _snippet: Optional[Snippet]
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

    _style_url: Optional[StyleUrl]
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

    region: Optional[Region]
    # Features and geometry associated with a Region are drawn only when
    # the Region is active.

    extended_data: Optional[ExtendedData]
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
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.name = name
        self.description = description
        self._style_url = style_url
        self._styles = list(styles) if styles else []
        self._view = view
        self.visibility = visibility
        self.isopen = isopen
        self.snippet = snippet
        self._atom_author = atom_author
        self._atom_link = atom_link
        self.address = address
        self.phone_number = phone_number
        self.region = region
        self.extended_data = extended_data
        self._times = times

    @property
    def style_url(self) -> Optional[str]:
        """
        Returns the url only, not a full StyleUrl object.
        if you need the full StyleUrl object use _style_url.
        """
        return self._style_url.url if isinstance(self._style_url, StyleUrl) else None

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
    def link(self) -> Optional[atom.Link]:
        return self._atom_link

    @link.setter
    def link(self, link: Optional[atom.Link]) -> None:
        self._atom_link = link

    @property
    def author(self) -> Optional[atom.Author]:
        return self._atom_author

    @author.setter
    def author(self, author: Optional[atom.Author]) -> None:
        self._atom_author = author

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
    def snippet(self) -> Optional[Snippet]:
        return self._snippet

    @snippet.setter
    def snippet(self, snippet: Optional[Snippet]) -> None:
        self._snippet = snippet

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
            name = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}name",
            )
            name.text = self.name
        if self.description:
            description = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}description",
            )
            description.text = self.description
        if self._view is not None:
            element.append(self._view.etree_element())
        if self.visibility is not None:
            visibility = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}visibility",
            )
            visibility.text = str(int(self.visibility))
        if self.isopen:
            isopen = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}open",
            )
            isopen.text = str(int(self.isopen))
        if self._style_url is not None:
            element.append(self._style_url.etree_element())
        for style in self.styles():
            element.append(style.etree_element())
        if self.snippet:
            snippet = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}Snippet",
            )
            snippet.text = self.snippet.text
            if self.snippet.max_lines:
                snippet.set("maxLines", str(self.snippet.max_lines))
        elif self._times is not None:
            element.append(self._times.etree_element())
        if self._atom_link is not None:
            element.append(self._atom_link.etree_element())
        if self._atom_author is not None:
            element.append(self._atom_author.etree_element())
        if self.extended_data is not None:
            element.append(self.extended_data.etree_element())
        if self._address is not None:
            address = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}address",
            )
            address.text = self._address
        if self._phone_number is not None:
            phone_number = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}phoneNumber",
            )
            phone_number.text = self._phone_number
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        name = element.find(f"{ns}name")
        if name is not None:
            kwargs["name"] = name.text
        description = element.find(f"{ns}description")
        if description is not None:
            kwargs["description"] = description.text
        visibility = element.find(f"{ns}visibility")
        if visibility is not None and visibility.text:
            kwargs["visibility"] = visibility.text in ["1", "true"]
        isopen = element.find(f"{ns}open")
        if isopen is not None:
            kwargs["isopen"] = isopen.text in ["1", "true"]
        style_url = element.find(f"{ns}styleUrl")
        if style_url is not None:
            kwargs["style_url"] = StyleUrl.class_from_element(
                ns=ns,
                name_spaces=name_spaces,
                element=style_url,
                strict=strict,
            )
        styles = element.findall(f"{ns}Style")
        kwargs["styles"] = []
        if styles is not None:
            for style in styles:
                kwargs["styles"].append(
                    Style.class_from_element(
                        ns=ns,
                        name_spaces=name_spaces,
                        element=style,
                        strict=strict,
                    ),
                )
        stylemaps = element.findall(f"{ns}StyleMap")
        if stylemaps is not None:
            for stylemap in stylemaps:
                kwargs["styles"].append(
                    StyleMap.class_from_element(
                        ns=ns,
                        name_spaces=name_spaces,
                        element=stylemap,
                        strict=strict,
                    ),
                )
        snippet = element.find(f"{ns}Snippet")
        if snippet is not None:
            max_lines = snippet.get("maxLines")
            if max_lines is not None:
                kwargs["snippet"] = Snippet(text=snippet.text, max_lines=int(max_lines))
            else:
                kwargs["snippet"] = Snippet(  # type: ignore[unreachable]
                    text=snippet.text,
                )
        timespan = element.find(f"{ns}TimeSpan")
        if timespan is not None:
            kwargs["times"] = TimeSpan.class_from_element(
                ns=ns,
                name_spaces=name_spaces,
                element=timespan,
                strict=strict,
            )
        timestamp = element.find(f"{ns}TimeStamp")
        if timestamp is not None:
            kwargs["times"] = TimeStamp.class_from_element(
                ns=ns,
                name_spaces=name_spaces,
                element=timestamp,
                strict=strict,
            )
        atom_link = element.find(f"{atom.NS}link")
        if atom_link is not None:
            kwargs["atom_link"] = atom.Link.class_from_element(
                ns=atom.NS,
                name_spaces=name_spaces,
                element=atom_link,
                strict=strict,
            )
        atom_author = element.find(f"{atom.NS}author")
        if atom_author is not None:
            kwargs["atom_author"] = atom.Author.class_from_element(
                ns=atom.NS,
                name_spaces=name_spaces,
                element=atom_author,
                strict=strict,
            )
        extended_data = element.find(f"{ns}ExtendedData")
        if extended_data is not None:
            kwargs["extended_data"] = ExtendedData.class_from_element(
                ns=ns,
                element=extended_data,
                strict=strict,
            )
        address = element.find(f"{ns}address")
        if address is not None:
            kwargs["address"] = address.text
        phone_number = element.find(f"{ns}phoneNumber")
        if phone_number is not None:
            kwargs["phone_number"] = phone_number.text
        camera = element.find(f"{ns}Camera")
        if camera is not None:
            kwargs["view"] = Camera.class_from_element(
                ns=ns,
                element=camera,
                strict=strict,
            )
        lookat = element.find(f"{ns}LookAt")
        if lookat is not None:
            kwargs["view"] = LookAt.class_from_element(
                ns=ns,
                element=lookat,
                strict=strict,
            )
        return kwargs


class Placemark(_Feature):
    """
    A Placemark is a Feature with associated Geometry.
    In Google Earth, a Placemark appears as a list item in the Places
    panel. A Placemark with a Point has an icon associated with it that
    marks a point on the Earth in the 3D viewer.
    """

    __name__ = "Placemark"
    _geometry: Optional[KmlGeometry]

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
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        # Placemark specific
        geometry: Optional[KmlGeometry] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
        )
        self._geometry = geometry

    @property
    def geometry(self) -> Optional[AnyGeometryType]:
        return self._geometry.geometry if self._geometry is not None else None

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

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        point = element.find(f"{ns}Point")
        if point is not None:
            kwargs["geometry"] = Point.class_from_element(
                ns=ns,
                element=point,
                strict=strict,
            )
            return kwargs
        line = element.find(f"{ns}LineString")
        if line is not None:
            kwargs["geometry"] = LineString.class_from_element(
                ns=ns,
                element=line,
                strict=strict,
            )
            return kwargs
        polygon = element.find(f"{ns}Polygon")
        if polygon is not None:
            kwargs["geometry"] = Polygon.class_from_element(
                ns=ns,
                element=polygon,
                strict=strict,
            )
            return kwargs
        linearring = element.find(f"{ns}LinearRing")
        if linearring is not None:
            kwargs["geometry"] = LinearRing.class_from_element(
                ns=ns,
                element=linearring,
                strict=strict,
            )
            return kwargs
        multigeometry = element.find(f"{ns}MultiGeometry")
        if multigeometry is not None:
            kwargs["geometry"] = MultiGeometry.class_from_element(
                ns=ns,
                element=multigeometry,
                strict=strict,
            )
            return kwargs
        track = element.find(f"{ns}Track")
        if track is not None:
            kwargs["geometry"] = gx.Track.class_from_element(
                ns=config.GXNS,
                element=track,
                strict=strict,
            )
            return kwargs
        multitrack = element.find(f"{ns}MultiTrack")
        if multitrack is not None:
            kwargs["geometry"] = gx.MultiTrack.class_from_element(
                ns=config.GXNS,
                element=multitrack,
                strict=strict,
            )
            return kwargs
        logger.warning("No geometries found")
        logger.debug(
            "Problem with element: %",
            config.etree.tostring(element),  # type: ignore[attr-defined]
        )
        return kwargs


class NetworkLink(_Feature):
    """
    References a KML file or KMZ archive on a local or remote network.

    Use the <Link> element to specify the location of the KML file.
    Within that element, you can define the refresh options for updating the file,
    based on time and camera change.
    NetworkLinks can be used in combination with Regions to handle very large datasets
    efficiently.
    https://developers.google.com/kml/documentation/kmlreference#networklink


    Elements Specific to NetworkLink
    <refreshVisibility>
    Boolean value.
    A value of 0 leaves the visibility of features within the control of the
    Google Earth user.
    Set the value to 1 to reset the visibility of features each time the NetworkLink is
    refreshed.
    For example, suppose a Placemark within the linked KML file has <visibility>
    set to 1 and the NetworkLink has <refreshVisibility> set to 1.
    When the file is first loaded into Google Earth, the user can clear the check box
    next to the item to turn off display in the 3D viewer.
    However, when the NetworkLink is refreshed, the Placemark will be made
    visible again, since its original visibility state was TRUE.
    <flyToView>
    Boolean value.
    A value of 1 causes Google Earth to fly to the view of the LookAt or Camera in the
    NetworkLinkControl (if it exists).
    If the NetworkLinkControl does not contain an AbstractView element,
    Google Earth flies to the LookAt or Camera element in the Feature child
    within the <kml> element in the refreshed file.
    If the <kml> element does not have a LookAt or Camera specified,
    the view is unchanged.
    For example, Google Earth would fly to the <LookAt> view of the parent Document,
    not the <LookAt> of the Placemarks contained within the Document.
    <Link>(required)
       https://developers.google.com/kml/documentation/kmlreference#link
    """

    refresh_visibility: Optional[bool]
    fly_to_view: Optional[bool]
    _link: Optional[Link]

    __name__ = "NetworkLink"

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
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        # NetworkLink specific
        refresh_visibility: Optional[bool] = None,
        fly_to_view: Optional[bool] = None,
        link: Optional[Link] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
        )
        self.refresh_visibility = refresh_visibility
        self.fly_to_view = fly_to_view
        self._link = link

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.refresh_visibility is not None:
            refresh_visibility = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}refreshVisibility",
            )
            refresh_visibility.text = str(int(self.refresh_visibility))

        if self.fly_to_view is not None:
            fly_to_view = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}flyToView",
            )
            fly_to_view.text = str(int(self.fly_to_view))
        if self.link is not None:
            element.append(self.link.etree_element())
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        visibility = element.find(f"{ns}refreshVisibility")
        if visibility is not None:
            kwargs["refresh_visibility"] = bool(int(visibility.text))
        flyto = element.find(f"{ns}flyToView")
        if flyto is not None:
            kwargs["fly_to_view"] = bool(int(flyto.text))
        link = element.find(f"{ns}Link")
        if link is not None:
            kwargs["link"] = Link.class_from_element(
                ns=ns,
                name_spaces=name_spaces,
                element=link,
                strict=strict,
            )
        return kwargs
