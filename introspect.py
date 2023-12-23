"""Introspection utilities."""
import collections.abc
import inspect
import typing


def get_init_args_with_annotations(cls: type):
    """Get the arguments of a class's __init__ method with type annotations."""
    subclass_init_signature = inspect.signature(cls.__init__)
    base_init_signature = inspect.signature(cls.__bases__[-1].__init__)

    # Extract parameter names and type annotations
    base_init_params = {
        param.name: param.annotation
        for param in base_init_signature.parameters.values()
    }
    subclass_init_params = {
        param.name: param.annotation
        for param in subclass_init_signature.parameters.values()
    }

    # Exclude arguments of baseclass from subclass
    subclass_init_params = {
        k: v for k, v in subclass_init_params.items() if k not in base_init_params
    }

    return subclass_init_params


def extract_types(annotation: typing.Type):
    try:
        origin = annotation.__origin__
    except AttributeError:
        return annotation
    if origin is typing.Union:
        return tuple(
            t
            for t in (
                extract_types(subtype)
                for subtype in annotation.__args__
                if subtype is not None
            )
            if t is not type(None)
        )
    elif origin is typing.Iterable or origin is collections.abc.Iterable:
        iterables = extract_types(annotation.__args__[0])
        return (
            {"Iterable": iterables}
            if type(iterables) is tuple
            else {"Iterable": (iterables,)}
        )
    elif origin is typing.Optional:
        return extract_types(annotation.__args__[0])


def get_type_hints(cls: typing.Type):
    """Get the type hints for a class."""
    return {k: extract_types(v) for k, v in get_init_args_with_annotations(cls).items()}
