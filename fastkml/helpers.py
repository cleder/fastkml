# Copyright (C) 2023 - 2024 Christian Ledermann
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
Helper functions for fastkml.

The helpers module acts as a bridge between the abstract registry definitions and the
concrete XML operations performed by ``_XMLObject``.

- Provides utility functions for XML parsing and serialization referenced in the
  registry for handling different data types.
- Implements ``get_kwarg`` and ``set_element`` functions used by ``_XMLObject``.
- Offers helper functions for common operations like text handling and type conversions.

``_XMLObject`` uses these helpers indirectly through the registry.
The registry references these helper functions for attribute parsing and serialization.
They form the implementation layer for the declarative approach defined by the registry.

"""

import logging
from enum import Enum
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import cast

from pygeoif.types import PointType

from fastkml import config
from fastkml.enums import Verbosity
from fastkml.exceptions import KMLParseError
from fastkml.types import Element

__all__ = [
    "attribute_enum_kwarg",
    "attribute_float_kwarg",
    "attribute_int_kwarg",
    "attribute_text_kwarg",
    "bool_subelement",
    "clean_string",
    "coords_subelement_list",
    "coords_subelement_list_kwarg",
    "datetime_subelement",
    "datetime_subelement_kwarg",
    "datetime_subelement_list",
    "datetime_subelement_list_kwarg",
    "enum_attribute",
    "enum_subelement",
    "float_attribute",
    "float_subelement",
    "get_coord_args",
    "get_ns",
    "get_value",
    "handle_error",
    "int_attribute",
    "int_subelement",
    "node_text",
    "node_text_kwarg",
    "subelement_bool_kwarg",
    "subelement_enum_kwarg",
    "subelement_float_kwarg",
    "subelement_int_kwarg",
    "subelement_text_kwarg",
    "text_attribute",
    "text_subelement",
    "xml_subelement",
    "xml_subelement_kwarg",
    "xml_subelement_list",
    "xml_subelement_list_kwarg",
]

if TYPE_CHECKING:
    from fastkml.base import _XMLObject
    from fastkml.times import KmlDateTime


logger = logging.getLogger(__name__)


def clean_string(value: Optional[str]) -> Optional[str]:
    """Clean and validate a string value, returning None if empty."""
    return value.strip() or None if value else None


def handle_error(
    *,
    error: Exception,
    strict: bool,
    element: Element,
    node: Element,
    expected: str,
) -> None:
    """
    Handle an error.

    Args:
    ----
        error (Exception): The exception that occurred.
        strict (bool): A flag indicating whether to raise an exception or log a warning.
        element (Element): The XML element being parsed.
        node (Element): The XML node that caused the error.
        expected (str): The expected format or value.

    Raises:
    ------
        KMLParseError: If `strict` is True, the function raises a `KMLParseError` with
        the error message.

    """
    serialized_element = config.etree.tostring(
        element,
        encoding="UTF-8",
    ).decode(
        "UTF-8",
    )
    serialized_node = config.etree.tostring(
        node,
        encoding="UTF-8",
    ).decode(
        "UTF-8",
    )
    msg = (
        f"Error parsing '{serialized_node}' in '{serialized_element}'; "
        f"expected: {expected}. \n {error}"
    )
    if strict:
        raise KMLParseError(msg) from error
    logger.warning("%s, %s", error, msg)


def get_ns(obj: "_XMLObject", value: object) -> str:
    """Get the namespace of an attribute, fall back on the objects namespace."""
    try:
        return obj.name_spaces.get(value.get_ns_id(), "")  # type: ignore[attr-defined]
    except AttributeError:
        return obj.ns


def get_value(
    obj: "_XMLObject",
    *,
    attr_name: str,
    verbosity: Verbosity,
    default: Optional[Any],
) -> Optional[Any]:
    """
    Get the value of an attribute from an object.

    If the verbosity is set to `Verbosity.terse`, the function returns `None` if the
    attribute value is equal to the default value. If the verbosity is set to
    `Verbosity.verbose`, the function returns the default value if the attribute value
    is `None`.

    Args:
    ----
        obj ("_XMLObject"): The object to get the attribute value from.
        attr_name (str): The name of the attribute to retrieve.
        verbosity (Optional[Verbosity]): The verbosity.
        default (Optional[Any]): The default value.

    """
    value = getattr(obj, attr_name, None)
    if value is None and default is not None and verbosity == Verbosity.verbose:
        return default
    return None if value == default and verbosity == Verbosity.terse else value


def node_text(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[str],
) -> None:
    """
    Set the text of an XML element based on the attribute value in the given object.

    Parameters
    ----------
    obj : "_XMLObject"
        The object containing the attribute value.
    element : Element
        The XML element to set the text content for.
    attr_name : str
        The name of the attribute in the object.
    node_name : str
        The name of the XML node (unused).
    precision : Optional[int]
        The precision to use when converting numeric values to text (unused).
    verbosity : Optional[Verbosity]
        The verbosity level for logging (unused).
    default : Optional[str]
        The default value for the attribute.

    Returns
    -------
    None
        This function does not return anything.

    """
    if value := get_value(
        obj,
        attr_name=attr_name,
        verbosity=verbosity,
        default=default,
    ):
        element.text = value


def text_subelement(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[str],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj ("_XMLObject"): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the subelement to create.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.
        default (Optional[str]): The default value for the attribute.

    Returns:
    -------
        None

    """
    if value := get_value(
        obj,
        attr_name=attr_name,
        verbosity=verbosity,
        default=default,
    ):
        subelement = config.etree.SubElement(
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = value


def text_attribute(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[str],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj ("_XMLObject"): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the attribute to be set.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.
        default (Optional[str]): The default value for the attribute.

    Returns:
    -------
        None

    """
    if value := get_value(
        obj,
        attr_name=attr_name,
        verbosity=verbosity,
        default=default,
    ):
        element.set(node_name, value)


def bool_subelement(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[bool],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj ("_XMLObject"): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the subelement to create.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.
        default (Optional[bool]): The default value for the attribute.

    Returns:
    -------
        None

    """
    value = get_value(obj, attr_name=attr_name, verbosity=verbosity, default=default)
    if value is not None:
        subelement = config.etree.SubElement(
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = str(int(value))


def int_subelement(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[int],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj ("_XMLObject"): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the subelement to create.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.
        default (Optional[int]): The default value for the attribute.

    Returns:
    -------
        None: This function does not return anything.

    """
    value = get_value(obj, attr_name=attr_name, verbosity=verbosity, default=default)
    if value is not None:
        subelement = config.etree.SubElement(
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = str(value)


def int_attribute(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[int],
) -> None:
    """
    Set the value of an attribute.

    Args:
    ----
        obj ("_XMLObject"): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the attribute to be set.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.
        default (Optional[int]): The default value for the attribute.

    Returns:
    -------
        None: This function does not return anything.

    """
    value = get_value(obj, attr_name=attr_name, verbosity=verbosity, default=default)
    if value is not None:
        element.set(node_name, str(value))


def float_subelement(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[float],
) -> None:
    """Set the value of an attribute from a subelement with a text node."""
    value = get_value(obj, attr_name=attr_name, verbosity=verbosity, default=default)
    if value is not None:
        subelement = config.etree.SubElement(
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = str(value)


def float_attribute(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[float],
) -> None:
    """Set the value of an attribute."""
    value = get_value(obj, attr_name=attr_name, verbosity=verbosity, default=default)
    if value is not None:
        element.set(node_name, str(value))


def enum_subelement(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[Enum],
) -> None:
    """Set the value of an attribute from a subelement with a text node."""
    value = get_value(obj, attr_name=attr_name, verbosity=verbosity, default=default)
    if value is not None:
        ns = get_ns(obj, value)
        subelement = config.etree.SubElement(
            element,
            f"{ns or ''}{node_name}",
        )
        subelement.text = value.value


def enum_attribute(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[Enum],
) -> None:
    """Set the value of an attribute."""
    value = get_value(obj, attr_name=attr_name, verbosity=verbosity, default=default)
    if value is not None:
        element.set(node_name, value.value)


def datetime_subelement(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[str],
) -> None:
    """Create the subelement for a KML datetime values."""
    if value := get_value(
        obj,
        attr_name=attr_name,
        verbosity=verbosity,
        default=default,
    ):
        ns = get_ns(obj, value)
        subelement = config.etree.SubElement(
            element,
            f"{ns}{node_name}",
        )
        subelement.text = str(value)


def datetime_subelement_list(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[str],
) -> None:
    """Create the subelements for a list of KML datetime values."""
    if value := get_value(
        obj,
        attr_name=attr_name,
        verbosity=verbosity,
        default=default,
    ):
        for item in value:
            ns = get_ns(obj, item)
            subelement = config.etree.SubElement(
                element,
                f"{ns}{node_name}",
            )
            subelement.text = str(item)


def coords_subelement_list(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[str],
) -> None:
    """Create the subelements for a list of KML coordinate values."""
    if value := get_value(
        obj,
        attr_name=attr_name,
        verbosity=verbosity,
        default=default,
    ):
        for coord in value:
            ns = get_ns(obj, coord)
            subelement = config.etree.SubElement(
                element,
                f"{ns}{node_name}",
            )
            if precision is None:
                subelement.text = " ".join(str(c) for c in coord)
            else:
                subelement.text = " ".join(f"{c:.{precision}f}" for c in coord)


def xml_subelement(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional["_XMLObject"],
) -> None:
    """
    Add a subelement to an XML element based on the value of an attribute of an object.

    Args:
    ----
        obj ("_XMLObject"): The object containing the attribute.
        element (Element): The XML element to which the subelement will be added.
        attr_name (str): The name of the attribute in the object.
        node_name (str): The name of the XML node for the subelement (unused).
        precision (Optional[int]): The precision for formatting numerical values.
        verbosity (Optional[Verbosity]): The verbosity level for the subelement.
        default (Optional["_XMLObject"]): The default value for the attribute (unused).

    Returns:
    -------
        None

    """
    if getattr(obj, attr_name, None):
        element.append(
            getattr(obj, attr_name).etree_element(
                precision=precision,
                verbosity=verbosity,
            ),
        )


def xml_subelement_list(
    obj: "_XMLObject",
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
    default: Optional[List["_XMLObject"]],
) -> None:
    """
    Add subelements to an XML element based on a list attribute of an object.

    Args:
    ----
        obj ("_XMLObject"): The object containing the list attribute.
        element (Element): The XML element to which the subelements will be added.
        attr_name (str): The name of the list attribute in the object.
        node_name (str): The name of the XML node for each subelement (unused).
        precision (Optional[int]): The precision for floating-point values.
        verbosity (Optional[Verbosity]): The verbosity level for the XML output.
        default (Optional[List["_XMLObject"]]): The default value for the attribute.

    Returns:
    -------
        None

    """
    if getattr(obj, attr_name, None):
        for item in getattr(obj, attr_name):
            if item:
                element.append(
                    item.etree_element(precision=precision, verbosity=verbosity),
                )


def node_text_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, str]:
    """
    Extract the text content of an XML element and return it as a dictionary.

    Args:
    ----
        element (Element): The XML element to extract the text content from.
        ns (str): The namespace of the XML element.
        name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to their
        URIs.
        node_name (str): The name of the XML node.
        kwarg (str): The name of the keyword argument to store the text content in.
        classes (Tuple[Type[object], ...]): A tuple of known types.
        strict (bool): A flag indicating whether to enforce strict parsing rules.

    Returns:
    -------
        Dict[str, str]: A dictionary containing the keyword argument and its
            corresponding text content, if it exists.

    """
    return (
        {kwarg: element.text.strip()} if element.text and element.text.strip() else {}
    )


def subelement_text_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, str]:
    """
    Extract the text content of a subelement and return it as a dictionary.

    Args:
    ----
        element (Element): The parent element.
        ns (str): The namespace of the subelement.
        name_spaces (Dict[str, str]): A dictionary of namespace prefixes and URIs.
        node_name (str): The name of the subelement.
        kwarg (str): The key to use in the returned dictionary.
        classes (Tuple[Type[object], ...]): A tuple of known types.
        strict (bool): A flag indicating whether to enforce strict parsing.

    Returns:
    -------
        Dict[str, str]: A dictionary containing the extracted text content,
            with the specified key.

    """
    node = element.find(f"{ns}{node_name}")
    if node is None or node.text is None:
        return {}
    assert isinstance(node.text, str)  # noqa: S101
    return {kwarg: node.text.strip()} if node.text and node.text.strip() else {}


def attribute_text_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, str]:
    """
    Return a dictionary representing the attribute as a keyword argument.

    Args:
    ----
        element (Element): The XML element.
        ns (str): The namespace of the attribute.
        name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to URIs.
        node_name (str): The name of the XML node.
        kwarg (str): The name of the keyword argument.
        classes (Tuple[Type[object], ...]): A tuple of known types.
        strict (bool): A flag indicating whether to enforce strict parsing.

    Returns:
    -------
        Dict[str, str]: A dictionary representing the attribute as a keyword argument.

    """
    attr = element.get(f"{ns}{node_name}")
    return {kwarg: attr} if attr else {}


def _get_boolean_value(*, text: str, strict: bool) -> bool:
    if not strict:
        text = text.lower()
    if text in {"1", "true"}:
        return True
    if text in {"0", "false"}:
        return False
    if not strict:
        return bool(float(text))
    msg = f"Value {text} is not a valid value for Boolean"
    raise ValueError(msg)


def subelement_bool_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, bool]:
    """
    Extract a boolean value from a subelement of an XML element.

    Args:
    ----
        element (Element): The XML element to search for the subelement.
        ns (str): The namespace of the subelement.
        name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to URIs.
        node_name (str): The name of the subelement.
        kwarg (str): The name of the keyword argument to store the boolean value.
        classes (Tuple[Type[object], ...]): A tuple of known types.
        strict (bool): A flag indicating whether to enforce strict parsing.

    Returns:
    -------
        Dict[str, bool]: A dictionary containing the keyword argument and its value.

    Raises:
    ------
        ValueError: If the value of the subelement is not a valid boolean.

    """
    assert len(classes) == 1  # noqa: S101
    assert issubclass(classes[0], bool)  # noqa: S101
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    if node.text and node.text.strip():
        try:
            return {kwarg: _get_boolean_value(text=node.text.strip(), strict=strict)}
        except ValueError as exc:
            handle_error(
                error=exc,
                strict=strict,
                element=element,
                node=node,
                expected="Boolean",
            )
    return {}


def subelement_int_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, int]:
    """
    Extract an integer value from a subelement of an XML element.

    Args:
    ----
        element (Element): The XML element to search for the subelement.
        ns (str): The namespace of the subelement.
        name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to URIs.
        node_name (str): The name of the subelement.
        kwarg (str): The key to use in the returned dictionary.
        classes (Tuple[Type[object], ...]): A tuple of known types for error handling.
        strict (bool): A flag indicating whether to enforce strict parsing.

    Returns:
    -------
        Dict[str, int]: A dictionary containing the keyword argument and its value.

    Raises:
    ------
        ValueError: If the value of the subelement is not a valid integer and strict.

    """
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    if node.text and node.text.strip():
        try:
            return {kwarg: int(node.text.strip())}
        except ValueError as exc:
            handle_error(
                error=exc,
                strict=strict,
                element=element,
                node=node,
                expected="Integer",
            )
    return {}


def attribute_int_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, int]:
    """
    Extract an integer attribute from an XML element and return it as a dictionary.

    Args:
    ----
        element (Element): The XML element to extract the attribute from.
        ns (str): The namespace of the attribute.
        name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to URIs.
        node_name (str): The name of the XML node containing the attribute.
        kwarg (str): The name of the keyword argument to store the extracted attribute.
        classes (Tuple[Type[object], ...]): A tuple of known types (unused).
        strict (bool): A flag indicating whether to raise an exception (unused).

    Returns:
    -------
        Dict[str, int]: A dictionary containing the extracted attribute value.

    """
    attr = element.get(f"{ns}{node_name}")
    return {kwarg: int(attr)} if attr else {}


def subelement_float_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, float]:
    """
    Extract a float value from a subelement of an XML element.

    Args:
    ----
        element (Element): The XML element to search for the subelement.
        ns (str): The namespace of the subelement.
        name_spaces (Dict[str, str]): A dictionary of namespace prefixes and URIs.
        node_name (str): The name of the subelement.
        kwarg (str): The name of the keyword argument to store the float value.
        classes (Tuple[Type[object], ...]): A tuple of known types for error handling.
        strict (bool): A flag indicating whether to raise an error.

    Returns:
    -------
        Dict[str, float]: A dictionary containing the float value as a keyword argument.

    Raises:
    ------
        ValueError: If the value of the subelement cannot be converted and strict.

    """
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    if node.text and node.text.strip():
        try:
            return {kwarg: float(node.text.strip())}
        except ValueError as exc:
            handle_error(
                error=exc,
                strict=strict,
                element=element,
                node=node,
                expected="Float",
            )
    return {}


def attribute_float_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, float]:
    """
    Convert an attribute value to a float and return it as a dictionary.

    Args:
    ----
        element (Element): The XML element containing the attribute.
        ns (str): The namespace of the attribute.
        name_spaces (Dict[str, str]): A dictionary of namespace prefixes and URIs.
        node_name (str): The name of the attribute.
        kwarg (str): The name of the keyword argument to store the converted float.
        classes (Tuple[Type[object], ...]): A tuple of known types for error handling.
        strict (bool): A flag indicating whether to raise an error for invalid values.

    Returns:
    -------
        Dict[str, float]: A dictionary containing the float as a keyword argument.

    Raises:
    ------
        ValueError: If the attribute value cannot be converted to a float.

    """
    attr = element.get(f"{ns}{node_name}")
    try:
        return {kwarg: float(attr)} if attr else {}
    except ValueError as exc:
        handle_error(
            error=exc,
            strict=strict,
            element=element,
            node=element,
            expected="Float",
        )
    return {}


def _get_enum_value(*, enum_class: Type[Enum], text: str, strict: bool) -> Enum:
    value = enum_class(text)
    if strict and value.value != text:
        msg = f"Value {text} is not a valid value for Enum {enum_class.__name__}"
        raise ValueError(msg)
    return value


def subelement_enum_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, Enum]:
    """
    Extract an enumerated value from a subelement of an XML element.

    Args:
    ----
        element (Element): The XML element to search for the subelement.
        ns (str): The namespace of the subelement.
        name_spaces (Dict[str, str]): A dictionary of namespace prefixes and URIs.
        node_name (str): The name of the subelement.
        kwarg (str): The name of the keyword argument to store the extracted value.
        classes (Tuple[Type[object], ...]): A tuple of enumerated value classes.
        strict (bool): A flag indicating whether to raise an exception.

    Returns:
    -------
        Dict[str, Enum]: A dictionary containing the extracted enumerated value.

    Raises:
    ------
        ValueError: If the extracted value is not a valid enumerated value and strict.

    """
    assert len(classes) == 1  # noqa: S101
    assert issubclass(classes[0], Enum)  # noqa: S101
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    node_text = node.text.strip() if node.text else ""
    if node_text:
        try:
            return {
                kwarg: _get_enum_value(
                    enum_class=classes[0],
                    text=node_text,
                    strict=strict,
                ),
            }
        except ValueError as exc:
            handle_error(
                error=exc,
                strict=strict,
                element=element,
                node=node,
                expected="Enum",
            )
    return {}


def attribute_enum_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, Enum]:
    """
    Return a dictionary with the specified keyword argument and its enum value.

    Args:
    ----
        element (Element): The XML element.
        ns (str): The namespace of the XML element.
        name_spaces (Dict[str, str]): A dictionary of namespace prefixes and their URIs.
        node_name (str): The name of the XML node.
        kwarg (str): The name of the keyword argument.
        classes (Tuple[Type[object], ...]): A tuple of enum classes.
        strict (bool): A flag indicating whether to raise an error for invalid values.

    Returns:
    -------
        Dict[str, Enum]: A dictionary with the specified keyword argument and its value.

    """
    assert len(classes) == 1  # noqa: S101
    assert issubclass(classes[0], Enum)  # noqa: S101
    if raw := element.get(f"{ns}{node_name}"):
        try:
            return {
                kwarg: _get_enum_value(
                    enum_class=classes[0],
                    text=raw,
                    strict=strict,
                ),
            }
        except ValueError as exc:
            handle_error(
                error=exc,
                strict=strict,
                element=element,
                node=element,
                expected="Enum",
            )
    return {}


def datetime_subelement_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, "KmlDateTime"]:
    """Extract a KML datetime from a subelement of an XML element."""
    cls = classes[0]
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    node_text = node.text.strip() if node.text else ""
    if node_text:
        try:
            return {kwarg: cls.parse(node_text)}  # type: ignore[attr-defined]
        except ValueError as exc:
            handle_error(
                error=exc,
                strict=strict,
                element=element,
                node=node,
                expected="DateTime",
            )
    return {}


def datetime_subelement_list_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, List["KmlDateTime"]]:
    """Extract a list of KML datetime values from subelements of an XML element."""
    args_list: List[KmlDateTime] = []
    cls = classes[0]
    if subelements := element.findall(f"{ns}{node_name}"):
        for subelement in subelements:
            try:
                args_list.append(
                    cls.parse(subelement.text),  # type: ignore[attr-defined]
                )
            except ValueError as exc:  # noqa: PERF203
                handle_error(
                    error=exc,
                    strict=strict,
                    element=element,
                    node=subelement,
                    expected="DateTime",
                )
    return {kwarg: args_list} if args_list else {}


def get_coord_args(
    element: Element,
    subelements: Iterable[Element],
    strict: bool,  # noqa: FBT001
) -> Iterable[PointType]:
    """Extract a list of KML coordinate values from subelements of an XML element."""
    for subelement in subelements:
        if subelement.text:
            try:
                yield cast(
                    PointType,
                    tuple(float(coord) for coord in subelement.text.split()),
                )
            except ValueError as exc:
                handle_error(
                    error=exc,
                    strict=strict,
                    element=element,
                    node=subelement,
                    expected="Coordinates",
                )


def coords_subelement_list_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, List[PointType]]:
    """Extract a list of KML coordinate values from subelements of an XML element."""
    args_list: List[PointType] = []
    if subelements := element.findall(f"{ns}{node_name}"):
        args_list = list(get_coord_args(element, subelements, strict))
    return {kwarg: args_list} if args_list else {}


def xml_subelement_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, "_XMLObject"]:
    """
    Return the subelement of the given XML element based on the provided parameters.

    Args:
    ----
    element (Element): The XML element to search within.
    ns (str): The namespace of the XML element.
    name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to their URIs.
    node_name (str): The name of the XML node to search for.
    kwarg (str): The name of the keyword argument to store the found subelement.
    classes (Tuple[Type[object], ...]): A tuple of classes that represent the types.
    strict (bool): A flag indicating whether to enforce strict parsing rules.

    Returns:
    -------
    Dict[str, "_XMLObject"]: A dictionary containing the found subelement as the value
        of the specified keyword argument.

    """
    for cls in classes:
        subelement = element.find(
            f"{ns}{cls.get_tag_name()}",  # type: ignore[attr-defined]
        )
        if subelement is not None:
            return {
                kwarg: cls.class_from_element(  # type: ignore[attr-defined]
                    ns=ns,
                    name_spaces=name_spaces,
                    element=subelement,
                    strict=strict,
                ),
            }
    return {}


def xml_subelement_list_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[Type[object], ...],
    strict: bool,
) -> Dict[str, List["_XMLObject"]]:
    """
    Return a dictionary with the specified keyword argument and its list of subelements.

    Args:
    ----
        element (Element): The XML element to search within.
        ns (str): The namespace of the XML element.
        name_spaces (Dict[str, str]): A dictionary mapping namespace prefixes to URIs.
        node_name (str): The name of the XML node to search for.
        kwarg (str): The name of the keyword argument to store the found subelements.
        classes (Tuple[Type[object], ...]): A tuple of classes that represent the types.
        strict (bool): A flag indicating whether to enforce strict parsing rules.

    Returns:
    -------
        Dict[str, List["_XMLObject"]]: A dictionary containing the specified keyword
            argument and its list of subelements.

    """
    args_list = []
    assert node_name is not None  # noqa: S101
    assert name_spaces is not None  # noqa: S101
    for obj_class in classes:
        if subelements := element.findall(
            f"{ns}{obj_class.get_tag_name()}",  # type: ignore[attr-defined]
        ):
            args_list.extend(
                [
                    obj_class.class_from_element(  # type: ignore[attr-defined]
                        ns=ns,
                        name_spaces=name_spaces,
                        element=subelement,
                        strict=strict,
                    )
                    for subelement in subelements
                ],
            )
    return {kwarg: args_list}
