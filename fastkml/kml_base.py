# Copyright (C) 2012 - 2024 Christian Ledermann
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

"""Abstract base classes."""
from typing import Any
from typing import Dict
from typing import Optional

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.helpers import attribute_text_kwarg
from fastkml.helpers import text_attribute
from fastkml.registry import RegistryItem
from fastkml.registry import registry

__all__ = ["_BaseObject"]


class _BaseObject(_XMLObject):
    """
    Base class for all KML objects.

    This is an abstract base class and cannot be used directly in a
    KML file. It provides the id attribute, which allows unique
    identification of a KML element, and the targetId attribute,
    which is used to reference objects that have already been loaded into
    Google Earth. The id attribute must be assigned if the <Update>
    mechanism is to be used.
    """

    _default_nsid = config.KML

    id = None
    target_id = None

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the KML Object.

        Parameters
        ----------
        ns: (Optional[str])
            The namespace of the KML object.
        name_spaces: (Optional[Dict[str, str]])
            The dictionary of namespace prefixes and URIs.
        id: (Optional[str])
            The id attribute of the KML object.
        target_id: (Optional[str])
            The targetId attribute of the KML object.
        kwargs: (Any)
            Additional keyword arguments.

        Returns
        -------
        None

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.id = id or ""
        self.target_id = target_id or ""

    def __repr__(self) -> str:
        """
        Create a string representation for _BaseObject.

        Returns
        -------
        str: The string representation of _BaseObject.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    _BaseObject,
    item=RegistryItem(
        ns_ids=("", "kml"),
        attr_name="id",
        node_name="id",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)

registry.register(
    _BaseObject,
    item=RegistryItem(
        ns_ids=("", "kml"),
        attr_name="target_id",
        node_name="targetId",
        classes=(str,),
        get_kwarg=attribute_text_kwarg,
        set_element=text_attribute,
    ),
)
