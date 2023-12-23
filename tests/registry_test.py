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

from fastkml.base import _XMLObject
from fastkml.registry import Registry
from fastkml.registry import RegistryItem


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


def test_registry_get_root() -> None:
    """Test the registry when getting the root class."""
    registry = Registry()
    registry.register(A, RegistryItem((A,), "a"))
    assert registry.get(A) == [RegistryItem((A,), "a")]


def test_registry_get() -> None:
    """Test the registry."""
    registry = Registry()
    registry.register(A, RegistryItem((A,), "a"))
    registry.register(B, RegistryItem((B,), "b"))
    registry.register(C, RegistryItem((C,), "c"))
    registry.register(D, RegistryItem((D,), "d"))
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
    registry.register(A, RegistryItem((A,), "a"))
    registry.register(B, RegistryItem((B,), "b"))
    registry.register(C, RegistryItem((C,), "c"))
    registry.register(D, RegistryItem((D,), "d"))
    registry.register(A, RegistryItem((int,), "int"))
    registry.register(B, RegistryItem((bool,), "bool"))
    registry.register(C, RegistryItem((float,), "float"))
    registry.register(D, RegistryItem((Enum,), "enum"))
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
