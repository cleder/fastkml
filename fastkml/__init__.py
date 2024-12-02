# Copyright (C) 2012 -2024 Christian Ledermann
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
Fastkml is a library to read, write and manipulate kml files.

It aims to keep it simple and fast (using lxml if available).
Fast refers to the time you spend to write and read KML files as well as the time
you spend to get acquainted to the library or to create KML objects.
It provides a subset of KML and is aimed at documents that can be read from
multiple clients such as openlayers and google maps rather than to give you all
functionality that KML on google earth provides.
"""

from fastkml.about import __version__  # noqa: F401
from fastkml.atom import Author as AtomAuthor
from fastkml.atom import Contributor as AtomContributor
from fastkml.atom import Link as AtomLink
from fastkml.containers import Document
from fastkml.containers import Folder
from fastkml.data import Data
from fastkml.data import ExtendedData
from fastkml.data import Schema
from fastkml.data import SchemaData
from fastkml.data import SimpleData
from fastkml.data import SimpleField
from fastkml.features import NetworkLink
from fastkml.features import Placemark
from fastkml.features import Snippet
from fastkml.geometry import Coordinates
from fastkml.geometry import InnerBoundaryIs
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import OuterBoundaryIs
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.geometry import create_kml_geometry
from fastkml.kml import KML
from fastkml.links import Icon
from fastkml.links import Link
from fastkml.model import Alias
from fastkml.model import Location
from fastkml.model import Model
from fastkml.model import Orientation
from fastkml.model import ResourceMap
from fastkml.model import Scale
from fastkml.network_link_control import NetworkLinkControl
from fastkml.overlays import GroundOverlay
from fastkml.overlays import ImagePyramid
from fastkml.overlays import LatLonBox
from fastkml.overlays import OverlayXY
from fastkml.overlays import PhotoOverlay
from fastkml.overlays import RotationXY
from fastkml.overlays import ScreenOverlay
from fastkml.overlays import ScreenXY
from fastkml.overlays import Size
from fastkml.overlays import ViewVolume
from fastkml.styles import BalloonStyle
from fastkml.styles import HotSpot
from fastkml.styles import IconStyle
from fastkml.styles import LabelStyle
from fastkml.styles import LineStyle
from fastkml.styles import Pair
from fastkml.styles import PolyStyle
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.times import KmlDateTime
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.utils import find
from fastkml.utils import find_all
from fastkml.validator import get_schema_parser
from fastkml.validator import validate
from fastkml.views import Camera
from fastkml.views import LookAt

__all__ = [
    "KML",
    "Alias",
    "AtomAuthor",
    "AtomContributor",
    "AtomLink",
    "BalloonStyle",
    "Camera",
    "Coordinates",
    "Data",
    "Document",
    "ExtendedData",
    "Folder",
    "GroundOverlay",
    "HotSpot",
    "Icon",
    "IconStyle",
    "ImagePyramid",
    "InnerBoundaryIs",
    "KmlDateTime",
    "LabelStyle",
    "LatLonBox",
    "LineString",
    "LineStyle",
    "LinearRing",
    "Link",
    "Location",
    "LookAt",
    "Model",
    "MultiGeometry",
    "NetworkLink",
    "NetworkLinkControl",
    "Orientation",
    "OuterBoundaryIs",
    "OverlayXY",
    "Pair",
    "PhotoOverlay",
    "Placemark",
    "Point",
    "PolyStyle",
    "Polygon",
    "ResourceMap",
    "RotationXY",
    "Scale",
    "Schema",
    "SchemaData",
    "ScreenOverlay",
    "ScreenXY",
    "SimpleData",
    "SimpleField",
    "Size",
    "Snippet",
    "Style",
    "StyleMap",
    "StyleUrl",
    "TimeSpan",
    "TimeStamp",
    "ViewVolume",
    "create_kml_geometry",
    "find",
    "find_all",
    "get_schema_parser",
    "validate",
]
