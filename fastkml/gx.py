# Copyright (C) 2012 - 2023 Christian Ledermann
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
KML Extension Namespace and the gx prefix.

With the launch of Google Earth 5.0, Google has provided extensions to KML
to support a number of new features. These extensions use the gx prefix
and the following namespace URI::

    xmlns:gx="http://www.google.com/kml/ext/2.2"

This namespace URI must be added to the <kml> element in any KML file
using gx-prefixed elements::

    <kml
        xmlns="http://www.opengis.net/kml/2.2"
        xmlns:gx="http://www.google.com/kml/ext/2.2"
    >

Extensions to KML may not be supported in all geo-browsers. If your
browser doesn't support particular extensions, the data in those
extensions should be silently ignored, and the rest of the KML file
should load without errors.

Elements that currently use the gx prefix are:

* gx:altitudeMode
* gx:altitudeOffset
* gx:angles
* gx:AnimatedUpdate
* gx:balloonVisibility
* gx:coord
* gx:delayedStart
* gx:drawOrder
* gx:duration
* gx:FlyTo
* gx:flyToMode
* gx:h
* gx:horizFov
* gx:interpolate
* gx:labelVisibility
* gx:LatLonQuad
* gx:MultiTrack
* gx:vieweroptions
* gx:outerColor
* gx:outerWidth
* gx:physicalWidth
* gx:Playlist
* gx:playMode
* gx:SoundCue
* gx:TimeSpan
* gx:TimeStamp
* gx:Tour
* gx:TourControl
* gx:TourPrimitive
* gx:Track
* gx:ViewerOptions
* gx:w
* gx:Wait
* gx:x
* gx:y

The complete XML schema for elements in this extension namespace is
located at http://developers.google.com/kml/schema/kml22gx.xsd.
"""

import logging
from dataclasses import dataclass
from itertools import zip_longest
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import cast

import pygeoif.geometry as geo
from pygeoif.types import PointType

from fastkml import config
from fastkml.enums import AltitudeMode
from fastkml.geometry import _Geometry
from fastkml.helpers import bool_subelement
from fastkml.helpers import coords_subelement_list
from fastkml.helpers import coords_subelement_list_kwarg
from fastkml.helpers import datetime_subelement_list
from fastkml.helpers import datetime_subelement_list_kwarg
from fastkml.helpers import enum_subelement
from fastkml.helpers import subelement_bool_kwarg
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.times import KmlDateTime

__all__ = [
    "Angle",
    "MultiTrack",
    "Track",
    "TrackItem",
    "track_items_to_geometry",
    "tracks_to_geometry",
]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Angle:
    """
    The gx:angles element specifies the heading, tilt, and roll.

    The angles are specified in degrees, and the
    default values are 0 (heading and tilt) and 0 (roll). The angles
    are specified in the following order: heading, tilt, roll.
    """

    heading: float = 0.0
    tilt: float = 0.0
    roll: float = 0.0

    @property
    def coords(self) -> PointType:
        """
        Get the coordinates of the angle.

        Returns
        -------
        PointType
            The coordinates of the angle.

        """
        return (self.heading, self.tilt, self.roll)


@dataclass(frozen=True)
class TrackItem:
    """A track item describes an objects position and heading at a specific time."""

    when: KmlDateTime
    coord: geo.Point
    angle: Optional[Angle] = None


def track_items_to_geometry(track_items: Iterable[TrackItem]) -> geo.LineString:
    """
    Convert a sequence of TrackItems to a LineString geometry.

    Args:
    ----
        track_items : Iterable[TrackItem]
            A sequence of TrackItems.

    Returns:
    -------
        geo.LineString
            A LineString geometry representing the track.

    """
    return geo.LineString.from_points(
        *[item.coord for item in track_items if item.coord is not None],
    )


class Track(_Geometry):
    """
    A track describes how an object moves through the world over a given time period.

    This feature allows you to create one visible object in Google Earth
    (either a Point icon or a Model) that encodes multiple positions for the same object
    for multiple times. In Google Earth, the time slider allows the user to move the
    view through time, which animates the position of the object.

    Tracks are a more efficient mechanism for associating time data with visible
    Features, since you create only one Feature, which can be associated with multiple
    time elements as the object moves through space.

    https://developers.google.com/kml/documentation/kmlreference#gxtrack
    """

    _default_nsid = config.GX
    track_items: List[TrackItem]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        track_items: Optional[Iterable[TrackItem]] = None,
        whens: Optional[Iterable[KmlDateTime]] = None,
        coords: Optional[Iterable[PointType]] = None,
        angles: Optional[Iterable[PointType]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a GX object.

        Parameters
        ----------
        ns : Optional[str], optional
            The namespace for the GX object, by default None
        name_spaces : Optional[Dict[str, str]], optional
            A dictionary of namespace prefixes and URIs, by default None
        id : Optional[str], optional
            The ID of the GX object, by default None
        target_id : Optional[str], optional
            The target ID of the GX object, by default None
        altitude_mode : Optional[AltitudeMode], optional
            The altitude mode of the GX object, by default None
        track_items : Optional[Iterable[TrackItem]], optional
            The track items of the GX object, by default None
        whens : Optional[Iterable[KmlDateTime]], optional
            The timestamps of the track items, by default None
        coords : Optional[Iterable[PointType]], optional
            The coordinates of the track items, by default None
        angles : Optional[Iterable[PointType]], optional
            The angles of the track items, by default None
        **kwargs : Any, optional
            Additional keyword arguments.

        Raises
        ------
        ValueError
            If both `geometry` and `track_items` are specified.

        """
        angles = list(angles) if angles else []
        if (whens or coords) and track_items:
            msg = "Cannot specify both geometry and track_items"
            raise ValueError(msg)
        if not track_items and whens and coords:
            track_items = [
                TrackItem(
                    when=cast(KmlDateTime, when),
                    coord=geo.Point(*coord),
                    angle=Angle(*angle),
                )
                for when, coord, angle in zip_longest(
                    whens,
                    coords,
                    angles,
                    fillvalue=(),
                )
            ]
        self.track_items = list(track_items) if track_items else []
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            altitude_mode=altitude_mode,
            **kwargs,
        )

    def __repr__(self) -> str:
        """
        Create a string representation for Track.

        Returns
        -------
        str
            The string representation of the Track object.

        """
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"track_items={self.track_items!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[geo.LineString]:
        """
        Get the geometry of the track.

        Returns
        -------
        Optional[geo.LineString]
            The geometry of the track.

        """
        return track_items_to_geometry(self.track_items)

    @property
    def whens(self) -> Tuple[KmlDateTime, ...]:
        """
        Get the timestamps of the track items.

        Returns
        -------
        Tuple[KmlDateTime]
            The timestamps of the track items.

        """
        return tuple(item.when for item in self.track_items)

    @property
    def coords(self) -> Tuple[PointType, ...]:
        """
        Get the coordinates of the track items.

        Returns
        -------
        Tuple[PointType]
            The coordinates of the track items.

        """
        return tuple(
            item.coord.coords[0]  # type: ignore[misc]
            for item in self.track_items
            if item.coord
        )

    @property
    def angles(self) -> Tuple[PointType, ...]:
        """
        Get the angles of the track items.

        Returns
        -------
        Tuple[Angle]
            The angles of the track items.

        """
        return tuple(item.angle.coords for item in self.track_items if item.angle)

    def __bool__(self) -> bool:
        """
        Check if the track has any track items.

        Returns
        -------
        bool
            True if the track has track items, False otherwise.

        """
        return bool(self.track_items)


registry.register(
    Track,
    item=RegistryItem(
        ns_ids=("gx", "kml", ""),
        classes=(AltitudeMode,),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
        default=AltitudeMode.clamp_to_ground,
    ),
)
registry.register(
    Track,
    item=RegistryItem(
        ns_ids=("kml", "gx", ""),
        classes=(KmlDateTime,),
        attr_name="whens",
        node_name="when",
        get_kwarg=datetime_subelement_list_kwarg,
        set_element=datetime_subelement_list,
    ),
)
registry.register(
    Track,
    item=RegistryItem(
        ns_ids=("gx", ""),
        classes=(tuple,),
        attr_name="coords",
        node_name="coord",
        get_kwarg=coords_subelement_list_kwarg,
        set_element=coords_subelement_list,
    ),
)
registry.register(
    Track,
    item=RegistryItem(
        ns_ids=("gx", ""),
        classes=(tuple,),
        attr_name="angles",
        node_name="angles",
        get_kwarg=coords_subelement_list_kwarg,
        set_element=coords_subelement_list,
        default=(0.0, 0.0, 0.0),
    ),
)


def tracks_to_geometry(tracks: Iterable[Track]) -> geo.MultiLineString:
    """
    Convert a collection of tracks to a MultiLineString geometry.

    Args:
    ----
        tracks : Iterable[Track]
            A collection of tracks.

    Returns:
    -------
        geo.MultiLineString
            A MultiLineString geometry representing the tracks.

    """
    return geo.MultiLineString.from_linestrings(
        *[track.geometry for track in tracks if track.geometry],
    )


class MultiTrack(_Geometry):
    """
    A MultiTrack is a collection of tracks.

    A multi-track element is used to combine multiple track elements into a single
    conceptual unit. For example, suppose you collect GPS data for a day's bike ride
    that includes several rest stops and a stop for lunch. Because of the interruptions
    in time, one bike ride might appear as four different tracks when the times and
    positions are plotted.
    Grouping these <gx:Track> elements into one <gx:MultiTrack> container causes them to
    be displayed in Google Earth as sections of a single path.
    When the icon reaches the end of one segment, it moves to the beginning of the next
    segment.
    The <gx:interpolate> element specifies whether to stop at the end of one track and
    jump immediately to the start of the next one, or to interpolate the missing values
    between the two tracks.
    """

    _default_nsid = config.GX
    tracks: List[Track]

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        tracks: Optional[Iterable[Track]] = None,
        interpolate: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a GX object.

        Args:
        ----
            ns (Optional[str]): The namespace for the GX object.
            name_spaces (Optional[Dict[str, str]]): The dictionary of namespace prefixes
                and URIs.
            id (Optional[str]): The ID of the GX object.
            target_id (Optional[str]): The target ID of the GX object.
            altitude_mode (Optional[AltitudeMode]): The altitude mode of the GX object.
            geometry (Optional[geo.MultiLineString]): The geometry of the GX object.
            tracks (Optional[Iterable[Track]]): The tracks of the GX object.
            interpolate (Optional[bool]): The interpolate flag of the GX object.
            **kwargs (Any): Additional keyword arguments.

        Raises:
        ------
            ValueError: If both geometry and tracks are specified.

        """
        self.tracks = [t for t in tracks if t] if tracks else []
        self.interpolate = interpolate
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            altitude_mode=altitude_mode,
            **kwargs,
        )

    def __repr__(self) -> str:
        """Create a string (c)representation for MultiTrack."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"tracks={self.tracks!r}, "
            f"interpolate={self.interpolate!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    @property
    def geometry(self) -> Optional[geo.MultiLineString]:
        """
        Get the geometry of the gx object.

        Returns
        -------
            Optional[geo.MultiLineString]: The geometry of the gx object.

        """
        return tracks_to_geometry(self.tracks)

    def __bool__(self) -> bool:
        """
        Check if the object has any tracks.

        Returns
        -------
        bool
            True if the object has tracks, False otherwise.

        """
        return bool(self.tracks)


registry.register(
    MultiTrack,
    item=RegistryItem(
        ns_ids=("gx", "kml"),
        classes=(AltitudeMode,),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
        default=AltitudeMode.clamp_to_ground,
    ),
)
registry.register(
    MultiTrack,
    item=RegistryItem(
        ns_ids=("gx",),
        classes=(bool,),
        attr_name="interpolate",
        node_name="interpolate",
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)
registry.register(
    MultiTrack,
    item=RegistryItem(
        ns_ids=("gx",),
        classes=(Track,),
        attr_name="tracks",
        node_name="gx:Track",
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)
