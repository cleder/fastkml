# Copyright (C) 2012  Christian Ledermann
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
Fastkml is a library to read, write and manipulate kml files. It aims to keep
it simple and fast (using lxml if available). Fast refers to the time you spend
to write and read KML files as well as the time you spend to get aquainted to
the library or to create KML objects. It provides a subset of KML and is aimed
at documents that can be read from multiple clients such as openlayers and
google maps rather than to give you all functionality that KML on google earth
provides.
"""

from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

from .atom import Author
from .atom import Contributor
from .atom import Link
from .kml import KML
from .kml import Data
from .kml import Document
from .kml import ExtendedData
from .kml import Folder
from .kml import Placemark
from .kml import Schema
from .kml import SchemaData
from .kml import TimeSpan
from .kml import TimeStamp
from .styles import BalloonStyle
from .styles import IconStyle
from .styles import LabelStyle
from .styles import LineStyle
from .styles import PolyStyle
from .styles import Style
from .styles import StyleMap
from .styles import StyleUrl

try:
    __version__ = get_distribution("fastkml").version
except DistributionNotFound:
    __version__ = "dev"

__all__ = [
    "KML",
    "Document",
    "Folder",
    "Placemark",
    "TimeSpan",
    "TimeStamp",
    "ExtendedData",
    "Data",
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
]
