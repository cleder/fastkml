# Copyright (C) 2012 - 2020  Christian Ledermann
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

"""Abstract base classes"""
from typing import Optional
from typing import cast

import fastkml.config as config
from fastkml.config import etree
from fastkml.types import Element


class _XMLObject:
    """XML Baseclass."""

    __name__ = None

    def __init__(self, ns: Optional[str] = None) -> None:
        self.ns: str = config.KMLNS if ns is None else ns

    def etree_element(self) -> Element:
        if self.__name__:
            element = etree.Element(  # type: ignore [unreachable]
                f"{self.ns}{self.__name__}"
            )
        else:
            raise NotImplementedError(
                "Call of abstract base class, subclasses implement this!"
            )
        return element  # type: ignore [unreachable]

    def from_element(self, element: Element) -> None:
        if f"{self.ns}{self.__name__}" != element.tag:
            raise TypeError("Call of abstract base class, subclasses implement this!")

    def from_string(self, xml_string: str) -> None:
        self.from_element(cast(Element, etree.XML(xml_string)))

    def to_string(self, prettyprint: bool = True) -> str:
        """Return the KML Object as serialized xml"""
        if config.LXML and prettyprint:
            return etree.tostring(  # type: ignore
                self.etree_element(), encoding="utf-8", pretty_print=True
            ).decode("UTF-8")
        else:
            return etree.tostring(  # type: ignore
                self.etree_element(), encoding="utf-8"
            ).decode("UTF-8")


class _BaseObject(_XMLObject):
    """
    Base class for all KML objects.

    This is an abstract base class and cannot be used directly in a
    KML file. It provides the id attribute, which allows unique
    identification of a KML element, and the targetId attribute,
    which is used to reference objects that have already been loaded into
    Google Earth. The id attribute must be assigned if the <Update>
    mechanism is to be used.
    """

    id = None
    target_id = None

    def __init__(self, ns: Optional[str] = None, id: Optional[str] = None) -> None:
        super().__init__(ns)
        self.id = id

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.id:
            element.set("id", self.id)
        if self.target_id:
            element.set("targetId", self.target_id)  # type: ignore [unreachable]
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        if element.get("id"):
            self.id = element.get("id")
        if element.get("targetId"):
            self.target_id = element.get("targetId")
