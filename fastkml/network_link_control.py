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
from typing import Any
from typing import Dict
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
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.times import KmlDateTime
from fastkml.views import Camera
from fastkml.views import LookAt

__all__ = [
    "NetworkLinkControl",
]

logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        min_refresh_period: Optional[float] = None,
        max_session_length: Optional[float] = None,
        cookie: Optional[str] = None,
        message: Optional[str] = None,
        link_name: Optional[str] = None,
        link_description: Optional[str] = None,
        link_snippet: Optional[str] = None,
        expires: Optional[KmlDateTime] = None,
        view: Optional[Union[Camera, LookAt]] = None,
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
