# Copyright (C) 2012 - 2022  Christian Ledermann
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
"""Types for fastkml."""
from typing import Iterable
from typing import Optional

from typing_extensions import Protocol

__all__ = ["Element"]


class Element(Protocol):
    """Protocol for Element."""

    tag: str
    text: str

    def set(self, tag: str, value: str) -> None:
        """Set the value of the tag."""

    def get(self, tag: str) -> str:
        """Get the value of the tag."""

    def find(self, tag: str) -> Optional["Element"]:
        """Find the first element with the given tag."""

    def findall(self, tag: str) -> Iterable["Element"]:
        """Find all elements with the given tag."""

    def append(self, element: "Element") -> None:
        """Append an element to the current element."""

    def remove(self, element: "Element") -> None:
        """Remove an element from the current element."""
