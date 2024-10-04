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
"""Container classes for KML elements."""
import logging
import urllib.parse as urlparse
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from fastkml import atom
from fastkml import gx
from fastkml.data import ExtendedData
from fastkml.data import Schema
from fastkml.features import Placemark
from fastkml.features import Snippet
from fastkml.features import _Feature
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
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


class _Container(_Feature):
    """
    A Container element that holds one or more Features.

    Supports the creation of nested hierarchies.
    subclasses are:
    Document,
    Folder.
    """

    features: List[_Feature]

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
        # Container specific
        features: Optional[Iterable[_Feature]] = None,
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
        self.features = list(features) if features else []

    def __repr__(self) -> str:
        """Create a string (c)representation for _Container."""
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
            f"features={self.features!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def append(self, kmlobj: _Feature) -> None:
        """Append a feature."""
        if kmlobj is self:
            msg = "Cannot append self"
            raise ValueError(msg)
        assert self.features is not None  # noqa: S101
        self.features.append(kmlobj)


class Folder(_Container):
    """
    A Folder is used to arrange other Features hierarchically.

    It may contain Folders, Placemarks, NetworkLinks, or Overlays.
    """


class Document(_Container):
    """
    A Document is a container for features and styles.

    This element is required if your KML file uses shared styles or schemata for typed
    extended data.
    """

    schemata: List[Schema]

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
        features: Optional[List[_Feature]] = None,
        schemata: Optional[Iterable[Schema]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the class.

        Args:
        ----
            ns (Optional[str]): The namespace.
            name_spaces (Optional[Dict[str, str]]):
                The dictionary of namespace prefixes and URIs.
            id (Optional[str]): The ID of the container.
            target_id (Optional[str]): The target ID.
            name (Optional[str]): The name of the container.
            visibility (Optional[bool]): The visibility flag.
            isopen (Optional[bool]): The isopen flag.
            atom_link (Optional[atom.Link]): The Atom link.
            atom_author (Optional[atom.Author]): The Atom author.
            address (Optional[str]): The address.
            phone_number (Optional[str]): The phone number.
            snippet (Optional[Snippet]): The snippet.
            description (Optional[str]): The description.
            view (Optional[Union[Camera, LookAt]]): The view.
            times (Optional[Union[TimeSpan, TimeStamp]]): The times.
            style_url (Optional[StyleUrl]): The style URL.
            styles (Optional[Iterable[Union[Style, StyleMap]]]): The styles.
            region (Optional[Region]): The region.
            extended_data (Optional[ExtendedData]): The extended data.
            features (Optional[List[_Feature]]): The list of features.
            schemata (Optional[Iterable[Schema]]): The schemata.
            **kwargs (Any): Additional keyword arguments.

        Returns:
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
            features=features,
            **kwargs,
        )
        self.schemata = list(schemata) if schemata else []

    def __repr__(self) -> str:
        """Create a string (c)representation for Document."""
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
            f"features={self.features!r}, "
            f"schemata={self.schemata!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def get_style_by_url(self, style_url: str) -> Optional[Union[Style, StyleMap]]:
        """
        Get a style by URL.

        Parameters
        ----------
        style_url : str
            The URL of the style.

        Returns
        -------
        Optional[Union[Style, StyleMap]]
            The style object if found, otherwise None.

        """
        id_ = urlparse.urlparse(style_url).fragment
        return next((style for style in self.styles if style.id == id_), None)


registry.register(
    _Container,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="features",
        node_name="Folder,Placemark,Document",
        classes=(Folder, Placemark, Document),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)
registry.register(
    Document,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="schemata",
        node_name="Schema",
        classes=(Schema,),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)
