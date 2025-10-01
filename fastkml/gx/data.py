# Copyright (C) 2024 Christian Ledermann
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

"""GX SimpleArrayData and SimpleArrayField Extension."""

from collections.abc import Iterable
from typing import Any
from typing import Optional

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.enums import DataType
from fastkml.helpers import attribute_enum_kwarg
from fastkml.helpers import attribute_text_kwarg
from fastkml.helpers import clean_string
from fastkml.helpers import enum_attribute
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import subelement_text_list_kwarg
from fastkml.helpers import text_attribute
from fastkml.helpers import text_subelement_kml
from fastkml.helpers import text_subelement_list
from fastkml.kml_base import _BaseObject
from fastkml.registry import RegistryItem
from fastkml.registry import registry

__all__ = ["SimpleArrayData", "SimpleArrayField"]


class SimpleArrayField(_XMLObject):
    """
    A SimpleArrayField always has both name and type attributes.

    The declaration of the custom field, must specify both the type
    and the name of this field.
    If either the type or the name is omitted, the field is ignored.

    The type can be one of the following:
     - string
     - int
     - uint
     - short
     - ushort
     - float
     - double
     - bool

    The displayName, if any, to be used when the field name is displayed to
    the Google Earth user.
    """

    _default_nsid = config.GX

    name: Optional[str]
    type_: Optional[DataType]
    display_name: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        name: Optional[str] = None,
        type_: Optional[DataType] = None,
        display_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the SimpleArrayField class.

        Args:
        ----
            ns (Optional[str]): The namespace of the data.
            name_spaces (Optional[Dict[str, str]]):
                The dictionary of namespace prefixes and URIs.
            name (Optional[str]): The name of the data.
            type_ (Optional[DataType]): The type of the data.
            display_name (Optional[str]): The display name of the data.
            **kwargs (Any): Additional keyword arguments.

        Returns:
        -------
            None

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )
        self.name = clean_string(name)
        self.type_ = type_ or None
        self.display_name = clean_string(display_name)

    def __repr__(self) -> str:
        """
        Return a string representation of the SimpleArrayField object.

        Returns
        -------
            str: A string representation of the SimpleArrayField object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"name={self.name!r}, "
            f"type_={self.type_}, "
            f"display_name={self.display_name!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the object is considered True or False.

        Returns
        -------
            bool: True if both the name and type are non-empty, False otherwise.

        """
        return bool(self.name) and bool(self.type_)


registry.register(
    SimpleArrayField,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="display_name",
        node_name="displayName",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement_kml,
    ),
)
registry.register(
    SimpleArrayField,
    RegistryItem(
        ns_ids=("", "gx"),
        attr_name="name",
        node_name="name",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
registry.register(
    SimpleArrayField,
    RegistryItem(
        ns_ids=("", "gx"),
        attr_name="type_",
        node_name="type",
        classes=(DataType,),
        get_kwarg=attribute_enum_kwarg,
        set_element=enum_attribute,
    ),
)


class SimpleArrayData(_BaseObject):
    """
    A SimpleArrayData element.

    This element is used to define an array of string values. It is used in
    conjunction with the gx:SimpleArrayField element to specify how the array
    values are to be displayed.
    """

    _default_nsid = config.GX
    name: Optional[str]
    data: list[Optional[str]]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        data: Optional[Iterable[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the SimpleArrayData class.

        Args:
        ----
            ns (Optional[str]): The namespace for the data.
            name_spaces (Optional[Dict[str, str]]):
                The dictionary of namespace prefixes and URIs.
            id (Optional[str]): The ID of the data.
            target_id (Optional[str]): The target ID of the data.
            name (Optional[str]): The name of the object.
            data (Optional[Iterable[str]]): The iterable of values.
            **kwargs: Additional keyword arguments.

        Returns:
        -------
            None

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.data = [clean_string(d) for d in data] if data is not None else []
        self.name = clean_string(name)

    def __repr__(self) -> str:
        """
        Return a string representation of the SimpleArrayData object.

        Returns
        -------
            str: The string representation of the SimpleArrayData object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"data={self.data!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the object is considered True or False.

        Returns
        -------
            bool: True if both the name and data are non-empty, False otherwise.

        """
        return bool(self.data) and bool(self.name)


registry.register(
    SimpleArrayData,
    RegistryItem(
        ns_ids=("gx", ""),
        classes=(str,),
        attr_name="data",
        node_name="value",
        get_kwarg=subelement_text_list_kwarg,
        set_element=text_subelement_list,
    ),
)
registry.register(
    SimpleArrayData,
    RegistryItem(
        ns_ids=("", "gx"),
        classes=(str,),
        attr_name="name",
        node_name="name",
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
