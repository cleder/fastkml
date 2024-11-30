# Copyright (C) 2012-2023 Christian Ledermann
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
Model element.

The Model element defines a 3D model that is attached to a Placemark.

https://developers.google.com/kml/documentation/models
https://developers.google.com/kml/documentation/kmlreference#model

"""

from typing import Dict
from typing import Iterable
from typing import Optional

from fastkml.base import _XMLObject
from fastkml.enums import AltitudeMode
from fastkml.helpers import clean_string
from fastkml.kml_base import _BaseObject
from fastkml.links import Link


class Location(_XMLObject):
    """Represents a location in KML."""

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        altitude: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.altitude = altitude
        self.latitude = latitude
        self.longitude = longitude


class Orientation(_XMLObject):
    """Represents an orientation in KML."""

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        heading: Optional[float] = None,
        tilt: Optional[float] = None,
        roll: Optional[float] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.heading = heading
        self.tilt = tilt
        self.roll = roll


class Scale(_XMLObject):
    """Represents a scale in KML."""

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.x = x
        self.y = y
        self.z = z


class Alias(_XMLObject):
    """Represents an alias in KML."""

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        target_href: Optional[str] = None,
        source_href: Optional[str] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.target_href = clean_string(target_href)
        self.source_href = clean_string(source_href)


class ResourceMap(_XMLObject):
    """Represents a resource map in KML."""

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        aliases: Optional[Iterable[Alias]] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.aliases = list(aliases) if aliases is not None else []


class Model(_BaseObject):
    """Represents a model in KML."""

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        location: Optional[Location] = None,
        orientation: Optional[Orientation] = None,
        scale: Optional[Scale] = None,
        link: Optional[Link] = None,
        resource_map: Optional[ResourceMap] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.altitude_mode = altitude_mode
        self.location = location
        self.orientation = orientation
        self.scale = scale
        self.link = link
        self.resource_map = resource_map

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"location={self.location!r}, "
            f"orientation={self.orientation!r}, "
            f"scale={self.scale!r}, "
            f"link={self.link!r}, "
            f"resource_map={self.resource_map!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )
