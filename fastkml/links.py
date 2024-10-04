# Copyright (C) 2012-2023 Christian Ledermann
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
"""Link and Icon elements."""
from typing import Any
from typing import Dict
from typing import Optional

from fastkml.enums import RefreshMode
from fastkml.enums import ViewRefreshMode
from fastkml.helpers import enum_subelement
from fastkml.helpers import float_subelement
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.kml_base import _BaseObject
from fastkml.registry import RegistryItem
from fastkml.registry import registry


class Link(_BaseObject):
    """
    Represents a <Link> element.

    It specifies the location of any of the following:

    - KML files fetched by network links
    - Image files used in any Overlay
    - Model files used in the <Model> element

    https://developers.google.com/kml/documentation/kmlreference#link
    """

    href: Optional[str]
    refresh_mode: Optional[RefreshMode]
    refresh_interval: Optional[float]
    view_refresh_mode: Optional[ViewRefreshMode]
    view_refresh_time: Optional[float]
    view_bound_scale: Optional[float]
    view_format: Optional[str]
    http_query: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        href: Optional[str] = None,
        refresh_mode: Optional[RefreshMode] = None,
        refresh_interval: Optional[float] = None,
        view_refresh_mode: Optional[ViewRefreshMode] = None,
        view_refresh_time: Optional[float] = None,
        view_bound_scale: Optional[float] = None,
        view_format: Optional[str] = None,
        http_query: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the KML Icon Object."""
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.href = href
        self.refresh_mode = refresh_mode
        self.refresh_interval = refresh_interval
        self.view_refresh_mode = view_refresh_mode
        self.view_refresh_time = view_refresh_time
        self.view_bound_scale = view_bound_scale
        self.view_format = view_format
        self.http_query = http_query

    def __repr__(self) -> str:
        """Create a string (c)representation for Link."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"href={self.href!r}, "
            f"refresh_mode={self.refresh_mode}, "
            f"refresh_interval={self.refresh_interval!r}, "
            f"view_refresh_mode={self.view_refresh_mode}, "
            f"view_refresh_time={self.view_refresh_time!r}, "
            f"view_bound_scale={self.view_bound_scale!r}, "
            f"view_format={self.view_format!r}, "
            f"http_query={self.http_query!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the link has a valid href.

        Returns
        -------
        bool
            True if the link has a valid href, False otherwise.

        """
        return bool(self.href)


registry.register(
    Link,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="href",
        node_name="href",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    Link,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="view_format",
        node_name="viewFormat",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    Link,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="http_query",
        node_name="httpQuery",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    Link,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="refresh_mode",
        node_name="refreshMode",
        classes=(RefreshMode,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)
registry.register(
    Link,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="view_refresh_mode",
        node_name="viewRefreshMode",
        classes=(ViewRefreshMode,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)
registry.register(
    Link,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="refresh_interval",
        node_name="refreshInterval",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    Link,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="view_refresh_time",
        node_name="viewRefreshTime",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    Link,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="view_bound_scale",
        node_name="viewBoundScale",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)


class Icon(Link):
    """
    Represents an <Icon> element used in IconStyle and Overlays.

    Defines an image associated with an Icon style or overlay.
    The required <href> child element defines the location
    of the image to be used as the overlay or as the icon for the placemark.
    This location can either be on a local file system or a remote web server.

    https://developers.google.com/kml/documentation/kmlreference#icon

    Todo:
    ----
    The <gx:x>, <gx:y>, <gx:w>, and <gx:h> elements are used to select one
    icon from an image that contains multiple icons
    (often referred to as an icon palette).

    """
