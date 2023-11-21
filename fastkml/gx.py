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
import contextlib
import datetime
import logging
from dataclasses import dataclass
from itertools import zip_longest
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import cast

import arrow
import pygeoif.geometry as geo

from fastkml import config
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity
from fastkml.geometry import _Geometry
from fastkml.types import Element

__all__ = [
    "Angle",
    "MultiTrack",
    "Track",
    "TrackItem",
    "linestring_to_track_items",
    "multilinestring_to_tracks",
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


@dataclass(frozen=True)
class TrackItem:
    """A track item describes an objects position and heading at a specific time."""

    when: Optional[datetime.datetime] = None
    coord: Optional[geo.Point] = None
    angle: Optional[Angle] = None

    def etree_elements(
        self,
        *,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
        name_spaces: Optional[Dict[str, str]] = None,
    ) -> Iterator[Element]:
        name_spaces = name_spaces or {}
        name_spaces = {**config.NAME_SPACES, **name_spaces}
        element: Element = config.etree.Element(  # type: ignore[attr-defined]
            f"{name_spaces.get('kml', '')}when",
        )
        if self.when:
            element.text = self.when.isoformat()
        yield element
        element = config.etree.Element(  # type: ignore[attr-defined]
            f"{name_spaces.get('gx', '')}coord",
        )
        if self.coord:
            element.text = " ".join([str(c) for c in self.coord.coords[0]])
        yield element
        element = config.etree.Element(  # type: ignore[attr-defined]
            f"{name_spaces.get('gx', '')}angles",
        )
        if self.angle:
            element.text = " ".join(
                [str(self.angle.heading), str(self.angle.tilt), str(self.angle.roll)],
            )
        yield element


def track_items_to_geometry(track_items: Sequence[TrackItem]) -> geo.LineString:
    return geo.LineString.from_points(
        *[item.coord for item in track_items if item.coord is not None],
    )


def linestring_to_track_items(linestring: geo.LineString) -> List[TrackItem]:
    return [TrackItem(coord=point) for point in linestring.geoms]


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
    """

    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: Optional[geo.LineString] = None,
        track_items: Optional[Sequence[TrackItem]] = None,
    ) -> None:
        if geometry and track_items:
            msg = "Cannot specify both geometry and track_items"
            raise ValueError(msg)
        if geometry:
            track_items = linestring_to_track_items(geometry)
        elif track_items:
            geometry = track_items_to_geometry(track_items)
        self.track_items = track_items
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"track_items={self.track_items!r}"
            ")"
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
        name_spaces: Optional[Dict[str, str]] = None,
    ) -> Element:
        self.__name__ = self.__class__.__name__
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.track_items:
            for track_item in self.track_items:
                for track_item_element in track_item.etree_elements(
                    precision=precision,
                    verbosity=verbosity,
                    name_spaces=name_spaces,
                ):
                    element.append(track_item_element)
        return element

    @classmethod
    def track_items_kwargs_from_element(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> List[TrackItem]:
        time_stamps: List[Optional[datetime.datetime]] = []
        for time_stamp in element.findall(f"{config.KMLNS}when"):
            if time_stamp is not None and time_stamp.text:
                time_stamps.append(arrow.get(time_stamp.text).datetime)
            else:
                time_stamps.append(None)
        coords: List[Optional[geo.Point]] = []
        for coord in element.findall(f"{config.GXNS}coord"):
            if coord is not None and coord.text:
                coords.append(
                    geo.Point(*[float(c) for c in coord.text.strip().split()]),
                )
            else:
                coords.append(None)
        angles: List[Optional[Angle]] = []
        for angle in element.findall(f"{config.GXNS}angles"):
            if angle is not None and angle.text:
                angles.append(Angle(*[float(a) for a in angle.text.strip().split()]))
            else:
                angles.append(None)
        return [
            TrackItem(when=when, coord=coord, angle=angle)
            for when, coord, angle in zip_longest(time_stamps, coords, angles)
        ]

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs["track_items"] = cls.track_items_kwargs_from_element(
            ns=ns,
            element=element,
            strict=strict,
        )
        return kwargs


def multilinestring_to_tracks(
    multilinestring: geo.MultiLineString,
    ns: Optional[str],
) -> List[Track]:
    return [Track(ns=ns, geometry=linestring) for linestring in multilinestring.geoms]


def tracks_to_geometry(tracks: Sequence[Track]) -> geo.MultiLineString:
    return geo.MultiLineString.from_linestrings(
        *[cast(geo.LineString, track.geometry) for track in tracks if track.geometry],
    )


class MultiTrack(_Geometry):
    def __init__(
        self,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        extrude: Optional[bool] = False,
        tessellate: Optional[bool] = False,
        altitude_mode: Optional[AltitudeMode] = None,
        geometry: Optional[geo.MultiLineString] = None,
        tracks: Optional[Sequence[Track]] = None,
        interpolate: Optional[bool] = None,
    ) -> None:
        if geometry and tracks:
            msg = "Cannot specify both geometry and track_items"
            raise ValueError(msg)
        if geometry:
            tracks = multilinestring_to_tracks(geometry, ns=ns)
        elif tracks:
            geometry = tracks_to_geometry(tracks)
        self.tracks = tracks
        self.interpolate = interpolate
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"extrude={self.extrude!r}, "
            f"tessellate={self.tessellate!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"tracks={self.tracks!r}, "
            f"interpolate={self.interpolate!r}"
            ")"
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
        name_spaces: Optional[Dict[str, str]] = None,
    ) -> Element:
        self.__name__ = self.__class__.__name__
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.interpolate is not None:
            i_element = cast(
                Element,
                config.etree.SubElement(  # type: ignore[attr-defined]
                    element,
                    f"{self.ns}interpolate",
                ),
            )
            i_element.text = str(int(self.interpolate))
        for track in self.tracks or []:
            element.append(
                track.etree_element(
                    precision=precision,
                    verbosity=verbosity,
                    name_spaces=name_spaces,
                ),
            )
        return element

    @classmethod
    def _get_interpolate(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> Optional[bool]:
        interpolate = element.find(f"{ns}interpolate")
        if interpolate is None:
            return None
        with contextlib.suppress(ValueError):
            return bool(int(interpolate.text.strip()))
        return None

    @classmethod
    def _get_track_kwargs_from_element(
        cls,
        *,
        ns: str,
        element: Element,
        strict: bool,
    ) -> List[Track]:
        return [
            cast(
                Track,
                Track.class_from_element(
                    ns=ns,
                    element=track,
                    strict=strict,
                ),
            )
            for track in element.findall(f"{ns}Track")
            if track is not None
        ]

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs["interpolate"] = cls._get_interpolate(
            ns=ns,
            element=element,
            strict=strict,
        )
        kwargs["tracks"] = cls._get_track_kwargs_from_element(
            ns=kwargs["name_spaces"].get("gx", ""),
            element=element,
            strict=strict,
        )
        return kwargs
