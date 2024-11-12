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
"""Test the geometry error handling."""

from typing import Callable
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from fastkml.enums import Verbosity
from fastkml.exceptions import KMLParseError
from fastkml.exceptions import KMLWriteError
from fastkml.geometry import coordinates_subelement
from fastkml.geometry import handle_invalid_geometry_error
from tests.base import StdLibrary


class TestGeometryFunctions(StdLibrary):
    """Test functions in Geometry."""

    @patch("fastkml.config.etree.tostring", return_value=b"<kml:../>")
    def test_handle_invalid_geometry_error_true(
        self,
        mock_to_string: Callable[..., str],
    ) -> None:
        mock_element = Mock()
        with pytest.raises(
            KMLParseError,
            match=mock_to_string.return_value.decode(),  # type: ignore[attr-defined]
        ):
            handle_invalid_geometry_error(
                error=ValueError(),
                element=mock_element,
                strict=True,
            )
        mock_to_string.assert_called_once_with(  # type: ignore[attr-defined]
            mock_element,
            encoding="UTF-8",
        )

    @patch("fastkml.config.etree.tostring", return_value=b"<kml:... />")
    def test_handle_invalid_geometry_error_false(
        self,
        mock_to_string: Callable[..., str],
    ) -> None:
        mock_element = Mock()
        handle_invalid_geometry_error(
            error=ValueError(),
            element=mock_element,
            strict=False,
        )
        mock_to_string.assert_called_once_with(  # type: ignore[attr-defined]
            mock_element,
            encoding="UTF-8",
        )

    def test_coordinates_subelement_exception(self) -> None:
        obj = Mock()
        obj.coordinates = [(1.123456, 2.654321, 3.111111, 4.222222)]

        element = Mock()

        precision = 9
        attr_name = "coordinates"

        with pytest.raises(KMLWriteError):
            coordinates_subelement(
                obj=obj,
                attr_name=attr_name,
                node_name="",
                element=element,
                precision=precision,
                verbosity=Verbosity.terse,
                default=None,
            )
