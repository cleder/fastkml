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
"""
Model element.

The Model element defines a 3D model that is attached to a Placemark.

https://developers.google.com/kml/documentation/models
https://developers.google.com/kml/documentation/kmlreference#model

"""

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from pygeoif.geometry import Point

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.enums import AltitudeMode
from fastkml.helpers import clean_string
from fastkml.helpers import enum_subelement
from fastkml.helpers import float_subelement
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.kml_base import _BaseObject
from fastkml.links import Link
from fastkml.registry import RegistryItem
from fastkml.registry import registry

__all__ = ["Alias", "Location", "Model", "Orientation", "ResourceMap", "Scale"]


class Location(_XMLObject):
    """Represents a location in KML."""

    _default_nsid = config.KML

    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        altitude: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new Location."""
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.altitude = altitude
        self.latitude = latitude
        self.longitude = longitude

    def __bool__(self) -> bool:
        """Return True if latitude and longitude are set."""
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
            f"**{self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[Point]:
        """Return a Point representation of the geometry."""
        if not self:
            return None
        assert self.longitude is not None  # noqa: S101
        assert self.latitude is not None  # noqa: S101
        return Point(self.longitude, self.latitude, self.altitude)


registry.register(
    Location,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="longitude",
        node_name="longitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    Location,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="latitude",
        node_name="latitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    Location,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="altitude",
        node_name="altitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=0.0,
    ),
)


class Orientation(_XMLObject):
    """Represents an orientation in KML."""

    _default_nsid = config.KML

    heading: Optional[float]
    tilt: Optional[float]
    roll: Optional[float]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        heading: Optional[float] = None,
        tilt: Optional[float] = None,
        roll: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new Orientation."""
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.heading = heading
        self.tilt = tilt
        self.roll = roll

    def __bool__(self) -> bool:
        """Return True if heading, tilt, or roll are set."""
        return any(
            (self.heading is not None, self.tilt is not None, self.roll is not None),
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
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    Orientation,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="heading",
        node_name="heading",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=0.0,
    ),
)
registry.register(
    Orientation,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="tilt",
        node_name="tilt",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=0.0,
    ),
)
registry.register(
    Orientation,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="roll",
        node_name="roll",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=0.0,
    ),
)


class Scale(_XMLObject):
    """Represents a scale in KML."""

    _default_nsid = config.KML

    x: Optional[float]
    y: Optional[float]
    z: Optional[float]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new Scale."""
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.x = x
        self.y = y
        self.z = z

    def __bool__(self) -> bool:
        """Return True if x, y, or z are set."""
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
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    Scale,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="x",
        node_name="x",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=1.0,
    ),
)
registry.register(
    Scale,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="y",
        node_name="y",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=1.0,
    ),
)
registry.register(
    Scale,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="z",
        node_name="z",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
        default=1.0,
    ),
)


class Alias(_XMLObject):
    """Represents an alias in KML."""

    _default_nsid = config.KML

    target_href: Optional[str]
    source_href: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        target_href: Optional[str] = None,
        source_href: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new Alias."""
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.target_href = clean_string(target_href)
        self.source_href = clean_string(source_href)

    def __bool__(self) -> bool:
        """Return True if target_href or source_href are set."""
        return any((self.target_href is not None, self.source_href is not None))

    def __repr__(self) -> str:
        """Create a string (c)representation for Alias."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"target_href={self.target_href!r}, "
            f"source_href={self.source_href!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    Alias,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="target_href",
        node_name="targetHref",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    Alias,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="source_href",
        node_name="sourceHref",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)


class ResourceMap(_XMLObject):
    """Represents a resource map in KML."""

    _default_nsid = config.KML

    aliases: List[Alias]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        aliases: Optional[Iterable[Alias]] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new ResourceMap."""
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.aliases = list(aliases) if aliases is not None else []

    def __bool__(self) -> bool:
        """Return True if aliases are set."""
        return bool(self.aliases)

    def __repr__(self) -> str:
        """Create a string (c)representation for ResourceMap."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"aliases={self.aliases!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    ResourceMap,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="aliases",
        node_name="Alias",
        classes=(Alias,),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


class Model(_BaseObject):
    """Represents a model in KML."""

    altitude_mode: Optional[AltitudeMode]
    location: Optional[Location]
    orientation: Optional[Orientation]
    scale: Optional[Scale]
    link: Optional[Link]
    resource_map: Optional[ResourceMap]

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
        **kwargs: Any,
    ) -> None:
        """Create a new Model."""
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.altitude_mode = altitude_mode
        self.location = location
        self.orientation = orientation
        self.scale = scale
        self.link = link
        self.resource_map = resource_map

    def __bool__(self) -> bool:
        """Return True if link and location are set."""
        return all((self.link, self.location))

    def __repr__(self) -> str:
        """Create a string representation for Model."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"location={self.location!r}, "
            f"orientation={self.orientation!r}, "
            f"scale={self.scale!r}, "
            f"link={self.link!r}, "
            f"resource_map={self.resource_map!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[Point]:
        """Return a Point representation of the geometry."""
        return self.location.geometry if self.location else None


registry.register(
    Model,
    RegistryItem(
        ns_ids=("kml", "gx", ""),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        classes=(AltitudeMode,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
        default=AltitudeMode.clamp_to_ground,
    ),
)
registry.register(
    Model,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="location",
        node_name="Location",
        classes=(Location,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Model,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="orientation",
        node_name="Orientation",
        classes=(Orientation,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Model,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="scale",
        node_name="Scale",
        classes=(Scale,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Model,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="link",
        node_name="Link",
        classes=(Link,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    Model,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="resource_map",
        node_name="ResourceMap",
        classes=(ResourceMap,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
