"""Helper functions for fastkml."""

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
