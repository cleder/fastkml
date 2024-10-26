"""Fastkml utility functions."""

from typing import Any
from typing import Generator
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union


def has_attribute_values(obj: object, **kwargs: Any) -> bool:
    """
    Check if an object has the given attribute values.

    Args:
        obj: The object to check.
        **kwargs: Attributes of the object to match.

    Returns:
        True if the object has the given attribute values, False otherwise.

    """
    try:
        for key, value in kwargs.items():
            if getattr(obj, key) != value:
                return False
    except AttributeError:
        return False
    return True


def find_all(
    obj: object,
    *,
    of_type: Optional[Union[Type[object], Tuple[Type[object], ...]]] = None,
    **kwargs: Any,
) -> Generator[object, None, None]:
    """
    Find all instances of a given type in a given object.

    Args:
        obj: The object to search.
        of_type: The type(s) to search for or None for any type.
        **kwargs: Attributes of the object to match.

    Returns:
        An iterable of all instances of the given type in the given object.

    """
    if of_type is None or isinstance(obj, of_type):
        if has_attribute_values(obj, **kwargs):
            yield obj
    else:
        try:
            attrs = [attr for attr in obj.__dict__ if not attr.startswith("_")]
        except AttributeError:
            return
        for attr_name in attrs:
            attr = getattr(obj, attr_name)
            if callable(attr):
                continue
            if attr is obj:
                continue
            try:
                for item in attr:
                    yield from find_all(item, of_type=of_type, **kwargs)
            except TypeError:
                yield from find_all(attr, of_type=of_type, **kwargs)
