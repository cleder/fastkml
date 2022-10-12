# Copyright (C) 2012 - 2022 Christian Ledermann
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

import logging
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from pygeoif.geometry import GeometryCollection
from pygeoif.geometry import LineString
from pygeoif.geometry import MultiLineString
from pygeoif.types import PointType

from fastkml.config import GXNS as NS
from fastkml.geometry import Geometry
from fastkml.types import Element

logger = logging.getLogger(__name__)


class GxGeometry(Geometry):
    def __init__(
        self,
        ns: None = None,
        id: None = None,
    ) -> None:
        """
        gxgeometry: a read-only subclass of geometry supporting gx: features,
        like gx:Track
        """
        super().__init__(ns, id)
        self.ns = NS if ns is None else ns

    def _get_geometry(self, element: Element) -> Optional[LineString]:
        # Track
        if element.tag == (f"{self.ns}Track"):
            coords = self._get_coordinates(element)
            self._get_geometry_spec(element)
            return LineString(
                coords,
            )
        return None

    def _get_multigeometry(
        self,
        element: Element,
    ) -> Union[MultiLineString, GeometryCollection, None]:
        # MultiTrack
        geoms = []
        if element.tag == (f"{self.ns}MultiTrack"):
            tracks = element.findall(f"{self.ns}Track")
            for track in tracks:
                self._get_geometry_spec(track)
                geoms.append(
                    LineString(
                        self._get_coordinates(track),
                    )
                )

        geom_types = {geom.geom_type for geom in geoms}
        if len(geom_types) > 1:
            return GeometryCollection(geoms)
        if "LineString" in geom_types:
            return MultiLineString.from_linestrings(*geoms)
        return None

    def _get_coordinates(self, element: Element) -> List[PointType]:
        coordinates = element.findall(f"{self.ns}coord")
        if coordinates is not None:
            return [
                cast(PointType, tuple(float(c) for c in coord.text.strip().split()))
                for coord in coordinates
            ]
        return []  # type: ignore[unreachable]


__all__ = ["GxGeometry"]
