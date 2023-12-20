"""Helper functions for fastkml."""
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.base import _XMLObject
from fastkml.enums import Verbosity
from fastkml.types import Element


def simple_text_subelement(
    obj: _BaseObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
) -> None:
    """Set the value of an attribute from a subelement with a text node."""
    if getattr(obj, attr_name, None):
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = getattr(obj, attr_name)


def bool_subelement(
    obj: _BaseObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
) -> None:
    """Set the value of an attribute from a subelement with a text node."""
    if getattr(obj, attr_name, None):
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = str(int(getattr(obj, attr_name)))


def float_subelement(
    obj: _BaseObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
) -> None:
    """Set the value of an attribute from a subelement with a text node."""
    if getattr(obj, attr_name, None):
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = str(round(getattr(obj, attr_name), precision))


def enum_subelement(
    obj: _BaseObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
) -> None:
    """Set the value of an attribute from a subelement with a text node."""
    if getattr(obj, attr_name, None):
        subelement = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{obj.ns}{node_name}",
        )
        subelement.text = getattr(obj, attr_name).value


def xml_subelement(
    obj: _BaseObject,
    *,
    element: Element,
    attr_name: str,
    precision: Optional[int],
    verbosity: Verbosity,
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
    precision: Optional[int],
    verbosity: Verbosity,
) -> None:
    if getattr(obj, attr_name, None):
        for item in getattr(obj, attr_name):
            element.append(item.etree_element(precision=precision, verbosity=verbosity))


def subelement_text_kwarg(
    *,
    element: Element,
    ns: str,
    node_name: str,
    kwarg: str,
    strict: bool,
) -> Dict[str, str]:
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    return {kwarg: node.text.strip()} if node.text and node.text.strip() else {}


def subelement_bool_kwarg(
    *,
    element: Element,
    ns: str,
    node_name: str,
    kwarg: str,
    strict: bool,
) -> Dict[str, bool]:
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    if node.text and node.text.strip():
        if strict:
            return {kwarg: bool(int(node.text.strip()))}
        if node.text.strip().lower() in {"1", "true"}:
            return {kwarg: True}
        if node.text.strip().lower() in {"0", "false"}:
            return {kwarg: False}
    return {}


def subelement_float_kwarg(
    *,
    element: Element,
    ns: str,
    node_name: str,
    kwarg: str,
    precision: Optional[int],
    strict: bool,
) -> Dict[str, float]:
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    if node.text and node.text.strip():
        return {kwarg: float(node.text.strip())}
    return {}


def subelement_enum_kwarg(
    *,
    element: Element,
    ns: str,
    node_name: str,
    kwarg: str,
    enum_class: Type[Enum],
    strict: bool,
) -> Dict[str, Enum]:
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    if node.text and node.text.strip():
        return {kwarg: enum_class(node.text.strip())}
    return {}


def xml_subelement_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    kwarg: str,
    obj_class: Type[_XMLObject],
    strict: bool,
) -> Dict[str, _XMLObject]:
    subelement = element.find(f"{ns}{obj_class.get_tag_name()}")
    if subelement is None:
        return {}
    return {
        kwarg: obj_class.class_from_element(
            ns=ns,
            name_spaces=name_spaces,
            element=subelement,
            strict=strict,
        ),
    }


def xml_subelement_list_kwarg(
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    kwarg: str,
    obj_class: Type[_XMLObject],
    strict: bool,
) -> Dict[str, List[_XMLObject]]:
    if subelements := element.findall(f"{ns}{obj_class.get_tag_name()}"):
        return {
            kwarg: [
                obj_class.class_from_element(
                    ns=ns,
                    name_spaces=name_spaces,
                    element=subelement,
                    strict=strict,
                )
                for subelement in subelements
            ],
        }
    else:
        return {}
