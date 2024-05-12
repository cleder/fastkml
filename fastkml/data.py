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

https://developers.google.com/kml/documentation/extendeddata#example
"""
import logging
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from fastkml import config
from fastkml.base import _BaseObject
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
        """Create a string (c)representation for SimpleField."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"type={self.type}, "
            f"display_name={self.display_name!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.name) and bool(self.type)


registry.register(
    SimpleField,
    RegistryItem(
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
        """Create a string (c)representation for Schema."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"fields={self.fields!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def append(self, field: SimpleField) -> None:
        """Append a field."""
        self.fields.append(field)


registry.register(
    Schema,
    RegistryItem(
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
        attr_name="fields",
        node_name="SimpleField",
        classes=(SimpleField,),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


class Data(_BaseObject):
    """Represents an untyped name/value pair with optional display name."""

    _default_ns = config.KMLNS

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
        """Create a string (c)representation for Data."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"value={self.value!r}, "
            f"display_name={self.display_name!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.name) and self.value is not None


registry.register(
    Data,
    RegistryItem(
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
        """Create a string (c)representation for SimpleData."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"value={self.value!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.name) and self.value is not None


registry.register(
    SimpleData,
    RegistryItem(
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
        attr_name="name",
        node_name="name",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)


class SchemaData(_BaseObject):
    """
    <SchemaData schemaUrl="anyURI">
    This element is used in conjunction with <Schema> to add typed
    custom data to a KML Feature. The Schema element (identified by the
    schemaUrl attribute) declares the custom data type. The actual data
    objects ("instances" of the custom data) are defined using the
    SchemaData element.
    The <schemaURL> can be a full URL, a reference to a Schema ID defined
    in an external KML file, or a reference to a Schema ID defined
    in the same KML file.
    """

    _default_ns = config.KMLNS

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
        """Create a string (c)representation for SchemaData."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"schema_url={self.schema_url!r}, "
            f"data={self.data!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.data) and bool(self.schema_url)

    def append_data(self, data: SimpleData) -> None:
        self.data.append(data)


registry.register(
    SchemaData,
    RegistryItem(
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
        attr_name="data",
        node_name="SimpleData",
        classes=(SimpleData,),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


class ExtendedData(_BaseObject):
    """
    Represents a list of untyped name/value pairs. See docs:

    -> 'Adding Untyped Name/Value Pairs'
       https://developers.google.com/kml/documentation/extendeddata

    """

    _default_ns = config.KMLNS

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
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.elements = list(elements) if elements else []

    def __repr__(self) -> str:
        """Create a string (c)representation for ExtendedData."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"elements={self.elements!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.elements)


registry.register(
    ExtendedData,
    RegistryItem(
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
