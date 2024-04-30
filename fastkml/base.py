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

"""Abstract base classes."""
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

logger = logging.getLogger(__name__)


class _XMLObject:
    """XML Baseclass."""

    _default_ns: str = ""
    _node_name: str = ""
    name_spaces: Dict[str, str]
    __kwarg_keys: Tuple[str, ...]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the XML Object."""
        self.ns: str = self._default_ns if ns is None else ns
        name_spaces = name_spaces or {}
        self.name_spaces = {**config.NAME_SPACES, **name_spaces}
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
        self.__kwarg_keys = tuple(kwargs.keys())

    def __repr__(self) -> str:
        """Create a string (c)representation for _XMLObject."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __str__(self) -> str:
        return self.to_string()

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, type(self))
        return self.ns == other.ns and self.name_spaces == other.name_spaces

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        """Return the KML Object as an Element."""
        element: Element = config.etree.Element(  # type: ignore[attr-defined]
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
            )
        return element

    def to_string(
        self,
        *,
        prettyprint: bool = True,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> str:
        """Return the KML Object as serialized xml."""
        element = self.etree_element(
            precision=precision,
            verbosity=verbosity,
        )
        try:
            return cast(
                str,
                config.etree.tostring(  # type: ignore[attr-defined]
                    element,
                    encoding="UTF-8",
                    pretty_print=prettyprint,
                ).decode(
                    "UTF-8",
                ),
            )
        except TypeError:
            return cast(
                str,
                config.etree.tostring(  # type: ignore[attr-defined]
                    element,
                    encoding="UTF-8",
                ).decode(
                    "UTF-8",
                ),
            )

    def _get_splat(self) -> Dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in self.__kwarg_keys
            if getattr(self, key) is not None
        }

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return cls.__name__

    @classmethod
    def _get_ns(cls, ns: Optional[str]) -> str:
        return cls._default_ns if ns is None else ns

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        """Returns a dictionary of kwargs for the class constructor."""
        name_spaces = name_spaces or {}
        name_spaces = {**config.NAME_SPACES, **name_spaces}
        kwargs: Dict[str, Any] = {"ns": ns, "name_spaces": name_spaces}
        for item in registry.get(cls):
            kwargs.update(
                item.get_kwarg(
                    element=element,
                    ns=ns,
                    name_spaces=name_spaces,
                    node_name=item.node_name,
                    kwarg=item.attr_name,
                    classes=item.classes,
                    strict=strict,
                ),
            )
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
        """Creates an XML object from an etree element."""
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
    def class_from_string(
        cls,
        string: str,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        strict: bool = True,
    ) -> Self:
        """
        Creates a geometry object from a string.

        Args:
        ----
            string: String representation of the geometry object

        Returns:
        -------
            Geometry object

        """
        ns = cls._get_ns(ns)
        return cls.class_from_element(
            ns=ns,
            name_spaces=name_spaces,
            strict=strict,
            element=cast(
                Element,
                config.etree.fromstring(string),  # type: ignore[attr-defined]
            ),
        )


class _BaseObject(_XMLObject):
    """
    Base class for all KML objects.

    This is an abstract base class and cannot be used directly in a
    KML file. It provides the id attribute, which allows unique
    identification of a KML element, and the targetId attribute,
    which is used to reference objects that have already been loaded into
    Google Earth. The id attribute must be assigned if the <Update>
    mechanism is to be used.
    """

    _default_ns = config.KMLNS

    id = None
    target_id = None

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the KML Object."""
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.id = id
        self.target_id = target_id

    def __repr__(self) -> str:
        """Create a string (c)representation for _BaseObject."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"**kwargs={self._get_splat()!r},"
            ")"
        )

    def __eq__(self, other: object) -> bool:
        """Return True if the two objects are equal."""
        try:
            assert isinstance(other, type(self))
            return (
                super().__eq__(other)
                and self.id == other.id
                and self.target_id == other.target_id
            )
        except AssertionError:
            return False

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        """Return the KML Object as an Element."""
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.id:
            element.set("id", self.id)
        if self.target_id:
            element.set("targetId", self.target_id)
        return element

    @classmethod
    def _get_id(cls, element: Element, strict: bool) -> str:
        return element.get("id") or ""

    @classmethod
    def _get_target_id(cls, element: Element, strict: bool) -> str:
        return element.get("targetId") or ""

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        """Get the keyword arguments to build the object from an element."""
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs.update(
            {
                "id": cls._get_id(element=element, strict=strict),
                "target_id": cls._get_target_id(element=element, strict=strict),
            },
        )
        return kwargs
