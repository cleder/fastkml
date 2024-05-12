# Copyright (C) 2012 - 2024  Christian Ledermann
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
from fastkml.helpers import attribute_int_kwarg
from fastkml.helpers import attribute_text_kwarg
from fastkml.helpers import int_attribute
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_attribute
from fastkml.helpers import text_subelement
from fastkml.registry import RegistryItem
from fastkml.registry import registry

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
        **kwargs: Any,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.href = href
        self.rel = rel
        self.type = type
        self.hreflang = hreflang
        self.title = title
        self.length = length

    def __repr__(self) -> str:
        """Create a string (c)representation for Link."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"href={self.href!r}, "
            f"rel={self.rel!r}, "
            f"type={self.type!r}, "
            f"hreflang={self.hreflang!r}, "
            f"title={self.title!r}, "
            f"length={self.length!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.href)

    def __eq__(self, other: object) -> bool:
        try:
            assert isinstance(other, type(self))
        except AssertionError:
            return False
        return (
            super().__eq__(other)
            and self.href == other.href
            and self.rel == other.rel
            and self.type == other.type
            and self.hreflang == other.hreflang
            and self.title == other.title
            and self.length == other.length
        )


registry.register(
    Link,
    item=RegistryItem(
        attr_name="href",
        node_name="href",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
registry.register(
    Link,
    item=RegistryItem(
        attr_name="rel",
        node_name="rel",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
registry.register(
    Link,
    item=RegistryItem(
        attr_name="type",
        node_name="type",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
registry.register(
    Link,
    item=RegistryItem(
        attr_name="hreflang",
        node_name="hreflang",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)

registry.register(
    Link,
    item=RegistryItem(
        attr_name="title",
        node_name="title",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
registry.register(
    Link,
    item=RegistryItem(
        attr_name="length",
        node_name="length",
        classes=(int,),
        get_kwarg=attribute_int_kwarg,
        set_element=int_attribute,
    ),
)


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
        **kwargs: Any,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.name = name
        self.uri = uri
        self.email = email

    def __repr__(self) -> str:
        """Create a string (c)representation for _Person."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"name={self.name!r}, "
            f"uri={self.uri!r}, "
            f"email={self.email!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.name)

    def __eq__(self, other: object) -> bool:
        try:
            assert isinstance(other, type(self))
        except AssertionError:
            return False
        return (
            super().__eq__(other)
            and self.name == other.name
            and self.uri == other.uri
            and self.email == other.email
        )


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
