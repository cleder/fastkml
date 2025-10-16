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
"""
Classes and functions for working with geometries in KML files.

The classes in this module represent different types of geometries, such as points,
lines, polygons, and multi-geometries.
These geometries can be used to define the shape and location of features in KML files.

The module also provides functions for handling coordinates and extracting them from XML
elements.

"""

from typing import Any
from typing import Optional

from fastkml.enums import AltitudeMode
from fastkml.kml_base import _BaseObject


class _Geometry(_BaseObject):
    """
    Baseclass with common methods for all geometry objects.

    Attributes: altitudeMode: --> Specifies how altitude components in the <coordinates>
                                  element are interpreted.

    """

    altitude_mode: Optional[AltitudeMode]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a _Geometry object.

        Args:
        ----
            ns: Namespace of the object.
            name_spaces: Name spaces of the object.
            id: Id of the object.
            target_id: Target id of the object.
            altitude_mode: Specifies how altitude components in the <coordinates>
                           element are interpreted.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(
            ns=ns,
            id=id,
            name_spaces=name_spaces,
            target_id=target_id,
            **kwargs,
        )
        self.altitude_mode = altitude_mode
