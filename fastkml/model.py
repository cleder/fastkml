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
        """Create a new Location."""
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.altitude = altitude
        self.latitude = latitude
        self.longitude = longitude

    def __bool__(self) -> bool:
        return all((self.latitude is not None, self.longitude is not None))

    def __repr__(self) -> str:
        """Create a string (c)representation for Location."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"altitude={self.altitude!r}, "
            f"latitude={self.latitude!r}, "
            f"longitude={self.longitude!r}, "
            ")"
        )


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

    def __bool__(self) -> bool:
        return any(
            (self.heading is not None, self.tilt is not None, self.roll is not None)
        )

    def __repr__(self) -> str:
        """Create a string (c)representation for Orientation."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"heading={self.heading!r}, "
            f"tilt={self.tilt!r}, "
            f"roll={self.roll!r}, "
            ")"
        )


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

    def __bool__(self) -> bool:
        return any((self.x is not None, self.y is not None, self.z is not None))

    def __repr__(self) -> str:
        """Create a string (c)representation for Scale."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"x={self.x!r}, "
            f"y={self.y!r}, "
            f"z={self.z!r}, "
            ")"
        )


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

    def __bool__(self) -> bool:
        return all((self.target_href is not None, self.source_href is not None))

    def __repr__(self) -> str:
        """Create a string (c)representation for Alias."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"target_href={self.target_href!r}, "
            f"source_href={self.source_href!r}, "
            ")"
        )


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

    def __bool__(self) -> bool:
        return bool(self.aliases)

    def __repr__(self) -> str:
        """Create a string (c)representation for ResourceMap."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"aliases={self.aliases!r}, "
            ")"
        )


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

    def __bool__(self) -> bool:
        return bool(self.link)

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
