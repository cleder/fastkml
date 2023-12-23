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
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

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


@dataclass(frozen=True)
class RegistryItem:
    """A registry item."""

    classes: Tuple[known_types, ...]
    attr_name: str
    node_name: Optional[str] = None
    iterable: bool = False


class Registry:
    """A registry of XML objects."""

    _registry: Dict[Type["_XMLObject"], List[RegistryItem]]

    def __init__(self) -> None:
        """Initialize the registry."""
        self._registry = {}

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
