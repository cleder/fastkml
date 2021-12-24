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
import logging
from typing import Any
from typing import Callable
from typing import Optional
from typing import Tuple
from typing import cast

from fastkml import config
from fastkml.types import Element
from fastkml.types import KmlObjectMap

logger = logging.getLogger(__name__)


def o_to_attr(
    obj: object,
    element: Element,
    kml_attr: str,
    obj_attr: str,
    required: bool,
    **kwargs: Any,
) -> None:
    """Set an attribute on an KML Element from an object attribute."""
    attribute = getattr(obj, obj_attr)
    if attribute:
        element.set(kml_attr, str(attribute))
    elif required:
        logger.warning(
            "Required attribute '%s' for '%s' missing.",
            obj_attr,
            obj.__class__.__name__,
        )


def o_from_attr(
    obj: object,
    element: Element,
    kml_attr: str,
    obj_attr: str,
    required: bool,
    **kwargs: Any,
) -> None:
    """Set an attribute on self from an KML attribute."""
    attribute = element.get(kml_attr)
    if attribute:
        setattr(obj, obj_attr, attribute)
    elif required:
        logger.warning(
            "Required attribute '%s' for '%s' missing.",
            kml_attr,
            obj.__class__.__name__,
        )


def o_int_from_attr(
    obj: object,
    element: Element,
    kml_attr: str,
    obj_attr: str,
    required: bool,
    **kwargs: Any,
) -> None:
    """Set an attribute on self from an KML attribute."""
    try:
        attribute = int(element.get(kml_attr))
    except (ValueError, TypeError):
        attribute = None
    if attribute is not None:
        setattr(obj, obj_attr, attribute)
    elif required:
        logger.warning(
            "Required attribute '%s' for '%s' missing.",
            kml_attr,
            obj.__class__.__name__,
        )


def o_from_subelement_text(
    obj: object,
    element: Element,
    kml_attr: str,
    obj_attr: str,
    required: bool,
    validator: Optional[Callable[..., bool]] = None,
    **kwargs: Any,
) -> None:
    """Set an attribute on self from the text of a SubElement."""
    elem = element.find(f"{obj.ns}{kml_attr}")  # type: ignore[attr-defined]
    if elem is not None:
        if validator is not None and not validator(elem.text):
            logger.warning(
                "Invalid value for attribute '%s' for '%s'",
                kml_attr,
                obj.__class__.__name__,
            )
        else:
            setattr(obj, obj_attr, elem.text)
    elif required:  # type: ignore[unreachable]
        logger.warning(
            "Required attribute '%s' for '%s' missing.",
            kml_attr,
            obj.__class__.__name__,
        )


def o_to_subelement_text(
    obj: object,
    element: Element,
    kml_attr: str,
    obj_attr: str,
    required: bool,
    validator: Optional[Callable[..., bool]] = None,
    **kwargs: Any,
) -> None:
    """Set the text of a SubElement from an object attribute."""
    attribute = getattr(obj, obj_attr)
    if attribute:
        if validator is not None and not validator(attribute):
            logger.warning(
                "Invalid value for attribute '%s' for '%s'",
                obj_attr,
                obj.__class__.__name__,
            )
        else:
            elem = config.etree.SubElement(
                element,  # type: ignore[arg-type]
                f"{obj.ns}{kml_attr}",  # type: ignore[attr-defined]
            )
            elem.text = str(attribute)
    elif required:
        logger.warning(
            "Required attribute '%s' for '%s' missing.",
            obj_attr,
            obj.__class__.__name__,
        )


class _XMLObject:
    """XML Baseclass."""

    __name__ = ""
    kml_object_mapping: Tuple[KmlObjectMap, ...] = ()

    def __init__(self, ns: Optional[str] = None) -> None:
        """Initialize the XML Object."""
        self.ns: str = config.KMLNS if ns is None else ns

    def etree_element(self) -> Element:
        """Return the KML Object as an Element."""
        if self.__name__:
            element = config.etree.Element(f"{self.ns}{self.__name__}")
        else:
            raise NotImplementedError(
                "Call of abstract base class, subclasses implement this!"
            )
        for mapping in self.kml_object_mapping:
            mapping["to_kml"](self, element, **mapping)
        return element  # type: ignore [return-value]

    def from_element(self, element: Element) -> None:
        """Load the KML Object from an Element."""
        if f"{self.ns}{self.__name__}" != element.tag:
            raise TypeError("Call of abstract base class, subclasses implement this!")
        for mapping in self.kml_object_mapping:
            mapping["from_kml"](self, element, **mapping)

    def from_string(self, xml_string: str) -> None:
        """Load the KML Object from serialized xml."""
        self.from_element(cast(Element, config.etree.XML(xml_string)))

    def to_string(self, prettyprint: bool = True) -> str:
        """Return the KML Object as serialized xml."""
        try:
            return cast(
                str,
                config.etree.tostring(  # type: ignore[call-overload]
                    self.etree_element(),
                    encoding="utf-8",
                    pretty_print=prettyprint,
                ).decode("UTF-8"),
            )
        except TypeError:
            return cast(
                str,
                config.etree.tostring(  # type: ignore[call-overload]
                    self.etree_element(), encoding="utf-8"
                ).decode("UTF-8"),
            )


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
    kml_object_mapping: Tuple[KmlObjectMap, ...] = (
        {
            "kml_attr": "id",
            "obj_attr": "id",
            "from_kml": o_from_attr,
            "to_kml": o_to_attr,
            "required": False,
            "validator": None,
        },
        {
            "kml_attr": "targetId",
            "obj_attr": "target_id",
            "from_kml": o_from_attr,
            "to_kml": o_to_attr,
            "required": False,
            "validator": None,
        },
    )

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> None:
        """Initialize the KML Object."""
        super().__init__(ns)
        self.id = id
        self.target_id = target_id

    def etree_element(self) -> Element:
        """Return the KML Object as an Element."""
        return super().etree_element()

    def from_element(self, element: Element) -> None:
        """Load the KML Object from an Element."""
        super().from_element(element)
