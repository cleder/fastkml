# Copyright (C) 2024 Rishit Chaudhary, Christian Ledermann
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
"""Test the helper functions edge cases."""
from enum import Enum
from typing import Callable
from unittest.mock import Mock
from unittest.mock import patch

from fastkml.helpers import attribute_enum_kwarg
from fastkml.helpers import attribute_float_kwarg
from fastkml.helpers import subelement_bool_kwarg
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import subelement_int_kwarg
from tests.base import StdLibrary


class Node:
    text: str


class Color(Enum):
    RED = 1


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_subelement_int_kwarg(self) -> None:
        node = Node()
        node.text = ""
        element = Mock()
        element.find.return_value = node
        res = subelement_int_kwarg(
            element=element,
            ns="ns",
            name_spaces={"name": "uri"},
            node_name="node",
            kwarg="kwarg",
            classes=(int,),
            strict=False,
        )
        assert res == {}

    def test_subelement_float_kwarg(self) -> None:
        node = Node()
        node.text = ""
        element = Mock()
        element.find.return_value = node
        res = subelement_float_kwarg(
            element=element,
            ns="ns",
            name_spaces={"name": "uri"},
            node_name="node",
            kwarg="kwarg",
            classes=(float,),
            strict=False,
        )
        assert res == {}

    @patch("fastkml.helpers.handle_error")
    def test_attribute_float_kwarg(
        self,
        mock_handle_error: Callable[..., None],
    ) -> None:
        element = Mock()
        element.get.return_value = "abcd"

        res = attribute_float_kwarg(
            element=element,
            ns="ns",
            name_spaces={"name": "uri"},
            node_name="node",
            kwarg="a",
            classes=(float,),
            strict=True,
        )

        assert res == {}
        mock_handle_error.assert_called_once()  # type: ignore[attr-defined]

    def test_subelement_enum_kwarg(self) -> None:
        node = Node()
        node.text = ""
        element = Mock()
        element.find.return_value = node

        res = subelement_enum_kwarg(
            element=element,
            ns="ns",
            name_spaces={"name": "uri"},
            node_name="node",
            kwarg="a",
            classes=(Color,),
            strict=True,
        )

        assert res == {}
        element.find.assert_called_once_with("nsnode")

    def test_attribute_enum_kwarg(self) -> None:
        element = Mock()
        element.get.return_value = None

        res = attribute_enum_kwarg(
            element=element,
            ns="ns",
            name_spaces={"name": "uri"},
            node_name="node",
            kwarg="a",
            classes=(Color,),
            strict=True,
        )

        assert res == {}
        element.get.assert_called_once_with("nsnode")

    def test_subelement_bool_kwarg(self) -> None:
        node = Node()
        node.text = ""
        element = Mock()
        element.find.return_value = node
        res = subelement_bool_kwarg(
            element=element,
            ns="ns",
            name_spaces={"name": "uri"},
            node_name="node",
            kwarg="a",
            classes=(bool,),
            strict=True,
        )

        assert res == {}
        element.find.assert_called_once_with("nsnode")
