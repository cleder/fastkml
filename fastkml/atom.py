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
import re
from typing import Any
from typing import Dict
from typing import Optional

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.config import ATOMNS as NS
from fastkml.enums import Verbosity
from fastkml.types import Element

logger = logging.getLogger(__name__)
regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
email_match = re.compile(regex).match


def check_email(email: str) -> bool:
    """Check if the email address is valid."""
    return bool(email_match(email))


class Link(_XMLObject):
    """
    Identifies a related Web page. The rel attribute defines the type of relation.
    A feed is limited to one alternate per type and hreflang.
    <link> is patterned after html's link element. It has one required
    attribute, href, and five optional attributes: rel, type, hreflang,
    title, and length.
    """

    __name__ = "link"

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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"href={self.href!r}, "
            f"rel={self.rel!r}, "
            f"type={self.type!r}, "
            f"hreflang={self.hreflang!r}, "
            f"title={self.title!r}, "
            f"length={self.length!r}, "
            ")"
        )

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
        kwargs["length"] = int(length) if length else None
        return kwargs


class _Person(_XMLObject):
    """
    <author> and <contributor> describe a person, corporation, or similar
    entity. It has one required element, name, and two optional elements:
    uri, email.
    """

    __name__ = ""

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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name={self.name!r}, "
            f"uri={self.uri!r}, "
            f"email={self.email!r}, "
            ")"
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        self.__name__ = self.__class__.__name__.lower()
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.name:
            name = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}name",
            )
            name.text = self.name
        else:
            logger.warning("No Name for person defined")
        if self.uri:
            uri = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}uri",
            )
            uri.text = self.uri
        if self.email and check_email(self.email):
            email = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}email",
            )
            email.text = self.email
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
        name = element.find(f"{ns}name")
        if name is not None:
            kwargs["name"] = name.text
        uri = element.find(f"{ns}uri")
        if uri is not None:
            kwargs["uri"] = uri.text
        email = element.find(f"{ns}email")
        if email is not None:
            kwargs["email"] = email.text
        return kwargs


class Author(_Person):
    """
    Return the names one author of the feed/entry.

    A feed/entry may have multiple authors.
    """

    __name__ = "author"


class Contributor(_Person):
    """
    Return the names one contributor to the feed/entry.

    A feed/entry may have multiple contributor elements.
    """

    __name__ = "contributor"


__all__ = ["Author", "Contributor", "Link", "NS"]
