# Copyright (C) 2012 - 2021  Christian Ledermann
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
from typing import Optional
from typing import Tuple

from fastkml.base import _XMLObject
from fastkml.config import ATOMNS as NS
from fastkml.helpers import o_from_attr
from fastkml.helpers import o_from_subelement_text
from fastkml.helpers import o_int_from_attr
from fastkml.helpers import o_to_attr
from fastkml.helpers import o_to_subelement_text
from fastkml.types import Element
from fastkml.types import KmlObjectMap

logger = logging.getLogger(__name__)
regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
email_match = re.compile(regex).match


def check_email(email: str) -> bool:
    """Check if the email address is valid."""
    return bool(email_match(email))


class Link(_XMLObject):
    """
    Identifies a related Web page. The type of relation is defined by
    the rel attribute. A feed is limited to one alternate per type and
    hreflang.
    <link> is patterned after html's link element. It has one required
    attribute, href, and five optional attributes: rel, type, hreflang,
    title, and length.
    """

    __name__ = "link"

    kml_object_mapping: Tuple[KmlObjectMap, ...] = (
        {
            "kml_attr": "href",
            "obj_attr": "href",
            "from_kml": o_from_attr,
            "to_kml": o_to_attr,
            "required": True,
            "validator": None,
        },
        {
            "kml_attr": "rel",
            "obj_attr": "rel",
            "from_kml": o_from_attr,
            "to_kml": o_to_attr,
            "required": False,
            "validator": None,
        },
        {
            "kml_attr": "type",
            "obj_attr": "type",
            "from_kml": o_from_attr,
            "to_kml": o_to_attr,
            "required": False,
            "validator": None,
        },
        {
            "kml_attr": "hreflang",
            "obj_attr": "hreflang",
            "from_kml": o_from_attr,
            "to_kml": o_to_attr,
            "required": False,
            "validator": None,
        },
        {
            "kml_attr": "title",
            "obj_attr": "title",
            "from_kml": o_from_attr,
            "to_kml": o_to_attr,
            "required": False,
            "validator": None,
        },
        {
            "kml_attr": "length",
            "obj_attr": "length",
            "from_kml": o_int_from_attr,
            "to_kml": o_to_attr,
            "required": False,
            "validator": None,
        },
    )

    href = None
    # href is the URI of the referenced resource

    rel = None
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

    type = None
    # indicates the media type of the resource

    hreflang = None
    # indicates the language of the referenced resource

    title = None
    # human readable information about the link

    length = None
    # the length of the resource, in bytes

    def __init__(
        self,
        ns: Optional[str] = None,
        href: Optional[str] = None,
        rel: Optional[str] = None,
        type: Optional[str] = None,
        hreflang: Optional[str] = None,
        title: Optional[str] = None,
        length: Optional[int] = None,
    ) -> None:
        self.ns: str = NS if ns is None else ns
        self.href = href
        self.rel = rel
        self.type = type
        self.hreflang = hreflang
        self.title = title
        self.length = length

    def from_element(self, element: Element) -> None:
        super().from_element(element)

    def etree_element(self) -> Element:
        return super().etree_element()


class _Person(_XMLObject):
    """
    <author> and <contributor> describe a person, corporation, or similar
    entity. It has one required element, name, and two optional elements:
    uri, email.
    """

    __name__ = ""
    kml_object_mapping: Tuple[KmlObjectMap, ...] = (
        {
            "kml_attr": "name",
            "obj_attr": "name",
            "from_kml": o_from_subelement_text,
            "to_kml": o_to_subelement_text,
            "required": True,
            "validator": None,
        },
        {
            "kml_attr": "uri",
            "obj_attr": "uri",
            "from_kml": o_from_subelement_text,
            "to_kml": o_to_subelement_text,
            "required": False,
            "validator": None,
        },
        {
            "kml_attr": "email",
            "obj_attr": "email",
            "from_kml": o_from_subelement_text,
            "to_kml": o_to_subelement_text,
            "required": False,
            "validator": check_email,
        },
    )

    name: Optional[str] = None
    # conveys a human-readable name for the person.

    uri: Optional[str] = None
    # contains a home page for the person.

    email: Optional[str] = None
    # contains an email address for the person.

    def __init__(
        self,
        ns: Optional[str] = None,
        name: Optional[str] = None,
        uri: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        self.ns: str = NS if ns is None else ns
        self.name = name
        self.uri = uri
        self.email = email

    def etree_element(self) -> Element:
        return super().etree_element()

    def from_element(self, element: Element) -> None:
        super().from_element(element)


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


__all__ = ["Author", "Contributor", "Link"]
