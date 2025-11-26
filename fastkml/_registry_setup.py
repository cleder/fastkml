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
from fastkml.data import ExtendedData
from fastkml.features import NetworkLink
from fastkml.features import Placemark
from fastkml.gx.track import Track
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.network_link_control import Change
from fastkml.network_link_control import Create
from fastkml.network_link_control import Delete
from fastkml.overlays import GroundOverlay
from fastkml.overlays import PhotoOverlay
from fastkml.overlays import ScreenOverlay
from fastkml.registry import RegistryItem
from fastkml.registry import registry

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
registry.register(
    Create,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="objects",
        node_name="Folder,Document",
        classes=(
            Document,
            Folder,
        ),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)

# Delete can contain any feature type
_delete_node_name = (
    "Folder,Placemark,Document,GroundOverlay,PhotoOverlay,ScreenOverlay,NetworkLink"
)
_delete_classes = (
    Document,
    Folder,
    Placemark,
    GroundOverlay,
    PhotoOverlay,
    ScreenOverlay,
    NetworkLink,
)
registry.register(
    Delete,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="objects",
        node_name=_delete_node_name,
        classes=_delete_classes,
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)

# Change can contain any KML object (features, styles, etc.)
# For now, we support the same feature types as Delete
_change_node_name = (
    "Folder,Placemark,Document,GroundOverlay,PhotoOverlay,ScreenOverlay,NetworkLink"
)
_change_classes = (
    Document,
    Folder,
    Placemark,
    GroundOverlay,
    PhotoOverlay,
    ScreenOverlay,
    NetworkLink,
)
registry.register(
    Change,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="objects",
        node_name=_change_node_name,
        classes=_change_classes,
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)
