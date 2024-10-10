from typing_extensions import Protocol
from unittest.mock import Mock, patch
import pytest
from fastkml.exceptions import KMLParseError, KMLWriteError
from fastkml.geometry import handle_invalid_geometry_error, coordinates_subelement, create_kml_geometry
from fastkml.types import Element
from tests.base import StdLibrary
from fastkml import base

class TestGeometryFunctions(StdLibrary):
    """Test functions in Geometry"""

    @patch('fastkml.config.etree.tostring')
    def test_handle_invalid_geometry_error_true(self, mock_to_string) -> None:
        mock_element = Mock()
        with pytest.raises(KMLParseError):
            handle_invalid_geometry_error(error=ValueError, element=mock_element, strict=True)
    
    @patch('fastkml.config.etree.tostring')
    def test_handle_invalid_geometry_error_false(self, mock_to_string) -> None:
        mock_element = Mock()
        assert handle_invalid_geometry_error(error=ValueError, element=mock_element, strict=False) is None
    
    def test_coordinates_subelement_exception(self) -> None:
        obj = Mock()
        setattr(obj, 'coordinates', [(1.123456, 2.654321, 3.111111, 4.222222)])  # Invalid 4D coordinates
        
        element = Mock()

        precision = None
        attr_name = 'coordinates'
        
        with pytest.raises(KMLWriteError):
            coordinates_subelement(
                obj=obj,
                attr_name=attr_name,
                node_name=None, 
                element=element,
                precision=precision,
                verbosity=None,
                default=None
            )
    def test_coordinates_subelement_getattr(self) -> None:
        obj = Mock()
        setattr(obj, 'coordinates', [(1.123456, 2.654321), (3.123456, 4.654321)])
        
        element = Mock()
        
        precision = 4
        attr_name = 'coordinates'
        
        assert coordinates_subelement(
                obj=None,
                attr_name=attr_name,
                node_name=None, 
                element=element,
                precision=precision,
                verbosity=None,
                default=None
            ) is None
