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
from typing import Any
from typing import Optional
from typing import Union

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

__all__ = [
    "Change",
    "Create",
    "Delete",
    "NetworkLinkControl",
    "Update",
]

logger = logging.getLogger(__name__)


class _UpdateAction(_XMLObject):
    """
    Base class for Update action elements (Create, Delete, Change).

    These elements contain KML objects that are the subject of the update action.
    """

    _default_nsid = config.KML

    objects: list[_XMLObject]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        objects: Optional[Iterable[_XMLObject]] = None,
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
        objects : Iterable[_XMLObject], optional
            The KML objects that are subject to this update action.
        **kwargs : Any, optional
            Additional keyword arguments.

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )
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


class Create(_UpdateAction):
    """
    Create element for Update.

    Adds new elements to a Folder or Document that has already been loaded via a
    NetworkLink. The targetHref element in Update specifies the file containing
    the element(s) to be modified.
    """


class Delete(_UpdateAction):
    """
    Delete element for Update.

    Deletes features from a complex element that has already been loaded via a
    NetworkLink. The targetHref element in Update specifies the file containing
    the element(s) to be deleted.
    """


class Change(_UpdateAction):
    """
    Change element for Update.

    Modifies the values in an element that has already been loaded via a NetworkLink.
    The targetHref element in Update specifies the file containing the element(s)
    to be modified.
    """


class Update(_XMLObject):
    """
    Specifies an addition, change, or deletion to KML data.

    The data has already been loaded using the specified URL.
    The <targetHref> specifies the .kml or .kmz file whose data (within Google Earth)
    is to be modified. <Update> is always contained in a NetworkLinkControl.
    Furthermore, the file containing the NetworkLinkControl must have been loaded
    by a NetworkLink.

    https://developers.google.com/kml/documentation/kmlreference#update
    """

    _default_nsid = config.KML

    target_href: Optional[str]
    create: Optional[Create]
    delete: Optional[Delete]
    change: Optional[Change]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        target_href: Optional[str] = None,
        create: Optional[Create] = None,
        delete: Optional[Delete] = None,
        change: Optional[Change] = None,
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
        create : Create, optional
            Specifies new elements to be added to a loaded KML file.
        delete : Delete, optional
            Specifies elements to be deleted from a loaded KML file.
        change : Change, optional
            Specifies elements to be changed in a loaded KML file.
        **kwargs : Any, optional
            Additional keyword arguments.

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )
        self.target_href = clean_string(target_href)
        self.create = create
        self.delete = delete
        self.change = change

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
            f"create={self.create!r}, "
            f"delete={self.delete!r}, "
            f"change={self.change!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the update has content.

        Returns
        -------
        bool
            True if the update has a target href or any actions, False otherwise.

        """
        return bool(self.target_href or self.create or self.delete or self.change)


class NetworkLinkControl(_XMLObject):
    """Controls the behavior of files fetched by a <NetworkLink>."""

    _default_nsid = config.KML

    min_refresh_period: Optional[float]
    max_session_length: Optional[float]
    cookie: Optional[str]
    message: Optional[str]
    link_name: Optional[str]
    link_description: Optional[str]
    link_snippet: Optional[str]
    expires: Optional[KmlDateTime]
    view: Union[Camera, LookAt, None]
    update: Optional[Update]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        min_refresh_period: Optional[float] = None,
        max_session_length: Optional[float] = None,
        cookie: Optional[str] = None,
        message: Optional[str] = None,
        link_name: Optional[str] = None,
        link_description: Optional[str] = None,
        link_snippet: Optional[str] = None,
        expires: Optional[KmlDateTime] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        update: Optional[Update] = None,
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
        attr_name="create",
        node_name="Create",
        classes=(Create,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Update,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="delete",
        node_name="Delete",
        classes=(Delete,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Update,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="change",
        node_name="Change",
        classes=(Change,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
