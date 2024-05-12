# Copyright (C) 2023  Christian Ledermann
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
Feature base, Placemark and NetworkLink.

These are the objects that can be added to a KML file.
"""

import logging
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from pygeoif.types import GeoCollectionType
from pygeoif.types import GeoType

from fastkml import atom
from fastkml import config
from fastkml import gx
from fastkml.base import _BaseObject
from fastkml.base import _XMLObject
from fastkml.data import ExtendedData
from fastkml.geometry import AnyGeometryType
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.geometry import create_kml_geometry
from fastkml.helpers import attribute_int_kwarg
from fastkml.helpers import bool_subelement
from fastkml.helpers import int_attribute
from fastkml.helpers import node_text
from fastkml.helpers import node_text_kwarg
from fastkml.helpers import subelement_bool_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.links import Link
from fastkml.mixins import TimeMixin
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
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


class Snippet(_XMLObject):
    """
    A short description of the feature.
    In Google Earth, this description is displayed in the Places panel
    under the name of the feature.
    If a Snippet is not supplied, the first two lines of the <description>
    are used.
    In Google Earth, if a Placemark contains both a description and a
    Snippet, the <Snippet> appears beneath the Placemark in the Places
    panel, and the <description> appears in the Placemark's description
    balloon.
    This tag does not support HTML markup.
    <Snippet> has a maxLines attribute, an integer that specifies the
    maximum number of lines to display.
    """

    _default_ns = config.KMLNS

    text: Optional[str]
    max_lines: Optional[int] = None

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        text: Optional[str] = None,
        max_lines: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.text = text
        self.max_lines = max_lines

    def __repr__(self) -> str:
        """Create a string (c)representation for Snippet."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"text={self.text!r}, "
            f"max_lines={self.max_lines!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.text)


registry.register(
    Snippet,
    RegistryItem(
        attr_name="text",
        node_name="",
        classes=(str,),
        get_kwarg=node_text_kwarg,
        set_element=node_text,
    ),
)
registry.register(
    Snippet,
    RegistryItem(
        attr_name="max_lines",
        node_name="maxLines",
        classes=(int,),
        get_kwarg=attribute_int_kwarg,
        set_element=int_attribute,
    ),
)


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

    atom_author: Optional[atom.Author]
    # KML 2.2 supports new elements for including data about the author
    # and related website in your KML file. This information is displayed
    # in geo search results, both in Earth browsers such as Google Earth,
    # and in other applications such as Google Maps.

    atom_link: Optional[atom.Link]
    # Specifies the URL of the website containing this KML or KMZ file.

    address: Optional[str]
    # A string value representing an unstructured address written as a
    # standard street, city, state address, and/or as a postal code.
    # You can use the <address> tag to specify the location of a point
    # instead of using latitude and longitude coordinates.

    phone_number: Optional[str]
    # A string value representing a telephone number.
    # This element is used by Google Maps Mobile only.

    snippet: Optional[Snippet]
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

    style_url: Optional[StyleUrl]
    # URL of a <Style> or <StyleMap> defined in a Document.
    # If the style is in the same file, use a # reference.
    # If the style is defined in an external file, use a full URL
    # along with # referencing.

    styles: List[Union[Style, StyleMap]]
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

    view: Union[Camera, LookAt, None]

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
    # (2 and 3) are already implemented, see data.py for more information.
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
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.name = name
        self.description = description
        self.style_url = style_url
        self.styles = list(styles) if styles else []
        self.view = view
        self.visibility = visibility
        self.isopen = isopen
        self.snippet = snippet
        self.atom_author = atom_author
        self.atom_link = atom_link
        self.address = address
        self.phone_number = phone_number
        self.region = region
        self.extended_data = extended_data
        self.times = times

    def __repr__(self) -> str:
        """Create a string (c)representation for _Feature."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"visibility={self.visibility!r}, "
            f"isopen={self.isopen!r}, "
            f"atom_link={self.atom_link!r}, "
            f"atom_author={self.atom_author!r}, "
            f"address={self.address!r}, "
            f"phone_number={self.phone_number!r}, "
            f"snippet={self.snippet!r}, "
            f"description={self.description!r}, "
            f"view={self.view!r}, "
            f"times={self.times!r}, "
            f"style_url={self.style_url!r}, "
            f"styles={self.styles!r}, "
            f"region={self.region!r}, "
            f"extended_data={self.extended_data!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )


registry.register(
    _Feature,
    RegistryItem(
        attr_name="name",
        node_name="name",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="visibility",
        node_name="visibility",
        classes=(bool,),
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="isopen",
        node_name="open",
        classes=(bool,),
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="atom_link",
        node_name="atom:link",
        classes=(atom.Link,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="atom_author",
        node_name="atom:author",
        classes=(atom.Author,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="address",
        node_name="address",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="phone_number",
        node_name="phoneNumber",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="snippet",
        node_name="Snippet",
        classes=(Snippet,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="description",
        node_name="description",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="view",
        node_name="Camera,LookAt",
        classes=(
            Camera,
            LookAt,
        ),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="times",
        node_name="TimeSpan,TimeStamp",
        classes=(
            TimeSpan,
            TimeStamp,
        ),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="style_url",
        node_name="styleUrl",
        classes=(StyleUrl,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="styles",
        node_name="Style,StyleMap",
        classes=(
            Style,
            StyleMap,
        ),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="region",
        node_name="region",
        classes=(Region,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    _Feature,
    RegistryItem(
        attr_name="extended_data",
        node_name="ExtendedData",
        classes=(ExtendedData,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


class Placemark(_Feature):
    """
    A Placemark is a Feature with associated Geometry.
    In Google Earth, a Placemark appears as a list item in the Places
    panel. A Placemark with a Point has an icon associated with it that
    marks a point on the Earth in the 3D viewer.
    """

    kml_geometry: Optional[KmlGeometry]

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
        kml_geometry: Optional[KmlGeometry] = None,
        geometry: Optional[Union[GeoType, GeoCollectionType]] = None,
        **kwargs: Any,
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
            **kwargs,
        )
        if kml_geometry and geometry:
            msg = "You can only specify one of kml_geometry or geometry"
            raise ValueError(msg)
        if geometry:
            kml_geometry = create_kml_geometry(  # type: ignore[assignment]
                geometry=geometry,
                ns=ns,
                name_spaces=name_spaces,
            )
        self.kml_geometry = kml_geometry

    def __repr__(self) -> str:
        """Create a string (c)representation for Placemark."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"visibility={self.visibility!r}, "
            f"isopen={self.isopen!r}, "
            f"atom_link={self.atom_link!r}, "
            f"atom_author={self.atom_author!r}, "
            f"address={self.address!r}, "
            f"phone_number={self.phone_number!r}, "
            f"snippet={self.snippet!r}, "
            f"description={self.description!r}, "
            f"view={self.view!r}, "
            f"times={self.times!r}, "
            f"style_url={self.style_url!r}, "
            f"styles={self.styles!r}, "
            f"region={self.region!r}, "
            f"extended_data={self.extended_data!r}, "
            f"kml_geometry={self.kml_geometry!r}, "
            f"geometry={self.geometry!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[AnyGeometryType]:
        return self.kml_geometry.geometry if self.kml_geometry is not None else None


registry.register(
    Placemark,
    RegistryItem(
        attr_name="kml_geometry",
        node_name=(
            "Point,LineString,LinearRing,Polygon,MultiGeometry,"
            "gx:MultiTrack,gx:Track"
        ),
        classes=(
            Point,
            LineString,
            LinearRing,
            Polygon,
            MultiGeometry,
            gx.MultiTrack,
            gx.Track,
        ),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


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
    link: Optional[Link]

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
        **kwargs: Any,
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
            **kwargs,
        )
        self.refresh_visibility = refresh_visibility
        self.fly_to_view = fly_to_view
        self.link = link

    def __repr__(self) -> str:
        """Create a string (c)representation for NetworkLink."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"visibility={self.visibility!r}, "
            f"isopen={self.isopen!r}, "
            f"atom_link={self.atom_link!r}, "
            f"atom_author={self.atom_author!r}, "
            f"address={self.address!r}, "
            f"phone_number={self.phone_number!r}, "
            f"snippet={self.snippet!r}, "
            f"description={self.description!r}, "
            f"view={self.view!r}, "
            f"times={self.times!r}, "
            f"style_url={self.style_url!r}, "
            f"styles={self.styles!r}, "
            f"region={self.region!r}, "
            f"extended_data={self.extended_data!r}, "
            f"refresh_visibility={self.refresh_visibility!r}, "
            f"fly_to_view={self.fly_to_view!r}, "
            f"link={self.link!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.link)


registry.register(
    NetworkLink,
    RegistryItem(
        attr_name="refresh_visibility",
        node_name="refreshVisibility",
        classes=(bool,),
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)
registry.register(
    NetworkLink,
    RegistryItem(
        attr_name="fly_to_view",
        node_name="flyToView",
        classes=(bool,),
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)
registry.register(
    NetworkLink,
    RegistryItem(
        attr_name="link",
        node_name="Link",
        classes=(Link,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
