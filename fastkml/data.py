# Copyright (C) 2022 - 2023  Christian Ledermann
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
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.base import _XMLObject
from fastkml.enums import DataType
from fastkml.enums import Verbosity
from fastkml.exceptions import KMLSchemaError
from fastkml.types import Element

__all__ = [
    "Data",
    "ExtendedData",
    "Schema",
    "SchemaData",
    "SimpleField",
]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SimpleField:
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

    name: str
    type: DataType
    display_name: Optional[str] = None


class Schema(_BaseObject):
    """
    Specifies a custom KML schema that is used to add custom data to KML Features.

    The "id" attribute is required and must be unique within the KML file.
    <Schema> is always a child of <Document>.

    https://developers.google.com/kml/documentation/extendeddata#declare-the-schema-element

    """

    __name__ = "Schema"

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        fields: Optional[Iterable[SimpleField]] = None,
    ) -> None:
        if id is None:
            msg = "Id is required for schema"
            raise KMLSchemaError(msg)
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.name = name
        self._simple_fields = list(fields) if fields else []

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name}, "
            f"fields={self.simple_fields!r}"
            ")"
        )

    @property
    def simple_fields(self) -> Tuple[SimpleField, ...]:
        return tuple(self._simple_fields)

    @simple_fields.setter
    def simple_fields(self, fields: Iterable[SimpleField]) -> None:
        self._simple_fields = list(fields)

    def append(self, field: SimpleField) -> None:
        """Append a field."""
        self._simple_fields.append(field)

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.name:
            element.set("name", self.name)
        for simple_field in self.simple_fields:
            sf = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}SimpleField",
            )
            sf.set("type", simple_field.type.value)
            sf.set("name", simple_field.name)
            if simple_field.display_name:
                dn = config.etree.SubElement(  # type: ignore[attr-defined]
                    sf,
                    f"{self.ns}displayName",
                )
                dn.text = simple_field.display_name
        return element

    @classmethod
    def _get_fields_kwargs_from_element(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> List[SimpleField]:
        def get_display_name(field: Element) -> Optional[str]:
            display_name = field.find(f"{ns}displayName")
            return display_name.text if display_name is not None else None

        return [
            SimpleField(
                name=field.get("name"),
                type=DataType(field.get("type")),
                display_name=get_display_name(field),
            )
            for field in element.findall(f"{ns}SimpleField")
            if field is not None
        ]

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs["name"] = element.get("name")
        kwargs["fields"] = cls._get_fields_kwargs_from_element(
            ns=ns,
            element=element,
            strict=strict,
        )
        return kwargs


class Data(_XMLObject):
    """Represents an untyped name/value pair with optional display name."""

    __name__ = "Data"

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        value: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)

        self.name = name
        self.value = value
        self.display_name = display_name

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns='{self.ns}',"
            f"name='{self.name}', value='{self.value}'"
            f"display_name='{self.display_name}')"
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        element.set("name", self.name or "")
        value = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}value",
        )
        value.text = self.value
        if self.display_name:
            display_name = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}displayName",
            )
            display_name.text = self.display_name
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs["name"] = element.get("name")
        value = element.find(f"{ns}value")
        if value is not None:
            kwargs["value"] = value.text
        display_name = element.find(f"{ns}displayName")
        if display_name is not None:
            kwargs["display_name"] = display_name.text
        return kwargs


@dataclass(frozen=True)
class SimpleData:
    name: str
    value: Union[int, str, float, bool]


class SchemaData(_XMLObject):
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

    __name__ = "SchemaData"

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        schema_url: Optional[str] = None,
        data: Optional[Iterable[SimpleData]] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        if (not isinstance(schema_url, str)) or (not schema_url):
            msg = "required parameter schema_url missing"
            raise ValueError(msg)
        self.schema_url = schema_url
        self._data = list(data) if data else []

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns='{self.ns}',"
            f"schema_url='{self.schema_url}', "
            f"data='{self.data}')"
        )

    @property
    def data(self) -> Tuple[SimpleData, ...]:
        return tuple(self._data)

    @data.setter
    def data(self, data: Iterable[SimpleData]) -> None:
        self._data = list(data)

    def append_data(self, data: SimpleData) -> None:
        self._data.append(data)

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        element.set("schemaUrl", self.schema_url)
        for data in self.data:
            sd = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}SimpleData",
            )
            sd.set("name", data.name)
            sd.text = data.value
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs["schema_url"] = element.get("schemaUrl")
        kwargs["data"] = [
            SimpleData(name=sd.get("name"), value=sd.text)
            for sd in element.findall(f"{ns}SimpleData")
            if sd is not None
        ]
        return kwargs


class ExtendedData(_XMLObject):
    """
    Represents a list of untyped name/value pairs. See docs:

    -> 'Adding Untyped Name/Value Pairs'
       https://developers.google.com/kml/documentation/extendeddata

    """

    __name__ = "ExtendedData"

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        elements: Optional[Iterable[Union[Data, SchemaData]]] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.elements = elements or []

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns='{self.ns}',"
            f"elements='{self.elements}')"
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        for subelement in self.elements:
            element.append(subelement.etree_element())
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        elements = []
        untyped_data = element.findall(f"{ns}Data")
        for ud in untyped_data:
            el_data = Data.class_from_element(ns=ns, element=ud, strict=strict)
            elements.append(el_data)
        typed_data = element.findall(f"{ns}SchemaData")
        for sd in typed_data:
            el_schema_data = SchemaData.class_from_element(
                ns=ns,
                element=sd,
                strict=strict,
            )
            elements.append(el_schema_data)
        kwargs["elements"] = elements
        return kwargs
