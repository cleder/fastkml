from unittest.mock import Mock, patch
from fastkml.helpers import attribute_enum_kwarg
from fastkml.helpers import attribute_float_kwarg
from fastkml.helpers import enum_attribute
from fastkml.helpers import float_attribute
from fastkml.helpers import node_text
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import subelement_int_kwarg
from tests.base import StdLibrary
from enum import Enum


class Node:
    text: str


class Color(Enum):
    RED = 1


class TestStdLibrary(StdLibrary):
    @patch('fastkml.helpers.get_value')
    def test_node_text(self, mock_get_value) -> None:
        mock_get_value.return_value = False
        res = node_text(
            obj=None,
            element=None,
            attr_name="a",
            node_name="n",
            precision=0,
            verbosity=0,
            default="default"
        )
        assert res is None

    @patch('fastkml.helpers.get_value')
    def test_float_attribute(self, mock_get_value) -> None:
        mock_get_value.return_value = None
        res = float_attribute(
            obj=None,
            element="ele",
            attr_name="a",
            node_name="n",
            precision=0,
            verbosity=0,
            default="default"
        )
        assert res is None

    @patch('fastkml.helpers.get_value')
    def test_enum_attribute(self, mock_get_value) -> None:
        mock_get_value.return_value = None
        res = enum_attribute(
            obj=None,
            element="ele",
            attr_name="a",
            node_name="n",
            precision=0,
            verbosity=0,
            default="default"
        )
        assert res is None

    def test_subelement_int_kwarg(self):
        node = Node()
        node.text = None
        element = Mock()
        element.find.return_value = node
        res = subelement_int_kwarg(
                element=element,
                ns="ns",
                name_spaces="name",
                node_name="node",
                kwarg="kwarg",
                classes=None,
                strict=False
            )
        assert res == {}

    def test_subelement_float_kwarg(self):
        node = Node()
        node.text = None
        element = Mock()
        element.find.return_value = node
        res = subelement_float_kwarg(
                element=element,
                ns="ns",
                name_spaces="name",
                node_name="node",
                kwarg="kwarg",
                classes=None,
                strict=False
            )
        assert res == {}

    @patch('fastkml.helpers.handle_error')
    def test_attribute_float_kwarg(self, mock_handle_error) -> None:
        element = Mock()
        element.get.return_value = "abcd"
        mock_handle_error.return_value = None
        res = attribute_float_kwarg(
            element=element,
            ns="ns",
            name_spaces="name",
            node_name="node",
            kwarg="a",
            classes=None,
            strict=True
        )
        assert res == {}

    def test_subelement_enum_kwarg(self) -> None:
        node = Node()
        node.text = None
        element = Mock()
        element.find.return_value = node
        res = subelement_enum_kwarg(
            element=element,
            ns="ns",
            name_spaces="name",
            node_name="node",
            kwarg="a",
            classes=[Color],
            strict=True
        )
        assert res == {}

    def test_attribute_enum_kwarg(self) -> None:
        element = Mock()
        element.get.return_value = None
        res = attribute_enum_kwarg(
            element=element,
            ns="ns",
            name_spaces="name",
            node_name="node",
            kwarg="a",
            classes=[Color],
            strict=True
        )
        assert res == {}
