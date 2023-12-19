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
) -> Dict[str, str]:
    kwargs = {}
    node = element.find(f"{ns}{node_name}")
    if node is None:
        return {}
    if node.text and node.text.strip():
        kwargs[kwarg] = node.text.strip()
    return kwargs
