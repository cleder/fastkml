# Copyright (C) 2023  Christian Ledermann
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
"""Helper functions for fastkml."""
import logging
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.enums import Verbosity
from fastkml.exceptions import KMLParseError
from fastkml.registry import known_types
from fastkml.types import Element

logger = logging.getLogger(__name__)


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
    serialized_element = config.etree.tostring(  # type: ignore[attr-defined]
        element,
        encoding="UTF-8",
    ).decode(
        "UTF-8",
    )
    serialized_node = config.etree.tostring(  # type: ignore[attr-defined]
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
    else:
        logger.warning("%s, %s", error, msg)


def node_text(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    if getattr(obj, attr_name, None):
        element.text = getattr(obj, attr_name)


def text_subelement(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj (_XMLObject): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the subelement to create.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.

    Returns:
    -------
        None

    """
    if getattr(obj, attr_name, None):
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = getattr(obj, attr_name)


def text_attribute(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj (_XMLObject): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the attribute to be set.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.

    Returns:
    -------
        None

    """
    if getattr(obj, attr_name, None):
        element.set(node_name, getattr(obj, attr_name))


def bool_subelement(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj (_XMLObject): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the subelement to create.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.

    Returns:
    -------
        None

    """
    if getattr(obj, attr_name, None) is not None:
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = str(int(getattr(obj, attr_name)))


def int_subelement(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """
    Set the value of an attribute from a subelement with a text node.

    Args:
    ----
        obj (_XMLObject): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the subelement to create.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.

    Returns:
    -------
        None: This function does not return anything.

    """
    if getattr(obj, attr_name, None) is not None:
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = str(getattr(obj, attr_name))


def int_attribute(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """
    Set the value of an attribute.

    Args:
    ----
        obj (_XMLObject): The object from which to retrieve the attribute value.
        element (Element): The parent element to add the subelement to.
        attr_name (str): The name of the attribute to retrieve the value from.
        node_name (str): The name of the attribute to be set.
        precision (Optional[int]): The precision of the attribute value.
        verbosity (Optional[Verbosity]): The verbosity level.

    Returns:
    -------
        None: This function does not return anything.

    """
    if getattr(obj, attr_name, None) is not None:
        element.set(node_name, str(getattr(obj, attr_name)))


def float_subelement(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """Set the value of an attribute from a subelement with a text node."""
    if getattr(obj, attr_name, None) is not None:
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = str(getattr(obj, attr_name))


def float_attribute(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """Set the value of an attribute."""
    if getattr(obj, attr_name, None) is not None:
        element.set(node_name, str(getattr(obj, attr_name)))


def enum_subelement(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """Set the value of an attribute from a subelement with a text node."""
    if getattr(obj, attr_name, None):
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = getattr(obj, attr_name).value


def enum_attribute(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """Set the value of an attribute."""
    if getattr(obj, attr_name, None):
        element.set(node_name, getattr(obj, attr_name).value)


def xml_subelement(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    if getattr(obj, attr_name, None):
        element.append(
            getattr(obj, attr_name).etree_element(
                precision=precision,
                verbosity=verbosity,
            ),
        )


def xml_subelement_list(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
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
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, str]:
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
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, str]:
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    return {kwarg: node.text.strip()} if node.text and node.text.strip() else {}


def attribute_text_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, str]:
    return {kwarg: element.get(node_name)} if element.get(node_name) else {}


def _get_boolean_value(text: str, strict: bool) -> bool:
    if not strict:
        text = text.lower()
    if text in {"1", "true"}:
        return True
    if text in {"0", "false"}:
        return False
    if not strict:
        return bool(float(text))
    raise ValueError(f"Invalid boolean value: {text}")


def subelement_bool_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, bool]:
    assert len(classes) == 1
    assert issubclass(classes[0], bool)
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    if node.text and node.text.strip():
        try:
            return {kwarg: _get_boolean_value(node.text.strip(), strict)}
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
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, int]:
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
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, int]:
    return {kwarg: int(element.get(node_name))} if element.get(node_name) else {}


def subelement_float_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, float]:
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
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, float]:
    try:
        return {kwarg: float(element.get(node_name))} if element.get(node_name) else {}
    except ValueError as exc:
        handle_error(
            error=exc,
            strict=strict,
            element=element,
            node=element,
            expected="Float",
        )
    return {}


def _get_enum_value(enum_class: Type[Enum], text: str, strict: bool) -> Enum:
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
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, Enum]:
    assert len(classes) == 1
    assert issubclass(classes[0], Enum)
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    node_text = node.text.strip() if node.text else ""
    if node_text:
        try:
            return {kwarg: _get_enum_value(classes[0], node_text, strict)}
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
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, Enum]:
    assert len(classes) == 1
    assert issubclass(classes[0], Enum)
    if raw := element.get(node_name):
        try:
            value = classes[0](raw)
            if raw != value.value and strict:
                msg = (
                    f"Value {raw} is not a valid value for Enum "
                    f"{classes[0].__name__}"
                )
                raise ValueError(msg)
            return {kwarg: classes[0](raw)}
        except ValueError as exc:
            handle_error(
                error=exc,
                strict=strict,
                element=element,
                node=element,
                expected="Enum",
            )
    return {}


def xml_subelement_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, _XMLObject]:
    for cls in classes:
        assert issubclass(cls, _XMLObject)
        namespace = ns if cls._default_ns == ns else cls._default_ns
        subelement = element.find(f"{namespace}{cls.get_tag_name()}")
        if subelement is not None:
            return {
                kwarg: cls.class_from_element(
                    ns=namespace,
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
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, List[_XMLObject]]:
    args_list = []
    assert node_name is not None
    assert name_spaces is not None
    for obj_class in classes:
        assert issubclass(obj_class, _XMLObject)
        namespace = ns if obj_class._default_ns == ns else obj_class._default_ns
        if subelements := element.findall(f"{namespace}{obj_class.get_tag_name()}"):
            args_list.extend(
                [
                    obj_class.class_from_element(
                        ns=namespace,
                        name_spaces=name_spaces,
                        element=subelement,
                        strict=strict,
                    )
                    for subelement in subelements
                ],
            )
    return {kwarg: args_list}
