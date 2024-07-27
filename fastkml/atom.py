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
Basic Atom support for KML.

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

    _default_nsid = config.ATOM

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return cls.__name__.lower()


class Link(_AtomObject):
    """
    Identifies a related Web page.

    The rel attribute defines the type of relation.
    A feed is limited to one alternate per type and hreflang.
    <link> is patterned after html's link element. It has one required
    attribute, href, and five optional attributes: rel, type, hreflang,
    title, and length.
    """

    href: Optional[str]
    rel: Optional[str]
    type: Optional[str]
    hreflang: Optional[str]
    title: Optional[str]
    length: Optional[int]

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
        """
        Initialize a Link object.

        Parameters
        ----------
        ns : str, optional
            The namespace of the Link object.
        name_spaces : dict, optional
            The dictionary of namespace prefixes and URIs.
        href : str, optional
            The URI of the referenced resource.
        rel : str, optional
            The link relationship type. It can be a full URI or one of the
            following predefined values: 'alternate', 'enclosure', 'related',
            'self', or 'via'.
        type : str, optional
            The media type of the resource.
        hreflang : str, optional
            The language of the referenced resource.
        title : str, optional
            Human-readable information about the link.
        length : int, optional
            The length of the resource in bytes.
        kwargs : dict, optional
            Additional keyword arguments.

        Returns
        -------
        None

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.href = href
        self.rel = rel
        self.type = type
        self.hreflang = hreflang
        self.title = title
        self.length = length

    def __repr__(self) -> str:
        """
        Return a string representation of the Link object.

        Returns
        -------
        str
            The string representation of the Link object.

        """
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
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the Link object is truthy.

        Returns
        -------
        bool
            True if the Link object has a href attribute, False otherwise.

        """
        return bool(self.href)


registry.register(
    Link,
    item=RegistryItem(
        ns_ids=("", "atom"),
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
        ns_ids=("", "atom"),
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
        ns_ids=("", "atom"),
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
        ns_ids=("", "atom"),
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
        ns_ids=("", "atom"),
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
        ns_ids=("", "atom"),
        attr_name="length",
        node_name="length",
        classes=(int,),
        get_kwarg=attribute_int_kwarg,
        set_element=int_attribute,
    ),
)


class _Person(_AtomObject):
    """
    Represents a person, corporation, or similar entity.

    Attributes
    ----------
        name (Optional[str]): A human-readable name for the person.
        uri (Optional[str]): A home page for the person.
        email (Optional[str]): An email address for the person.

    """

    name: Optional[str]
    uri: Optional[str]
    email: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        uri: Optional[str] = None,
        email: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the _Person class.

        Args:
        ----
            ns (Optional[str]): The namespace for the XML element.
            name_spaces (Optional[Dict[str, str]]): The namespace dictionary.
            name (Optional[str]): A human-readable name for the person.
            uri (Optional[str]): A home page for the person.
            email (Optional[str]): An email address for the person.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.name = name
        self.uri = uri
        self.email = email

    def __repr__(self) -> str:
        """
        Return a string representation of the _Person object.

        Returns
        -------
            str: The string representation of the _Person object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"name={self.name!r}, "
            f"uri={self.uri!r}, "
            f"email={self.email!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the _Person object has a name.

        Returns
        -------
            bool: True if the _Person object has a name, False otherwise.

        """
        return bool(self.name)


registry.register(
    _Person,
    item=RegistryItem(
        ns_ids=("atom",),
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
        ns_ids=("atom",),
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
        ns_ids=("atom",),
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
