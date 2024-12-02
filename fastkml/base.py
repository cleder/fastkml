# Copyright (C) 2012 - 2024 Christian Ledermann
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
Abstract XML base class.

The purpose of ``_XMLObject`` is to serve as a base class for KML objects in fastkml.
Its main functions are:

- Provide a common interface for XML serialization and deserialization.
- Handle namespace management for KML elements.
- Manage attribute storage and retrieval for derived classes.
- Provide the ``etree_element()`` method for converting objects to XML Elements.
- Facilitate integration with the registry system for flexible XML mapping.

By inheriting from ``_XMLObject``, KML classes gain these capabilities, ensuring
consistent handling of XML operations across the library.

"""

import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import cast

from typing_extensions import Self

from fastkml import config
from fastkml.enums import Verbosity
from fastkml.registry import registry
from fastkml.types import Element
from fastkml.validator import validate

logger = logging.getLogger(__name__)

__all__ = ["_XMLObject"]


class _XMLObject:
    """XML Baseclass."""

    _default_nsid: str = ""
    _node_name: str = ""
    name_spaces: Dict[str, str]
    __kwarg_keys: Tuple[str, ...]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the XML Object.

        Parameters
        ----------
        ns : Optional[str], default=None
            The namespace of the XML object.
        name_spaces : Optional[Dict[str, str]], default=None
            The dictionary of namespace prefixes and URIs.
        **kwargs : Any
            Additional keyword arguments.

        """
        name_spaces = name_spaces or {}
        self.name_spaces = {**config.NAME_SPACES, **name_spaces}
        self.ns: str = (
            self.name_spaces.get(self._default_nsid, "") if ns is None else ns
        )
        for arg, val in kwargs.items():
            setattr(self, arg, val)
        self.__kwarg_keys = tuple(kwargs.keys())

    def __repr__(self) -> str:
        """
        Create a string (c)representation for _XMLObject.

        Returns
        -------
        str
            The string representation of the object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __str__(self) -> str:
        """
        Return the string representation of the object.

        Returns
        -------
        str
            The string representation of the object.

        """
        return self.to_string()

    def __eq__(self, other: object) -> bool:
        """
        Compare two _XMLObject instances for equality.

        Parameters
        ----------
        other : object
            The object to compare with.

        Returns
        -------
        bool
            True if the objects are equal, False otherwise.

        """
        return self.__dict__ == other.__dict__ if type(self) is type(other) else False

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        """
        Return the KML Object as an Element.

        This method essentially converts the Python object to its XML representation,
        using the registry to determine how each attribute should be serialized.

        - Create an XML Element with the object's tag name and namespace.
        - Iterate through registered attributes for the object's class.
          For each attribute:
            - Call the corresponding set_element function. This function adds the
              attribute to the Element as a sub-element or attribute.
        - Handle different data types and nested objects.
        - Apply precision and verbosity settings if specified.
        - Return the complete Element tree representing the object.

        Parameters
        ----------
        precision : Optional[int], default=None
            The precision of the KML object.
        verbosity : Verbosity, default=Verbosity.normal
            The verbosity level.

        Returns
        -------
        Element
            The KML object as an Element.

        """
        element: Element = config.etree.Element(
            f"{self.ns}{self.get_tag_name()}",
        )
        for item in registry.get(self.__class__):
            item.set_element(
                obj=self,
                element=element,
                attr_name=item.attr_name,
                node_name=item.node_name,
                precision=precision,
                verbosity=verbosity,
                default=item.default,
            )
        return element

    def to_string(
        self,
        *,
        prettyprint: bool = True,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> str:
        """
        Return the KML Object as serialized xml.

        Parameters
        ----------
        prettyprint : bool, default=True
            Whether to pretty print the XML.
        precision : Optional[int], default=None
            The precision of the KML object.
        verbosity : Verbosity, default=Verbosity.normal
            The verbosity level.

        Returns
        -------
        str
            The KML object as serialized XML.

        """
        element = self.etree_element(
            precision=precision,
            verbosity=verbosity,
        )
        try:
            return cast(
                str,
                config.etree.tostring(
                    element,
                    encoding="unicode",
                    pretty_print=prettyprint,
                ),
            )
        except TypeError:
            return cast(
                str,
                config.etree.tostring(
                    element,
                    encoding="unicode",
                ),
            )

    def validate(self) -> Optional[bool]:
        """
        Validate the KML object against the XML schema.

        Returns
        -------
        Optional[bool]
            True if the object is valid, None if the XMLSchema is not available.

        Raises
        ------
        AssertionError
            If the object is not valid.

        """
        return validate(element=self.etree_element())

    def _get_splat(self) -> Dict[str, Any]:
        """
        Get the keyword arguments as a dictionary.

        Returns
        -------
        Dict[str, Any]
            The keyword arguments as a dictionary.

        """
        return {
            key: getattr(self, key)
            for key in self.__kwarg_keys
            if getattr(self, key) is not None
        }

    @classmethod
    def get_tag_name(cls) -> str:
        """
        Return the tag name.

        Returns
        -------
        str
            The tag name.

        """
        return cls.__name__

    @classmethod
    def _get_ns(cls, ns: Optional[str], name_spaces: Dict[str, str]) -> str:
        """
        Get the namespace.

        Parameters
        ----------
        ns : Optional[str]
            The namespace.
        name_spaces : Dict[str, str]
            The dictionary of namespace prefixes and URIs.

        Returns
        -------
        str
            The namespace.

        """
        return name_spaces.get(cls._default_nsid, "") if ns is None else ns

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        """
        Get the keyword arguments for the class constructor.

        A class method used for XML deserialization. Its main purposes are:

        - Extract attribute values from an XML element.
        - Convert these values into appropriate Python types.
        - Prepare a dictionary of keyword arguments for object initialization.
        - It is called during the parsing process to populate object attributes from XML
          data. The method uses the registry and helper functions to handle different
          attribute types and nested objects.

        Subclasses may override this method to add custom deserialization logic for
        specific KML elements, although this should be rare. Prefer registration over
        a custom ``_get_kwargs`` implementation to ensure consistent handling of KML:

        - Consistency: Ensures uniform handling across all KML elements.
        - Maintainability: Centralizes parsing logic, making updates easier.
        - Declarative approach: Simplifies code by moving logic to configuration.
        - Reusability: Allows sharing of parsing logic across different classes.
        - Separation of concerns: Keeps parsing logic separate from class definitions.
        - Extensibility: Makes it easier to add new attributes or change parsing
          behavior.
        - Reduced duplication: Avoids repeating similar parsing code in multiple
          classes.
        - Easier testing: Allows testing of parsing logic independently of class
          implementations.

        Parameters
        ----------
        ns : str
            The namespace.
        name_spaces : Optional[Dict[str, str]], default=None
            The dictionary of namespace prefixes and URIs.
        element : Element
            The XML element.
        strict : bool
            Whether to enforce strict parsing.

        Returns
        -------
        Dict[str, Any]
            The keyword arguments for the class constructor.

        """
        name_spaces = name_spaces or {}
        name_spaces = {**config.NAME_SPACES, **name_spaces}
        kwargs: Dict[str, Any] = {"ns": ns, "name_spaces": name_spaces}
        for item in registry.get(cls):
            for name_space in item.ns_ids:
                kwarg = item.get_kwarg(
                    element=element,
                    ns=name_spaces.get(name_space, ""),
                    name_spaces=name_spaces,
                    node_name=item.node_name,
                    kwarg=item.attr_name,
                    classes=item.classes,
                    strict=strict,
                )
                if kwarg:
                    kwargs.update(
                        kwarg,
                    )
                    break
        return kwargs

    @classmethod
    def class_from_element(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Self:
        """
        Create an XML object from an etree element.

        Parameters
        ----------
        ns : str
            The namespace.
        name_spaces : Optional[Dict[str, str]], default=None
            The dictionary of namespace prefixes and URIs.
        element : Element
            The XML element.
        strict : bool
            Whether to enforce strict parsing.

        Returns
        -------
        Self
            The XML object.

        """
        kwargs = cls._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        return cls(
            **kwargs,
        )

    @classmethod
    def from_string(
        cls,
        string: str,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        strict: bool = True,
    ) -> Self:
        """
        Create an XML object from a string.

        Parameters
        ----------
        string : str
            The string representation of the XML object.
        ns : Optional[str], default=None
            The namespace of the XML object.
        name_spaces : Optional[Dict[str, str]], default=None
            The dictionary of namespace prefixes and URIs.
        strict : bool, default=True
            Whether to enforce strict parsing.

        Returns
        -------
        Self
            The XML object.

        """
        name_spaces = name_spaces or {}
        name_spaces = {**config.NAME_SPACES, **name_spaces}
        ns = cls._get_ns(ns, name_spaces=name_spaces)
        return cls.class_from_element(
            ns=ns,
            name_spaces=name_spaces,
            strict=strict,
            element=cast(
                Element,
                config.etree.fromstring(string),
            ),
        )
