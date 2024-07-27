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
from fastkml import gx
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
from fastkml.kml_base import _BaseObject
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
        """
        Initialize a Feature object.

        Args:
        ----
            ns : str, optional
                The namespace for the feature.
            name_spaces : dict[str, str], optional
                A dictionary of namespace prefixes and URIs.
            text : str, optional
                The text content of the feature.
            max_lines : int, optional
                The maximum number of lines for the feature.
            **kwargs : Any
                Additional keyword arguments.

        Returns:
        -------
        None

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.text = text
        self.max_lines = max_lines

    def __repr__(self) -> str:
        """
        Create a string representation for Snippet.

        Returns
        -------
            str: The string representation of the Snippet object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"text={self.text!r}, "
            f"max_lines={self.max_lines!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the feature has text.

        Returns
        -------
        bool
            True if the feature has text, False otherwise.

        """
        return bool(self.text)


registry.register(
    Snippet,
    RegistryItem(
        ns_ids=("kml",),
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
        ns_ids=("", "kml"),
        attr_name="max_lines",
        node_name="maxLines",
        classes=(int,),
        get_kwarg=attribute_int_kwarg,
        set_element=int_attribute,
    ),
)


class _Feature(TimeMixin, _BaseObject):
    """
    Abstract base class representing a feature in KML.

    Direct known subclasses:
        - Container (Document, Folder)
        - Placemark
        - Overlay
        - NetworkLink
        - NetworkLink.
    """

    name: Optional[str]
    visibility: Optional[bool]
    isopen: Optional[bool]
    atom_author: Optional[atom.Author]
    atom_link: Optional[atom.Link]
    address: Optional[str]
    phone_number: Optional[str]
    snippet: Optional[Snippet]
    description: Optional[str]
    style_url: Optional[StyleUrl]
    styles: List[Union[Style, StyleMap]]
    view: Union[Camera, LookAt, None]
    region: Optional[Region]
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
        """
        Initialize the _Feature object.

        Args:
        ----
            ns (Optional[str]): Namespace for the element.
            name_spaces (Optional[Dict[str, str]]):
                Dictionary of namespace prefixes and URIs.
            id (Optional[str]): ID of the element.
            target_id (Optional[str]): ID of the target element.
            name (Optional[str]): User-defined text displayed in the 3D viewer as the
                label for the object.
            visibility (Optional[bool]): Specifies whether the feature is drawn in the
                3D viewer when it is initially loaded.
            isopen (Optional[bool]): Specifies whether a Document or Folder appears
                closed or open when first loaded into the Places panel.
            atom_link (Optional[atom.Link]): URL of the website containing this KML or
                KMZ file.
            atom_author (Optional[atom.Author]): Information about the author and
                related website in the KML file.
            address (Optional[str]): Unstructured address written as a standard street,
                city, state address, and/or as a postal code.
            phone_number (Optional[str]): Telephone number associated with the feature.
            snippet (Optional[Snippet]): Short description of the feature.
            description (Optional[str]): User-supplied content that appears in the
                description balloon.
            view (Optional[Union[Camera, LookAt]]): Camera or LookAt view associated.
            times (Optional[Union[TimeSpan, TimeStamp]]): Time information associated.
            style_url (Optional[StyleUrl]): URL of a Style or StyleMap.
            styles (Optional[Iterable[Union[Style, StyleMap]]]): Styles and StyleMaps
                defined to customize the appearance of the feature.
            region (Optional[Region]): Region associated with the feature.
            extended_data (Optional[ExtendedData]): Custom data added to the KML file.
            **kwargs (Any): Additional keyword arguments.

        """
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
        """
        Return a string representation of the _Feature object.

        Returns
        -------
            str: String representation of the _Feature object.

        """
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
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    _Feature,
    RegistryItem(
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("atom",),
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
        ns_ids=("atom",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        """
        Initialize a Feature object.

        Parameters
        ----------
        ns : str, optional
            The namespace for the feature.
        name_spaces : dict[str, str], optional
            The dictionary of namespace prefixes and URIs.
        id : str, optional
            The ID of the feature.
        target_id : str, optional
            The target ID of the feature.
        name : str, optional
            The name of the feature.
        visibility : bool, optional
            The visibility of the feature.
        isopen : bool, optional
            The open status of the feature.
        atom_link : atom.Link, optional
            The Atom link associated with the feature.
        atom_author : atom.Author, optional
            The Atom author associated with the feature.
        address : str, optional
            The address of the feature.
        phone_number : str, optional
            The phone number of the feature.
        snippet : Snippet, optional
            The snippet of the feature.
        description : str, optional
            The description of the feature.
        view : Union[Camera, LookAt], optional
            The view associated with the feature.
        times : Union[TimeSpan, TimeStamp], optional
            The times associated with the feature.
        style_url : StyleUrl, optional
            The style URL of the feature.
        styles : Iterable[Union[Style, StyleMap]], optional
            The styles associated with the feature.
        region : Region, optional
            The region associated with the feature.
        extended_data : ExtendedData, optional
            The extended data associated with the feature.
        kml_geometry : KmlGeometry, optional
            The KML geometry associated with the feature.
        geometry : Union[GeoType, GeoCollectionType], optional
            The geometry associated with the feature.
        **kwargs : Any
            Additional keyword arguments.

        Raises
        ------
        ValueError
            If both `kml_geometry` and `geometry` are specified.

        """
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
        """
        Return a string representation of the Placemark object.

        Returns
        -------
            str: A string representation of the Placemark object.

        """
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
            f"**{self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[AnyGeometryType]:
        """
        Returns the geometry associated with this feature.

        Returns
        -------
            Optional[AnyGeometryType]: The geometry associated with this feature,
            or None if no geometry is present.

        """
        return self.kml_geometry.geometry if self.kml_geometry is not None else None


registry.register(
    Placemark,
    RegistryItem(
        ns_ids=("kml",),
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
        """
        Initialize a Feature object.

        Parameters
        ----------
        ns : str, optional
            The namespace for the feature.
        name_spaces : dict[str, str], optional
            The dictionary of namespace prefixes and URIs.
        id : str, optional
            The ID of the feature.
        target_id : str, optional
            The target ID of the feature.
        name : str, optional
            The name of the feature.
        visibility : bool, optional
            The visibility of the feature.
        isopen : bool, optional
            Whether the feature is open.
        atom_link : atom.Link, optional
            The Atom link associated with the feature.
        atom_author : atom.Author, optional
            The Atom author associated with the feature.
        address : str, optional
            The address of the feature.
        phone_number : str, optional
            The phone number of the feature.
        snippet : Snippet, optional
            The snippet associated with the feature.
        description : str, optional
            The description of the feature.
        view : Union[Camera, LookAt], optional
            The view associated with the feature.
        times : Union[TimeSpan, TimeStamp], optional
            The times associated with the feature.
        style_url : StyleUrl, optional
            The style URL of the feature.
        styles : Iterable[Union[Style, StyleMap]], optional
            The styles associated with the feature.
        region : Region, optional
            The region associated with the feature.
        extended_data : ExtendedData, optional
            The extended data associated with the feature.
        refresh_visibility : bool, optional
            The refresh visibility of the feature (NetworkLink specific).
        fly_to_view : bool, optional
            Whether to fly to the view (NetworkLink specific).
        link : Link, optional
            The link associated with the feature.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        None

        """
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
        """
        Return a string representation of the NetworkLink object.

        Returns
        -------
            str: A string representation of the NetworkLink object.

        """
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
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the feature has a link.

        Returns
        -------
        bool
            True if the feature has a link, False otherwise.

        """
        return bool(self.link)


registry.register(
    NetworkLink,
    RegistryItem(
        ns_ids=("kml",),
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
        ns_ids=("kml",),
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
        ns_ids=("kml",),
        attr_name="link",
        node_name="Link",
        classes=(Link,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
