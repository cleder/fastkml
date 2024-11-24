# Copyright (C) 2023  Christian Ledermann
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

from typing import Any
from typing import Union
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
# from fastkml.containers import Folder
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.registry import registry
from fastkml.registry import RegistryItem
from fastkml.base import _XMLObject
from fastkml.times import TimeSpan

class Change(_XMLObject):
    
    def __int__(
        self,
        target_id: str,
        elements: Optional[Union[TimeSpan]] = None
    ):
        super().__init__(
            target_id=target_id,
            elements=elements
        )
    
    def parse_children(self):
        pass

class Create(_XMLObject):
    def __int__(
        self,
        target_id: str,
        elements: Optional[Union[TimeSpan]] = None
    ):
        super().__init__(
            target_id=target_id,
            elements=elements
        )
    
    def parse_children(self):
        pass

class Delete(_XMLObject):
    def __int__(
        self,
        target_id: str,
        elements: Optional[Union[TimeSpan]] = None
    ):
        super().__init__(
            target_id=target_id,
            elements=elements
        )
    
    def parse_children(self):
        pass

class Update:

    def __init__(
            target_href: Optional[str] = None,
            change: Optional[Iterable[Change]] = None,
            create: Optional[Iterable[Create]] = None,
            delete: Optional[Iterable[Delete]] = None
    ):
        super().__init__(
            target_href=target_href,
            change=change,
            create=create,
            delete=delete
        )

registry.register(
    Update,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="change",
        node_name="TimeSpan",
        classes=(
            # PhotoOverlay,
            # Folder,
            TimeSpan,
        ),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    )
)
registry.register(
    Update,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="create",
        node_name="TimeSpan",
        classes=(
            # PhotoOverlay,
            # Folder,
            TimeSpan,
        ),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    )
)
registry.register(
    Update,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="delete",
        node_name="TimeSpan",
        classes=(
            # PhotoOverlay,
            # Folder,
            TimeSpan,
        ),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    )
)