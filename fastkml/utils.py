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
"""Fastkml utility functions."""

from collections.abc import Generator
from typing import Any
from typing import TypeVar
from typing import overload

__all__ = ["find", "find_all", "has_attribute_values"]

_T = TypeVar("_T")


def has_attribute_values(obj: object, **kwargs: Any) -> bool:
    """
    Check if an object has all of the given attribute values.

    Args:
    ----
        obj: The object to check.
        **kwargs: Attributes of the object to match.

    Returns:
    -------
        True if the object has the given attribute values, False otherwise.

    """
    try:
        return all(getattr(obj, key) == value for key, value in kwargs.items())
    except AttributeError:
        return False


def get_all_attrs(obj: object) -> Generator[object, None, None]:
    """
    Get all attributes of an object.

    Args:
    ----
        obj: The object to get attributes from.

    Returns:
    -------
        An iterable of all attributes of the object or, if the attribute itself is
            iterable, iterate over the attribute values.

    """
    try:
        attrs = (attr for attr in obj.__dict__ if not attr.startswith("_"))
    except AttributeError:
        return
    for attr_name in attrs:
        attr = getattr(obj, attr_name)
        if isinstance(attr, str):
            continue
        try:
            yield from attr
        except TypeError:
            yield attr


@overload
def find_all(
    obj: object,
    *,
    of_type: type[_T],
    **kwargs: Any,
) -> Generator[_T, None, None]: ...
@overload
def find_all(
    obj: object,
    *,
    of_type: tuple[type[_T], ...],
    **kwargs: Any,
) -> Generator[_T, None, None]: ...
@overload
def find_all(
    obj: object,
    *,
    of_type: None = None,
    **kwargs: Any,
) -> Generator[object, None, None]: ...
def find_all(
    obj: object,
    *,
    of_type: type[object] | tuple[type[object], ...] | None = None,
    **kwargs: Any,
) -> Generator[object, None, None]:
    """
    Find all instances of a given type with attributes matching the kwargs.

    Args:
    ----
        obj: The object to search.
        of_type: The type(s) to search for or None for any type.
        **kwargs: Attributes of the object to match.

    Returns:
    -------
        An iterable of all instances of the given type in the given object.

    """
    if (of_type is None or isinstance(obj, of_type)) and has_attribute_values(
        obj,
        **kwargs,
    ):
        yield obj

    for attr in get_all_attrs(obj):
        yield from find_all(attr, of_type=of_type, **kwargs)


@overload
def find(
    obj: object,
    *,
    of_type: type[_T],
    **kwargs: Any,
) -> _T | None: ...
@overload
def find(
    obj: object,
    *,
    of_type: tuple[type[_T], ...],
    **kwargs: Any,
) -> _T | None: ...
@overload
def find(
    obj: object,
    *,
    of_type: None = None,
    **kwargs: Any,
) -> object | None: ...
def find(
    obj: object,
    *,
    of_type: type[object] | tuple[type[object], ...] | None = None,
    **kwargs: Any,
) -> object | None:
    """
    Find the first instance of a given type in a given object.

    Args:
    ----
        obj: The object to search.
        of_type: The type(s) to search for or None for any type.
        **kwargs: Attributes of the object to match.

    Returns:
    -------
        The first instance of the given type in the given object or None if not found.

    """
    return next(find_all(obj, of_type=of_type, **kwargs), None)
