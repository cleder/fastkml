# Copyright (C) 2012 -2022 Christian Ledermann
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
from fastkml.atom import Author
from fastkml.atom import Contributor
from fastkml.atom import Link
from fastkml.containers import Document
from fastkml.containers import Folder
from fastkml.data import Data
from fastkml.data import ExtendedData
from fastkml.data import Schema
from fastkml.data import SchemaData
from fastkml.features import Placemark
from fastkml.kml import KML
from fastkml.overlays import GroundOverlay
from fastkml.overlays import PhotoOverlay
from fastkml.styles import BalloonStyle
from fastkml.styles import IconStyle
from fastkml.styles import LabelStyle
from fastkml.styles import LineStyle
from fastkml.styles import PolyStyle
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.views import Camera
from fastkml.views import LookAt

__all__ = [
    "KML",
    "Document",
    "Folder",
    "GroundOverlay",
    "Placemark",
    "TimeSpan",
    "TimeStamp",
    "ExtendedData",
    "Data",
    "PhotoOverlay",
    "Schema",
    "SchemaData",
    "StyleUrl",
    "Style",
    "StyleMap",
    "IconStyle",
    "LineStyle",
    "PolyStyle",
    "LabelStyle",
    "BalloonStyle",
    "Link",
    "Author",
    "Contributor",
    "Camera",
    "LookAt",
]
