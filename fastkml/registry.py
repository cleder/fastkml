# Copyright (C) 2023 Christian Ledermann
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
Registry for XML objects.

The Registry is used to store and retrieve information about XML objects.
This approach allows for flexible, declarative mapping between XML and Python objects,
with the registry acting as a central configuration for these mappings.

Direct ``Registry`` class use is typically only for library internals or advanced
customization. For normal usage, stick with the ``registry`` instance:

- The library is designed around this global instance.
- Ensures all parts of the library use the same registry.
- Pre-populated with standard KML mappings.
- Singleton pattern: Avoids multiple conflicting registries.

"""

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from typing_extensions import Protocol

from fastkml.enums import Verbosity
from fastkml.types import Element

if TYPE_CHECKING:
    from fastkml.base import _XMLObject


class GetKWArgs(Protocol):
    def __call__(
        self,
        *,
        element: Element,
        ns: str,
        name_spaces: Dict[str, str],
        node_name: str,
        kwarg: str,
        classes: Tuple[Type[object], ...],
        strict: bool,
    ) -> Dict[str, Any]: ...


class SetElement(Protocol):
    def __call__(
        self,
        obj: "_XMLObject",
        *,
        element: Element,
        attr_name: str,
        node_name: str,
        precision: Optional[int],
        verbosity: Verbosity,
        default: Any,
    ) -> None: ...


@dataclass(frozen=True)
class RegistryItem:
    """
    A registry item.

    The RegistryItem class is a dataclass that represents a single mapping between an
    XML object and a Python object. It contains the following fields:

    - ``ns_ids``: A tuple of namespace identifiers that the mapping applies to.
    - ``classes``: A tuple of Python classes that the mapping applies to.
    - ``attr_name``: The name of the attribute on the Python object that corresponds to
      the XML object.
    - ``get_kwarg``: A function that retrieves keyword arguments for the Python object.
    - ``type``: The type of the XML object.
    - ``node_name``: The name of the XML node that the mapping applies to.
    - ``default``: An optional default value for the Python object attribute.

    """

    ns_ids: Tuple[str, ...]
    classes: Tuple[Type[object], ...]
    attr_name: str
    get_kwarg: GetKWArgs
    set_element: SetElement
    node_name: str
    default: Any = None


class Registry:
    """
    A registry of XML objects.

    The registry acts as a configuration hub, allowing the library to dynamically handle
    various KML elements and their attributes without hardcoding the logic into each
    class.

    The purpose of the registry is to:

    - Centralize XML mapping configuration for KML objects.
    - Define attribute-to-element/attribute mappings.
    - Specify parsing and serialization functions for each attribute.
    - Support inheritance in XML mappings.
    - Provide a flexible, declarative approach to XML handling.
    - Decouple XML parsing/serialization logic from class definitions.
    - Allow easy addition or modification of XML mappings.
    - Enable consistent handling of attributes across different KML classes.
    - Facilitate extensibility and maintainability of the library.

    """

    _registry: Dict[Type["_XMLObject"], List[RegistryItem]]

    def __init__(
        self,
        registry: Optional[Dict[Type["_XMLObject"], List[RegistryItem]]] = None,
    ) -> None:
        """Initialize the registry."""
        self._registry = registry or {}

    def __repr__(self) -> str:
        """Create a string (c)representation for Registry."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}({self._registry})"
        )

    def register(self, cls: Type["_XMLObject"], item: RegistryItem) -> None:
        """
        Register a class.

        Add a new RegistryItem to the registry for a specific class.

        - Appends the item to an existing list if the class is already registered.
        - Creates a new list with the item if it's the first for that class.
        - Associates XML parsing/serialization rules with a class attribute.
        - Defines how a specific attribute should be handled in XML operations.
        - Allows for multiple registrations per class, supporting complex mappings.
        - Is called during library initialization to set up KML mappings.

        This is the primary way to configure how different KML elements and their
        attributes are processed in fastkml.

        """
        existing = self._registry.get(cls, [])
        existing.append(item)
        self._registry[cls] = existing

    def get(self, cls: Type["_XMLObject"]) -> List[RegistryItem]:
        """
        Get the registry items for a class and its ancestors.

        The get method of the registry, in conjunction with _XMLObject:

        - Retrieves all registered items for a given class and its ancestors.
        - Supports inheritance in XML mappings.
        - Allows ``_XMLObject`` to dynamically determine how to parse/serialize
          attributes.
        - Enables flexible XML handling without hardcoding in each class.
        - Facilitates polymorphic behavior in XML parsing and serialization.

        It allows ``_XMLObject`` to handle different KML elements consistently while
        respecting their inheritance structure.

        """
        parents = reversed(cls.__mro__[:-1])
        items = []
        for parent in parents:
            items.extend(self._registry.get(parent, []))
        return items


registry = Registry()

__all__ = ["registry", "RegistryItem"]
