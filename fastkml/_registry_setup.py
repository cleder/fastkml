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

from fastkml.data import ExtendedData
from fastkml.gx.track import Track
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
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
