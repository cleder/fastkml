"""Helper functions for fastkml."""

from typing import Dict

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.types import Element


def simple_text_subelement(
    obj: _BaseObject,
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


def subelement_text_kwarg(
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
