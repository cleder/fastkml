"""Introspection utilities."""
# flake8: noqa
import collections.abc
import enum
import inspect
import typing
from types import ModuleType

from fastkml import views
from fastkml.base import _XMLObject


def get_init_args_with_annotations(cls: type):  # type: ignore[no-untyped-def]
    """Get the arguments of a class's __init__ method with type annotations."""
    subclass_init_signature = inspect.signature(cls.__init__)  # type: ignore[misc]
    base_init_signature = inspect.signature(cls.__bases__[-1].__init__)  # type: ignore[misc]

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


def extract_types(annotation: typing.Type):  # type: ignore[type-arg,no-untyped-def]
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


def get_type_hints(cls: typing.Type):  # type: ignore[type-arg,no-untyped-def]
    """Get the type hints for a class."""
    return {k: extract_types(v) for k, v in get_init_args_with_annotations(cls).items()}


def is_class_in_module(cls: type, module: ModuleType) -> bool:
    """
    Check if a class is defined in a specific module.

    Args:
    ----
        cls (type): The class to check.
        module (ModuleType): The module to compare against.

    Returns:
    -------
        bool: True if the class is defined in the specified module,
              False if it is imported.
    """
    return inspect.getmodule(cls) == module


def get_classes_in_module(module: ModuleType) -> typing.List[type]:
    """
    Get all classes defined in a module.

    Args:
    ----
        module (ModuleType): The module to check.

    Returns:
    -------
        typing.List[type]: A list of classes defined in the module.
    """
    return [
        cls
        for name, cls in inspect.getmembers(module, inspect.isclass)
        if is_class_in_module(cls, module)
    ]


def create_registry(module: ModuleType) -> None:
    """
    Create a registry of classes defined in a module.

    Args:
    ----
        module (ModuleType): The module to check.

    """
    attr_cls_dict = {
        bool: {
            "get_kwarg": "subelement_bool_kwarg",
            "set_element": "bool_subelement",
        },
        str: {
            "get_kwarg": "subelement_text_kwarg",
            "set_element": "text_subelement",
        },
        int: {
            "get_kwarg": "subelement_int_kwarg",
            "set_element": "int_subelement",
        },
        float: {
            "get_kwarg": "subelement_float_kwarg",
            "set_element": "float_subelement",
        },
    }
    print("from fastkml.registry import registry, RegistryItem")
    print()
    for cls in get_classes_in_module(module):
        if not issubclass(cls, _XMLObject):
            continue
        print(f"###  {cls.__name__} ###")
        hints = get_type_hints(cls)
        for k, v in hints.items():
            print("registry.register(")
            print(f"    {cls.__name__},")
            print("    RegistryItem(")
            print(f"        attr_name='{k}',")
            print(f"        node_name='${k},")
            if isinstance(v[0], dict):
                try:
                    classes = ", ".join([c.__name__ for c in v[0]["Iterable"]])
                except AttributeError:
                    print(f"# XXX: Error in {cls.__name__}: {k} > {v}")
                print(f"        classes=({classes},),")
                print("        get_kwarg=xml_subelement_kwarg,")
                print("        set_element=xml_subelement_list,")

                print("    ),")
                print(")")
                continue
            try:
                classes = ", ".join([c.__name__ for c in v])
                print(f"        classes=({classes},),")
            except AttributeError:
                print(f"# XXX: Error in {cls.__name__}: {k} > {v}")
            try:
                for k, v in attr_cls_dict[v[0]].items():
                    print(f"        {k}={v},")
            except KeyError:
                if issubclass(v[0], enum.Enum):
                    print("        get_kwarg=subelement_enum_kwarg,")
                    print("        set_element=enum_subelement,")
                elif issubclass(v[0], _XMLObject):
                    print("        get_kwarg=xml_subelement_kwarg,")
                    print("        set_element=xml_subelement,")
                else:
                    print(f"# XXX Need to add support for {v[0]}")

            print("    ),")
            print(")")
        print()


if __name__ == "__main__":
    create_registry(views)
