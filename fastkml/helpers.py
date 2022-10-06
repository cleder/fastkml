# Copyright (C) 2020  Christian Ledermann
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

"""Helper functions and classes."""
import logging
from typing import Any
from typing import Callable
from typing import Optional

from fastkml import config
from fastkml.types import Element

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
            elem = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{obj.ns}{kml_attr}",  # type: ignore[attr-defined]
            )
            elem.text = str(attribute)
    elif required:
        logger.warning(
            "Required attribute '%s' for '%s' missing.",
            obj_attr,
            obj.__class__.__name__,
        )
