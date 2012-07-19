# -*- coding: utf-8 -*-
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

"""
With the launch of Google Earth 5.0, Google has provided extensions to KML
to support a number of new features. These extensions use the gx prefix
and the following namespace URI:

 xmlns:gx="http://www.google.com/kml/ext/2.2"

This namespace URI must be added to the <kml> element in any KML file
using gx-prefixed elements:

<kml xmlns="http://www.opengis.net/kml/2.2"
 xmlns:gx="http://www.google.com/kml/ext/2.2">
Extensions to KML may not be supported in all geo-browsers. If your
browser doesn't support particular extensions, the data in those
extensions should be silently ignored, and the rest of the KML file
should load without errors.

Elements that currently use the gx prefix are:

gx:altitudeMode
gx:altitudeOffset
gx:angles
gx:AnimatedUpdate
gx:balloonVisibility
gx:coord
gx:delayedStart
gx:drawOrder
gx:duration
gx:FlyTo
gx:flyToMode
gx:h
gx:horizFov
gx:interpolate
gx:labelVisibility
gx:LatLonQuad
gx:MultiTrack
gx:vieweroptions
gx:outerColor
gx:outerWidth
gx:physicalWidth
gx:Playlist
gx:playMode
gx:SoundCue
gx:TimeSpan
gx:TimeStamp
gx:Tour
gx:TourControl
gx:TourPrimitive
gx:Track
gx:ViewerOptions
gx:w
gx:Wait
gx:x
gx:y
The complete XML schema for elements in this extension namespace is
located at http://developers.google.com/kml/schema/kml22gx.xsd.
"""
