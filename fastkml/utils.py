"""Fastkml utility functions."""

from typing import Any
from typing import Generator
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

__all__ = ["find", "find_all", "has_attribute_values"]


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
        try:
            yield from attr
        except TypeError:
            yield attr


def find_all(
    obj: object,
    *,
    of_type: Optional[Union[Type[object], Tuple[Type[object], ...]]] = None,
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


def find(
    obj: object,
    *,
    of_type: Optional[Union[Type[object], Tuple[Type[object], ...]]] = None,
    **kwargs: Any,
) -> Optional[object]:
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
