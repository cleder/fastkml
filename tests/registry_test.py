# Copyright (C) 2023  Christian Ledermann
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
"""Test the registry module."""
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from fastkml.base import _XMLObject
from fastkml.enums import Verbosity
from fastkml.registry import Registry
from fastkml.registry import RegistryItem
from fastkml.types import Element

known_types = Union[
    Type[_XMLObject],
    Type[Enum],
    Type[bool],
    Type[int],
    Type[str],
    Type[float],
]


class A(_XMLObject):
    """A test class."""


class B(A):
    """B test class."""


class C(B):
    """C test class."""


class Mixin:
    """A test mixin."""


class D(Mixin, C):
    """D test class."""


def set_element(
    obj: _XMLObject,
    *,
    element: Element,
    attr_name: str,
    node_name: str,
    precision: Optional[int],
    verbosity: Optional[Verbosity],
) -> None:
    """Get an attribute from an XML object."""


def get_kwarg(  # type: ignore[empty-body]
    *,
    element: Element,
    ns: str,
    name_spaces: Dict[str, str],
    node_name: str,
    kwarg: str,
    classes: Tuple[known_types, ...],
    strict: bool,
) -> Dict[str, Any]:
    """Get the kwarg for the constructor from the element."""


def test_registry_get_root() -> None:
    """Test the registry when getting the root class."""
    registry = Registry()
    registry.register(
        A,
        RegistryItem(
            ns_ids=("kml",),
            classes=(A,),
            attr_name="a",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="a",
        ),
    )

    assert registry.get(A)[0].attr_name == "a"


def test_registry_get() -> None:
    """Test the registry."""
    registry = Registry()
    registry.register(
        A,
        RegistryItem(
            ns_ids=("kml",),
            classes=(A,),
            attr_name="a",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="a",
        ),
    )
    registry.register(
        B,
        RegistryItem(
            ns_ids=("kml",),
            classes=(B,),
            attr_name="b",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="b",
        ),
    )
    registry.register(
        C,
        RegistryItem(
            ns_ids=("kml",),
            classes=(C,),
            attr_name="c",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="c",
        ),
    )
    registry.register(
        D,
        RegistryItem(
            ns_ids=("kml",),
            classes=(D,),
            attr_name="d",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="d",
        ),
    )
    d = D()

    assert isinstance(d, D)
    assert isinstance(d, A)
    assert len(registry.get(A)) == 1
    assert len(registry.get(B)) == 2
    assert len(registry.get(C)) == 3
    assert len(registry.get(D)) == 4
    assert registry.get(D)[0].classes == (A,)
    assert registry.get(D)[1].classes == (B,)
    assert registry.get(D)[2].classes == (C,)
    assert registry.get(D)[3].classes == (D,)


def test_registry_get_multi() -> None:
    """Test the registry with multiple classes."""
    registry = Registry()
    registry.register(
        A,
        RegistryItem(
            ns_ids=("kml",),
            classes=(A,),
            attr_name="a",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="a",
        ),
    )
    registry.register(
        B,
        RegistryItem(
            ns_ids=("kml",),
            classes=(B,),
            attr_name="b",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="b",
        ),
    )
    registry.register(
        C,
        RegistryItem(
            ns_ids=("kml",),
            classes=(C,),
            attr_name="c",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="c",
        ),
    )
    registry.register(
        D,
        RegistryItem(
            ns_ids=("kml",),
            classes=(D,),
            attr_name="d",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="d",
        ),
    )
    registry.register(
        A,
        RegistryItem(
            ns_ids=("kml",),
            classes=(int,),
            attr_name="int",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="int",
        ),
    )
    registry.register(
        B,
        RegistryItem(
            ns_ids=("kml",),
            classes=(bool,),
            attr_name="bool",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="bool",
        ),
    )
    registry.register(
        C,
        RegistryItem(
            ns_ids=("kml",),
            classes=(float,),
            attr_name="float",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="float",
        ),
    )
    registry.register(
        D,
        RegistryItem(
            ns_ids=("kml",),
            classes=(Enum,),
            attr_name="enum",
            get_kwarg=get_kwarg,
            set_element=set_element,
            node_name="enum",
        ),
    )

    assert len(registry.get(A)) == 2
    assert len(registry.get(D)) == 8
    assert registry.get(D)[0].classes == (A,)
    assert registry.get(D)[1].classes == (int,)
    assert registry.get(D)[2].classes == (B,)
    assert registry.get(D)[3].classes == (bool,)
    assert registry.get(D)[4].classes == (C,)
    assert registry.get(D)[5].classes == (float,)
    assert registry.get(D)[6].classes == (D,)
    assert registry.get(D)[7].classes == (Enum,)


def test_registry_repr() -> None:
    registry = Registry()

    assert repr(registry) == "fastkml.registry.Registry({})"
