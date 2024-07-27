# Copyright (C) 2022 - 2024 Christian Ledermann
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
"""
Add Custom Data.

https://developers.google.com/kml/documentation/extendeddata
"""
import logging
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from fastkml.enums import DataType
from fastkml.exceptions import KMLSchemaError
from fastkml.helpers import attribute_enum_kwarg
from fastkml.helpers import attribute_text_kwarg
from fastkml.helpers import enum_attribute
from fastkml.helpers import node_text
from fastkml.helpers import node_text_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_attribute
from fastkml.helpers import text_subelement
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.kml_base import _BaseObject
from fastkml.registry import RegistryItem
from fastkml.registry import registry

__all__ = [
    "Data",
    "ExtendedData",
    "Schema",
    "SchemaData",
    "SimpleField",
]

logger = logging.getLogger(__name__)


class SimpleField(_BaseObject):
    """
    A SimpleField always has both name and type attributes.

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
    the Google Earth user. Use the [CDATA] element to escape standard
    HTML markup.
    """

    name: Optional[str]
    type: Optional[DataType]
    display_name: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[DataType] = None,
        display_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the Data class.

        Args:
        ----
            ns (Optional[str]): The namespace of the data.
            name_spaces (Optional[Dict[str, str]]):
                The dictionary of namespace prefixes and URIs.
            id (Optional[str]): The ID of the data.
            target_id (Optional[str]): The target ID of the data.
            name (Optional[str]): The name of the data.
            type (Optional[DataType]): The type of the data.
            display_name (Optional[str]): The display name of the data.
            **kwargs (Any): Additional keyword arguments.

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
        self.name = name
        self.type = type
        self.display_name = display_name

    def __repr__(self) -> str:
        """
        Return a string representation of the SimpleField object.

        Returns
        -------
            str: A string representation of the SimpleField object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"type={self.type}, "
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
        return bool(self.name) and bool(self.type)


registry.register(
    SimpleField,
    RegistryItem(
        ns_ids=("", "kml"),
        attr_name="name",
        node_name="name",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
registry.register(
    SimpleField,
    RegistryItem(
        ns_ids=("", "kml"),
        attr_name="type",
        node_name="type",
        classes=(DataType,),
        get_kwarg=attribute_enum_kwarg,
        set_element=enum_attribute,
    ),
)
registry.register(
    SimpleField,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="display_name",
        node_name="displayName",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)


class Schema(_BaseObject):
    """
    Specifies a custom KML schema that is used to add custom data to KML Features.

    The "id" attribute is required and must be unique within the KML file.
    <Schema> is always a child of <Document>.

    https://developers.google.com/kml/documentation/extendeddata#declare-the-schema-element

    """

    name: Optional[str]
    fields: List[SimpleField]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        fields: Optional[Iterable[SimpleField]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a Schema object.

        Parameters
        ----------
        ns : str, optional
            The namespace of the schema.
        name_spaces : dict[str, str], optional
            The dictionary of namespace prefixes and URIs.
        id : str, optional
            The unique identifier for the schema.
        target_id : str, optional
            The target identifier for the schema.
        name : str, optional
            The name of the schema.
        fields : Iterable[SimpleField], optional
            The list of fields in the schema.
        **kwargs : Any
            Additional keyword arguments.

        Raises
        ------
        KMLSchemaError
            If the id is not provided.

        """
        if id is None:
            msg = "Id is required for schema"
            raise KMLSchemaError(msg)
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.name = name
        self.fields = list(fields) if fields else []

    def __repr__(self) -> str:
        """
        Return a string representation of the Schema object.

        Returns
        -------
        str
            The string representation of the Schema object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"fields={self.fields!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def append(self, field: SimpleField) -> None:
        """
        Append a field to the schema.

        Parameters
        ----------
        field : SimpleField
            The field to be appended.

        """
        self.fields.append(field)


registry.register(
    Schema,
    RegistryItem(
        ns_ids=("", "kml"),
        attr_name="name",
        node_name="name",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
registry.register(
    Schema,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="fields",
        node_name="SimpleField",
        classes=(SimpleField,),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


class Data(_BaseObject):
    """Represents an untyped name/value pair with optional display name."""

    name: Optional[str]
    value: Optional[str]
    display_name: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        value: Optional[str] = None,
        display_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the Data class.

        Args:
        ----
            ns (Optional[str]): The namespace of the data.
            name_spaces (Optional[Dict[str, str]]):
                The dictionary of namespace prefixes and URIs.
            id (Optional[str]): The ID of the data.
            target_id (Optional[str]): The target ID of the data.
            name (Optional[str]): The name of the data.
            value (Optional[str]): The value of the data.
            display_name (Optional[str]): The display name of the data.
            **kwargs (Any): Additional keyword arguments.

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
        self.name = name
        self.value = value
        self.display_name = display_name

    def __repr__(self) -> str:
        """
        Create a string representation for Data.

        Returns
        -------
        str
            The string representation of the Data object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"value={self.value!r}, "
            f"display_name={self.display_name!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the Data object is truthy.

        Returns
        -------
        bool
            True if the Data object has a name and a non-None value, False otherwise.

        """
        return bool(self.name) and self.value is not None


registry.register(
    Data,
    RegistryItem(
        ns_ids=("", "kml"),
        attr_name="name",
        node_name="name",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)

registry.register(
    Data,
    RegistryItem(
        ns_ids=("", "kml"),
        attr_name="value",
        node_name="value",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    Data,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="display_name",
        node_name="displayName",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)


class SimpleData(_BaseObject):
    name: Optional[str]
    value: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a SimpleData object.

        Args:
        ----
            ns (Optional[str]): The namespace of the object.
            name_spaces (Optional[Dict[str, str]]):
                The dictionary of namespace prefixes and URIs.
            id (Optional[str]): The ID of the object.
            target_id (Optional[str]): The target ID of the object.
            name (Optional[str]): The name of the object.
            value (Optional[str]): The value of the object.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        """
        Return a string representation of the SimpleData object.

        Returns
        -------
            str: The string representation of the SimpleData object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"value={self.value!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the SimpleData object is truthy.

        Returns
        -------
            bool: True if the name and the value attribute are set, False otherwise.

        """
        return bool(self.name) and self.value is not None


registry.register(
    SimpleData,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="value",
        node_name="value",
        classes=(str,),
        get_kwarg=node_text_kwarg,
        set_element=node_text,
    ),
)
registry.register(
    SimpleData,
    RegistryItem(
        ns_ids=("", "kml"),
        attr_name="name",
        node_name="name",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)


class SchemaData(_BaseObject):
    """
    Represents the SchemaData element in KML.

    The SchemaData element is used in conjunction with Schema to add typed
    custom data to a KML Feature. The Schema element (identified by the
    schemaUrl attribute) declares the custom data type. The actual data
    objects ("instances" of the custom data) are defined using the
    SchemaData element.
    """

    schema_url: Optional[str]
    data: List[SimpleData]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        schema_url: Optional[str] = None,
        data: Optional[Iterable[SimpleData]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the Data class.

        Args:
        ----
            ns (Optional[str]): The namespace for the data.
            name_spaces (Optional[Dict[str, str]]):
                The dictionary of namespace prefixes and URIs.
            id (Optional[str]): The ID of the data.
            target_id (Optional[str]): The target ID of the data.
            schema_url (Optional[str]): The URL of the schema for the data.
            data (Optional[Iterable[SimpleData]]): The iterable of SimpleData objects.
            **kwargs (Any): Additional keyword arguments.

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
        self.schema_url = schema_url
        self.data = list(data) if data else []

    def __repr__(self) -> str:
        """Create a string representation for SchemaData."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"schema_url={self.schema_url!r}, "
            f"data={self.data!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the SchemaData object contains data.

        Returns
        -------
            bool: True if the SchemaData object contains data and a
                schema URL, False otherwise.

        """
        return bool(self.data) and bool(self.schema_url)

    def append_data(self, data: SimpleData) -> None:
        """
        Append a SimpleData object to the SchemaData.

        Args:
        ----
            data (SimpleData): The SimpleData object to be appended.

        """
        self.data.append(data)


registry.register(
    SchemaData,
    RegistryItem(
        ns_ids=("", "kml"),
        attr_name="schema_url",
        node_name="schemaUrl",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
registry.register(
    SchemaData,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="data",
        node_name="SimpleData",
        classes=(SimpleData,),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


class ExtendedData(_BaseObject):
    """Represents a list of untyped name/value pairs."""

    elements: List[Union[Data, SchemaData]]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        elements: Optional[Iterable[Union[Data, SchemaData]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the Data class.

        Args:
        ----
            ns (Optional[str]): The namespace for the data.
            name_spaces (Optional[Dict[str, str]]):
                The dictionary of namespace prefixes and URIs.
            id (Optional[str]): The ID of the data.
            target_id (Optional[str]): The target ID of the data.
            elements (Optional[Iterable[Union[Data, SchemaData]]]):
                The iterable of data elements.
            **kwargs (Any): Additional keyword arguments.

        Returns:
        -------
            - None

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.elements = list(elements) if elements else []

    def __repr__(self) -> str:
        """
        Return a string representation of the ExtendedData object.

        Returns
        -------
            str: A string representation of the ExtendedData object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"elements={self.elements!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the object has any elements.

        Returns
        -------
        bool
            True if the object has elements, False otherwise.

        """
        return bool(self.elements)


registry.register(
    ExtendedData,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="elements",
        node_name="Data,SchemaData",
        classes=(
            Data,
            SchemaData,
        ),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)
