# Copyright (C) 2024 Christian Ledermann
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

"""GX SimpleArrayData Extension."""

from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.helpers import attribute_text_kwarg
from fastkml.helpers import clean_string
from fastkml.helpers import subelement_text_list_kwarg
from fastkml.helpers import text_attribute
from fastkml.helpers import text_subelement_list
from fastkml.registry import RegistryItem
from fastkml.registry import registry

__all__ = ["SimpleArrayData"]


class SimpleArrayData(_XMLObject):
    """
    A SimpleArrayData element.

    This element is used to define an array of string values. It is used in
    conjunction with the gx:SimpleArrayField element to specify how the array
    values are to be displayed.
    """

    _default_nsid = config.GX
    name: Optional[str]
    data: List[Optional[str]]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        data: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Create a SimpleArrayData element.

        Args:
            ns: The namespace to use.
            name_spaces: A dictionary of namespace prefixes to namespace URIs.
            name: The name of the element.
            data: A list of string values.

        """
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.data = [clean_string(d) for d in data] if data is not None else []
        self.name = clean_string(name)

    def __repr__(self) -> str:
        """Create a string (c)representation for SimpleArrayData."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"name={self.name!r}, "
            f"data={self.data!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """Check if the element is named and has any data."""
        return bool(self.data) and bool(self.name)


registry.register(
    SimpleArrayData,
    RegistryItem(
        ns_ids=("gx", ""),
        classes=(str,),
        attr_name="data",
        node_name="value",
        get_kwarg=subelement_text_list_kwarg,
        set_element=text_subelement_list,
    ),
)
registry.register(
    SimpleArrayData,
    RegistryItem(
        ns_ids=("", "gx"),
        classes=(str,),
        attr_name="name",
        node_name="name",
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
