# Copyright (C) 2024 Christian Ledermann
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
NetworkLinkControl class.

Controls the behavior of files fetched by a <NetworkLink>.

https://developers.google.com/kml/documentation/kmlreference#networklinkcontrol
"""

import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import TypeVar

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.helpers import clean_string
from fastkml.helpers import datetime_subelement
from fastkml.helpers import datetime_subelement_kwarg
from fastkml.helpers import float_subelement
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.times import KmlDateTime
from fastkml.views import Camera
from fastkml.views import LookAt

if TYPE_CHECKING:
    from fastkml.containers import Document
    from fastkml.containers import Folder
    from fastkml.data import Data
    from fastkml.data import SchemaData
    from fastkml.features import NetworkLink
    from fastkml.features import Placemark
    from fastkml.geometry import LinearRing
    from fastkml.geometry import LineString
    from fastkml.geometry import MultiGeometry
    from fastkml.geometry import Point
    from fastkml.geometry import Polygon
    from fastkml.gx.data import SimpleArrayData
    from fastkml.gx.track import MultiTrack
    from fastkml.gx.track import Track
    from fastkml.links import Link
    from fastkml.model import Alias
    from fastkml.model import Location
    from fastkml.model import Model
    from fastkml.model import Orientation
    from fastkml.model import ResourceMap
    from fastkml.model import Scale
    from fastkml.overlays import GroundOverlay
    from fastkml.overlays import ImagePyramid
    from fastkml.overlays import LatLonBox
    from fastkml.overlays import PhotoOverlay
    from fastkml.overlays import ScreenOverlay
    from fastkml.overlays import ViewVolume
    from fastkml.styles import BalloonStyle
    from fastkml.styles import IconStyle
    from fastkml.styles import LabelStyle
    from fastkml.styles import LineStyle
    from fastkml.styles import Pair
    from fastkml.styles import PolyStyle
    from fastkml.styles import Style
    from fastkml.styles import StyleMap
    from fastkml.times import TimeSpan
    from fastkml.times import TimeStamp
    from fastkml.views import LatLonAltBox
    from fastkml.views import Lod
    from fastkml.views import Region

    # Type aliases for the objects allowed in each Update action element.
    # These narrow the generic type parameter T of _UpdateAction for type checkers.
    _CreateObjects = Document | Folder
    _DeleteObjects = (
        Document
        | Folder
        | GroundOverlay
        | NetworkLink
        | PhotoOverlay
        | Placemark
        | ScreenOverlay
    )
    _ChangeObjects = (
        # Features
        Document
        | Folder
        | GroundOverlay
        | NetworkLink
        | PhotoOverlay
        | Placemark
        | ScreenOverlay
        # Overlay sub-elements
        | ImagePyramid
        | LatLonBox
        | ViewVolume
        # Views
        | Camera
        | LatLonAltBox
        | Lod
        | LookAt
        | Region
        # Styles
        | BalloonStyle
        | IconStyle
        | LabelStyle
        | LineStyle
        | Pair
        | PolyStyle
        | Style
        | StyleMap
        # Times
        | TimeSpan
        | TimeStamp
        # Geometry
        | LinearRing
        | LineString
        | MultiGeometry
        | Point
        | Polygon
        # GX Geometry
        | MultiTrack
        | Track
        # Model
        | Alias
        | Location
        | Model
        | Orientation
        | ResourceMap
        | Scale
        # Links
        | Link
        # Data
        | Data
        | SchemaData
        # GX Data
        | SimpleArrayData
    )
else:
    _CreateObjects = _XMLObject
    _DeleteObjects = _XMLObject
    _ChangeObjects = _XMLObject

__all__ = [
    "Change",
    "Create",
    "Delete",
    "NetworkLinkControl",
    "Update",
]

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=_XMLObject)


class _UpdateAction(_XMLObject, Generic[T]):
    """
    Base class for Update action elements (Create, Delete, Change).

    These elements contain KML objects that are the subject of the update action.
    """

    _default_nsid = config.KML

    objects: list[T]

    def __init__(
        self,
        ns: str | None = None,
        name_spaces: dict[str, str] | None = None,
        objects: Iterable[T] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize an Update action element.

        Parameters
        ----------
        ns : str, optional
            The namespace to use for the element.
        name_spaces : dict, optional
            A dictionary of namespaces to use for the element.
        objects : Iterable[T], optional
            The KML objects that are subject to this update action.
        **kwargs : Any, optional
            Additional keyword arguments.

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )
        if objects is not None and not isinstance(objects, Iterable):
            msg = f"objects must be an iterable, got {type(objects).__name__}"  # type: ignore[unreachable]
            raise TypeError(msg)
        self.objects = list(objects) if objects else []

    def __repr__(self) -> str:
        """
        Return a string representation of the Update action element.

        Returns
        -------
            str: A string representation of the Update action element.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"objects={self.objects!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the update action contains objects.

        Returns
        -------
        bool
            True if the update action contains objects, False otherwise.

        """
        return bool(self.objects)


class Create(_UpdateAction[_CreateObjects]):
    """
    Adds new elements to a Folder or Document already loaded via a NetworkLink.

    The ``<targetHref>`` element in ``<Update>`` specifies the URL of the .kml or .kmz
    file that contained the original Folder or Document. Within that file, the Folder
    or Document that is to contain the new data must already have an explicit ``id``
    defined for it. This ``id`` is referenced as the ``targetId`` attribute of the
    Folder or Document within ``<Create>`` that contains the element to be added.

    Once an object has been created and loaded into Google Earth, it takes on the URL
    of the original parent Document or Folder. To perform subsequent updates to objects
    added with this Update/Create mechanism, set ``<targetHref>`` to the URL of the
    original Document or Folder (not the URL of the file that loaded the intervening
    updates).

    Example:
    -------
    This example creates a new Placemark in a previously created Document that has
    an ``id`` of "region24". Note that subsequent updates to "placemark891" will still
    use the original targetHref::

        <Update>
          <targetHref>http://myserver.com/Point.kml</targetHref>
          <Create>
            <Document targetId="region24">
              <Placemark id="placemark891">
                <Point>
                  <coordinates>-95.48,40.43,0</coordinates>
                </Point>
              </Placemark>
            </Document>
          </Create>
        </Update>

    https://developers.google.com/kml/documentation/kmlreference#create

    """


class Delete(_UpdateAction[_DeleteObjects]):
    """
    Deletes features from a complex element already loaded via a NetworkLink.

    The ``<targetHref>`` element in ``<Update>`` specifies the .kml or .kmz file
    containing the data to be deleted. Within that file, the element to be deleted
    must already have an explicit ``id`` defined for it. The ``<Delete>`` element
    references this ``id`` in the ``targetId`` attribute.

    Child elements for ``<Delete>``, which are the only elements that can be deleted,
    are ``Document``, ``Folder``, ``GroundOverlay``, ``Placemark``, and
    ``ScreenOverlay``.

    Example:
    -------
    This example deletes a Placemark previously loaded into Google Earth::

        <Update>
          <targetHref>http://www.foo.com/Point.kml</targetHref>
          <Delete>
            <Placemark targetId="pa3556"/>
          </Delete>
        </Update>

    https://developers.google.com/kml/documentation/kmlreference#delete

    """


class Change(_UpdateAction[_ChangeObjects]):
    """
    Modifies the values in an element already loaded with a NetworkLink.

    Within the ``<Change>`` element, the child to be modified must include a
    ``targetId`` attribute that references the original element's ``id``.

    This update can be considered a "sparse update": in the modified element, only
    the values listed in ``<Change>`` are replaced; all other values remain untouched.
    When ``<Change>`` is applied to a set of coordinates, the new coordinates replace
    the current coordinates.

    Children of this element are the element(s) to be modified, which are identified
    by the ``targetId`` attribute.

    Example:
    -------
    This example changes the coordinates of a Point with id "point123"::

        <NetworkLinkControl>
          <Update>
            <targetHref>http://www/~sam/January14Data/Point.kml</targetHref>
            <Change>
              <Point targetId="point123">
                <coordinates>-95.48,40.43,0</coordinates>
              </Point>
            </Change>
          </Update>
        </NetworkLinkControl>

    https://developers.google.com/kml/documentation/kmlreference#change

    """


class Update(_XMLObject):
    """
    Specifies an addition, change, or deletion to KML data already loaded.

    The ``<targetHref>`` specifies the .kml or .kmz file whose data (within Google
    Earth) is to be modified. ``<Update>`` is always contained in a
    ``NetworkLinkControl``. Furthermore, the file containing the ``NetworkLinkControl``
    must have been loaded by a ``NetworkLink``.

    ``Update`` can contain any number of ``<Change>``, ``<Create>``, and ``<Delete>``
    elements, which will be processed in order.

    How Updates Work
    ----------------
    1. A ``NetworkLink`` loads the "original" KML file into Google Earth. An element
       that will later be updated needs to have an explicit ``id`` defined when it
       is first specified. The ``id``s must be unique within a given file.

    2. Another ``NetworkLink`` loads a second KML file containing the updates (any
       combination of Change, Create, and Delete) to the KML object(s) that have
       already been loaded.

    3. The update file contains two references to identify the original KML data:

       - To locate the objects within Google Earth, the ``Update`` element uses the
         ``targetHref`` element to identify the original file that defined the
         object(s) to be modified.
       - To identify the object(s) to be modified or the container for new objects,
         the ``Change``, ``Create``, and ``Delete`` elements contain a ``targetId``
         attribute that references the ``id``s of those objects.

    Syntax
    ------
    ::

        <Update>
          <targetHref>...</targetHref>    <!-- required, URL -->
          <Change>...</Change>
          <Create>...</Create>
          <Delete>...</Delete>
        </Update>

    Example:
    -------
    A complete example showing how to change a Placemark's name::

        <NetworkLinkControl>
          <Update>
            <targetHref>http://developers.google.com/kml/documentation/Point.kml
            </targetHref>
            <Change>
              <Placemark targetId="pm123">
                <name>Name changed by Update Change</name>
              </Placemark>
            </Change>
          </Update>
        </NetworkLinkControl>

    https://developers.google.com/kml/documentation/kmlreference#update
    https://developers.google.com/kml/documentation/updates

    """

    _default_nsid = config.KML

    target_href: str | None
    operations: list[Create | Delete | Change]

    def __init__(
        self,
        ns: str | None = None,
        name_spaces: dict[str, str] | None = None,
        target_href: str | None = None,
        operations: Iterable[Create | Delete | Change] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Create an Update object.

        Parameters
        ----------
        ns : str, optional
            The namespace to use for the Update object.
        name_spaces : dict, optional
            A dictionary of namespaces to use for the Update object.
        target_href : str, optional
            A URL that specifies the .kml or .kmz file whose data is to be modified.
        operations : Iterable[Union[Create, Delete, Change]], optional
            A sequence of update operations (Create, Delete, Change) to be applied
            in order.
        **kwargs : Any, optional
            Additional keyword arguments.

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )
        self.target_href = clean_string(target_href)
        self.operations = list(operations) if operations else []

    def __repr__(self) -> str:
        """
        Return a string representation of the Update object.

        Returns
        -------
            str: A string representation of the Update object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"target_href={self.target_href!r}, "
            f"operations={self.operations!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the update can be applied.

        An Update requires a target_href to identify the file to be modified.
        Without a target_href, the update cannot be applied.

        Returns
        -------
        bool
            True if the update has a target href and can be applied, False otherwise.

        """
        return bool(self.target_href)


class NetworkLinkControl(_XMLObject):
    """Controls the behavior of files fetched by a <NetworkLink>."""

    _default_nsid = config.KML

    min_refresh_period: float | None
    max_session_length: float | None
    cookie: str | None
    message: str | None
    link_name: str | None
    link_description: str | None
    link_snippet: str | None
    expires: KmlDateTime | None
    view: Camera | LookAt | None
    update: Update | None

    def __init__(
        self,
        ns: str | None = None,
        name_spaces: dict[str, str] | None = None,
        *,
        min_refresh_period: float | None = None,
        max_session_length: float | None = None,
        cookie: str | None = None,
        message: str | None = None,
        link_name: str | None = None,
        link_description: str | None = None,
        link_snippet: str | None = None,
        expires: KmlDateTime | None = None,
        view: Camera | LookAt | None = None,
        update: Update | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a NetworkLinkControl object.

        Parameters
        ----------
        ns : str, optional
            The namespace to use for the NetworkLinkControl object.
        name_spaces : dict, optional
            A dictionary of namespaces to use for the NetworkLinkControl object.
        min_refresh_period : float, optional
            The minimum number of seconds between fetches. A value of -1 indicates that
            the NetworkLinkControl object should be fetched only once.
        max_session_length : float, optional
            The maximum number of seconds that the link should be followed.
        cookie : str, optional
            A string value that can be used to identify the client request.
        message : str, optional
            A message to be displayed to the user in case of a failure.
        link_name : str, optional
            The name of the link.
        link_description : str, optional
            A description of the link.
        link_snippet : str, optional
            A snippet of text to be displayed in the link.
        expires : KmlDateTime, optional
            The time at which the link should expire.
        view : Camera or LookAt, optional
            The view to be used when the link is followed.
        update : Update, optional
            Specifies an addition, change, or deletion to KML data.
        **kwargs : Any, optional
            Additional keyword arguments.

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )
        self.min_refresh_period = min_refresh_period
        self.max_session_length = max_session_length
        self.cookie = clean_string(cookie)
        self.message = clean_string(message)
        self.link_name = clean_string(link_name)
        self.link_description = clean_string(link_description)
        self.link_snippet = clean_string(link_snippet)
        self.expires = expires
        self.view = view
        self.update = update

    def __repr__(self) -> str:
        """
        Return a string representation of the NetworkLinkControl object.

        Returns
        -------
            str: A string representation of the NetworkLinkControl object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"min_refresh_period={self.min_refresh_period!r}, "
            f"max_session_length={self.max_session_length!r}, "
            f"cookie={self.cookie!r}, "
            f"message={self.message!r}, "
            f"link_name={self.link_name!r}, "
            f"link_description={self.link_description!r}, "
            f"link_snippet={self.link_snippet!r}, "
            f"expires={self.expires!r}, "
            f"view={self.view!r}, "
            f"update={self.update!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    NetworkLinkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="min_refresh_period",
        node_name="minRefreshPeriod",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=0,
    ),
)
registry.register(
    NetworkLinkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="max_session_length",
        node_name="maxSessionLength",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=-1,
    ),
)
registry.register(
    NetworkLinkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="cookie",
        node_name="cookie",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    NetworkLinkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="message",
        node_name="message",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    NetworkLinkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="link_name",
        node_name="linkName",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    NetworkLinkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="link_description",
        node_name="linkDescription",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    NetworkLinkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="link_snippet",
        node_name="linkSnippet",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    NetworkLinkControl,
    item=RegistryItem(
        ns_ids=("kml",),
        classes=(KmlDateTime,),
        attr_name="expires",
        node_name="expires",
        get_kwarg=datetime_subelement_kwarg,
        set_element=datetime_subelement,
    ),
)
registry.register(
    NetworkLinkControl,
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
    NetworkLinkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="update",
        node_name="Update",
        classes=(Update,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)

registry.register(
    Update,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="target_href",
        node_name="targetHref",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    Update,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="operations",
        node_name="Create,Delete,Change",
        classes=(Create, Delete, Change),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)
