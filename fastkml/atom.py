# Copyright (C) 2012 - 2023  Christian Ledermann
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
KML 2.2 supports new elements for including data about the author and related
website in your KML file. This information is displayed in geo search results,
both in Earth browsers such as Google Earth, and in other applications such as
Google Maps. The ascription elements used in KML are as follows:

atom:author element - parent element for atom:name
atom:name element - the name of the author
atom:link element - contains the href attribute
href attribute - URL of the web page containing the KML/KMZ file

These elements are defined in the Atom Syndication Format. The complete
specification is found at http://atompub.org.

This library only implements a subset of Atom that is useful with KML
"""

import logging
from typing import Any
from typing import Dict
from typing import Optional

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.config import ATOMNS as NS
from fastkml.enums import Verbosity
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.types import Element

logger = logging.getLogger(__name__)


class _AtomObject(_XMLObject):
    """
    Baseclass for Atom Objects.

    Atom objects are used in KML to provide information about the author and
    related website in your KML file. This information is displayed in geo
    search results, both in Earth browsers such as Google Earth, and in other
    applications such as Google Maps.
    The atom tag name is the class name in lower case.
    """

    _default_ns = config.ATOMNS

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return cls.__name__.lower()


class Link(_AtomObject):
    """
    Identifies a related Web page. The rel attribute defines the type of relation.
    A feed is limited to one alternate per type and hreflang.
    <link> is patterned after html's link element. It has one required
    attribute, href, and five optional attributes: rel, type, hreflang,
    title, and length.
    """

    href: Optional[str]
    # href is the URI of the referenced resource

    rel: Optional[str]
    # rel contains a single link relationship type.
    # It can be a full URI, or one of the following predefined values
    # (default=alternate):
    # alternate: an alternate representation
    # enclosure: a related resource which is potentially large in size
    # and might require special handling, for example an audio or video
    # recording.
    # related: an document related to the entry or feed.
    # self: the feed itself.
    # via: the source of the information provided in the entry.

    type: Optional[str]
    # indicates the media type of the resource

    hreflang: Optional[str]
    # indicates the language of the referenced resource

    title: Optional[str]
    # human readable information about the link

    length: Optional[int]
    # the length of the resource, in bytes

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        href: Optional[str] = None,
        rel: Optional[str] = None,
        type: Optional[str] = None,
        hreflang: Optional[str] = None,
        title: Optional[str] = None,
        length: Optional[int] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.href = href
        self.rel = rel
        self.type = type
        self.hreflang = hreflang
        self.title = title
        self.length = length

    def __bool__(self) -> bool:
        return bool(self.href)

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.href:
            element.set("href", self.href)
        else:
            logger.warning("required attribute href missing")
        if self.rel:
            element.set("rel", self.rel)
        if self.type:
            element.set("type", self.type)
        if self.hreflang:
            element.set("hreflang", self.hreflang)
        if self.title:
            element.set("title", self.title)
        if self.length:
            element.set("length", str(self.length))
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
        kwargs["href"] = element.get("href")
        kwargs["rel"] = element.get("rel")
        kwargs["type"] = element.get("type")
        kwargs["hreflang"] = element.get("hreflang")
        kwargs["title"] = element.get("title")
        length = element.get("length")
        kwargs["length"] = int(length) if length and length.strip() else None
        return kwargs


class _Person(_AtomObject):
    """
    <author> and <contributor> describe a person, corporation, or similar
    entity. It has one required element, name, and two optional elements:
    uri, email.
    """

    name: Optional[str]
    # conveys a human-readable name for the person.

    uri: Optional[str]
    # contains a home page for the person.

    email: Optional[str]
    # contains an email address for the person.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        uri: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.name = name
        self.uri = uri
        self.email = email

    def __bool__(self) -> bool:
        return bool(self.name)


registry.register(
    _Person,
    item=RegistryItem(
        attr_name="name",
        node_name="name",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _Person,
    item=RegistryItem(
        attr_name="uri",
        node_name="uri",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _Person,
    item=RegistryItem(
        attr_name="email",
        node_name="email",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)


class Author(_Person):
    """
    Return the names one author of the feed/entry.

    A feed/entry may have multiple authors.
    """


class Contributor(_Person):
    """
    Return the names one contributor to the feed/entry.

    A feed/entry may have multiple contributor elements.
    """


__all__ = ["Author", "Contributor", "Link", "NS"]
