# Copyright (C) 2025 Christian Ledermann
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

"""To avoid circular imports, some element registration is performed here."""

import logging

from fastkml.containers import Document
from fastkml.containers import Folder
from fastkml.data import Data
from fastkml.data import ExtendedData
from fastkml.data import SchemaData
from fastkml.features import NetworkLink
from fastkml.features import Placemark
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.gx.track import MultiTrack
from fastkml.gx.track import Track
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.helpers import xml_subelement_list_kwarg_ordered
from fastkml.links import Icon
from fastkml.links import Link
from fastkml.model import Alias
from fastkml.model import Location
from fastkml.model import Model
from fastkml.model import Orientation
from fastkml.model import ResourceMap
from fastkml.model import Scale
from fastkml.network_link_control import Change
from fastkml.network_link_control import Create
from fastkml.network_link_control import Delete
from fastkml.overlays import GroundOverlay
from fastkml.overlays import ImagePyramid
from fastkml.overlays import LatLonBox
from fastkml.overlays import PhotoOverlay
from fastkml.overlays import ScreenOverlay
from fastkml.overlays import ViewVolume
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.styles import BalloonStyle
from fastkml.styles import IconStyle
from fastkml.styles import LabelStyle
from fastkml.styles import LineStyle
from fastkml.styles import Pair
from fastkml.styles import PolyStyle
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.views import Camera
from fastkml.views import LatLonAltBox
from fastkml.views import Lod
from fastkml.views import LookAt
from fastkml.views import Region

logger = logging.getLogger(__name__)


registry.register(
    Track,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="extended_data",
        node_name="ExtendedData",
        classes=(ExtendedData,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


# Register objects for Create, Delete, and Change according to the KML schema:
# - Create: Contains AbstractContainerGroup (Document, Folder)
# - Delete: Contains AbstractFeatureGroup (features)
# - Change: Contains AbstractObjectGroup (any KML object)

# Create can only contain containers (Document, Folder)
_create_classes = (
    Document,
    Folder,
)
registry.register(
    Create,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="objects",
        node_name=",".join(cls.get_tag_name() for cls in _create_classes),
        classes=_create_classes,
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
        custom_get_kwarg=xml_subelement_list_kwarg_ordered,
    ),
)

# Delete can contain any feature type
_delete_classes = (
    Document,
    Folder,
    Placemark,
    GroundOverlay,
    PhotoOverlay,
    ScreenOverlay,
    NetworkLink,
)
_delete_node_name = ",".join(cls.get_tag_name() for cls in _delete_classes)
registry.register(
    Delete,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="objects",
        node_name=_delete_node_name,
        classes=_delete_classes,
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
        custom_get_kwarg=xml_subelement_list_kwarg_ordered,
    ),
)

# Change can contain any KML object (AbstractObjectGroup).
# This covers the full set of non-abstract classes derived from _BaseObject,
# matching the KML schema's AbstractObjectGroup.
_change_classes = (
    # Features
    Document,
    Folder,
    NetworkLink,
    Placemark,
    # Overlays
    GroundOverlay,
    PhotoOverlay,
    ScreenOverlay,
    # Overlay sub-elements
    ImagePyramid,
    LatLonBox,
    ViewVolume,
    # Views
    Camera,
    LatLonAltBox,
    Lod,
    LookAt,
    Region,
    # Styles
    BalloonStyle,
    IconStyle,
    LabelStyle,
    LineStyle,
    Pair,
    PolyStyle,
    Style,
    StyleMap,
    # Times
    TimeSpan,
    TimeStamp,
    # Geometry
    LinearRing,
    LineString,
    MultiGeometry,
    Point,
    Polygon,
    # GX Geometry
    MultiTrack,
    Track,
    # Model
    Alias,
    Location,
    Model,
    Orientation,
    ResourceMap,
    Scale,
    # Links
    Icon,
    Link,
    # Data
    Data,
    SchemaData,
)
_change_node_name = ",".join(cls.get_tag_name() for cls in _change_classes)
registry.register(
    Change,
    RegistryItem(
        ns_ids=("kml", "", "gx"),
        attr_name="objects",
        node_name=_change_node_name,
        classes=_change_classes,
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
        custom_get_kwarg=xml_subelement_list_kwarg_ordered,
    ),
)
