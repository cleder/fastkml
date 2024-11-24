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

from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from fastkml.helpers import datetime_subelement
from fastkml.helpers import datetime_subelement_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.registry import registry
from fastkml.registry import RegistryItem
from fastkml.base import _XMLObject
from fastkml.times import KmlDateTime
from fastkml.update import Update
from fastkml.views import Camera, LookAt


class _NetworkControl(_XMLObject):
    """
    Absrtact base class representing NetworkLinkControl in KML.
    """
    min_refresh_period: Optional[float]
    max_session_length: Optional[float]
    cookie: Optional[str]
    message: Optional[str]
    link_name: Optional[str]
    link_description: Optional[str]
    link_snippet: Optional[str]
    expires: Optional[KmlDateTime]
    view: Union[Camera, LookAt, None]
    update:Optional[Update]

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
            update:Optional[Update] = None,
            **kwargs: Any,
    ):
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )
        self.min_refresh_period = min_refresh_period
        self.max_session_length = max_session_length
        self.cookie = cookie
        self.message = message
        self.link_name = link_name
        self.link_description = link_description
        self.link_snippet = link_snippet
        self.expires = expires
        self.view = view
        self.update = update

registry.register(
    _NetworkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="min_refresh_period",
        node_name="minRefreshPeriod",
        classes=(float,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _NetworkControl,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="max_session_length",
        node_name="maxSessionLength",
        classes=(float,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _NetworkControl,
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
    _NetworkControl,
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
    _NetworkControl,
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
    _NetworkControl,
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
    _NetworkControl,
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
    _NetworkControl,
    item=RegistryItem(
        ns_ids=("kml", ),
        classes=(KmlDateTime,),
        attr_name="expires",
        node_name="expires",
        get_kwarg=datetime_subelement_kwarg,
        set_element=datetime_subelement,
    ),
)

registry.register(
    _NetworkControl,
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