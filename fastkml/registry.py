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
"""Registry for XML objects."""
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from typing_extensions import Protocol

from fastkml.enums import Verbosity
from fastkml.types import Element

if TYPE_CHECKING:
    from fastkml.base import _XMLObject


known_types = Union[
    Type["_XMLObject"],
    Type[Enum],
    Type[bool],
    Type[int],
    Type[str],
    Type[float],
]


class GetKWArgs(Protocol):
    def __call__(
        self,
        *,
        element: Element,
        ns: str,
        name_spaces: Dict[str, str],
        node_name: str,
        kwarg: str,
        classes: Tuple[known_types, ...],
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
        verbosity: Optional[Verbosity],
    ) -> None: ...


@dataclass(frozen=True)
class RegistryItem:
    """A registry item."""

    ns_ids: Tuple[str, ...]
    classes: Tuple[known_types, ...]
    attr_name: str
    get_kwarg: GetKWArgs
    set_element: SetElement
    node_name: str


class Registry:
    """A registry of XML objects."""

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
        """Register a class."""
        existing = self._registry.get(cls, [])
        existing.append(item)
        self._registry[cls] = existing

    def get(self, cls: Type["_XMLObject"]) -> List[RegistryItem]:
        """Get a class by name."""
        parents = reversed(cls.__mro__[:-1])
        items = []
        for parent in parents:
            items.extend(self._registry.get(parent, []))
        return items


registry = Registry()

__all__ = ["registry", "RegistryItem"]
