# Copyright (C) 2012 - 2025  Christian Ledermann
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

from typing import TYPE_CHECKING

__all__ = ["Element"]

if TYPE_CHECKING:
    # fastkml treats lxml as the reference etree implementation for static
    # analysis (it is the preferred runtime backend, and its API is a
    # superset of xml.etree.ElementTree's); see fastkml.config.
    from lxml.etree import _Element as Element
else:
    from collections.abc import Iterable

    from typing_extensions import Protocol

    class Element(Protocol):
        """Protocol for Element."""

        tag: str
        text: str | None

        def set(self, tag: str, value: str) -> None:
            """Set the value of the tag."""

        def get(self, tag: str) -> str:
            """Get the value of the tag."""

        def find(self, tag: str) -> "Element | None":
            """Find the first element with the given tag."""

        def findall(self, tag: str) -> Iterable["Element"]:
            """Find all elements with the given tag."""

        def append(self, element: "Element") -> None:
            """Append an element to the current element."""

        def remove(self, element: "Element") -> None:
            """Remove an element from the current element."""
