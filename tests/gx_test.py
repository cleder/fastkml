# Copyright (C) 2021  Christian Ledermann
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

"""Test the gx classes."""
import datetime

import pygeoif.geometry as geo
from dateutil.tz import tzutc

from fastkml.enums import AltitudeMode
from fastkml.gx import Angle
from fastkml.gx import MultiTrack
from fastkml.gx import Track
from fastkml.gx import TrackItem
from tests.base import Lxml
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""


class TestGetGxGeometry(StdLibrary):
    def test_track(self) -> None:
        doc = """<gx:Track xmlns:kml="http://www.opengis.net/kml/2.2"
                xmlns:gx="http://www.google.com/kml/ext/2.2">
            <when>2020-01-01T00:00:00Z</when>
            <when>2020-01-01T00:10:00Z</when>
            <gx:coord>0.000000 0.000000</gx:coord>
            <gx:coord>1.000000 1.000000</gx:coord>
        </gx:Track>"""
        g = Track.class_from_string(doc, ns="")

        assert g.geometry.__geo_interface__ == {
            "type": "LineString",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": ((0.0, 0.0), (1.0, 1.0)),
        }

    def test_multitrack(self) -> None:
        doc = """
        <gx:MultiTrack xmlns:kml="http://www.opengis.net/kml/2.2"
            xmlns:gx="http://www.google.com/kml/ext/2.2">
          <gx:Track>
            <kml:when>2020-01-01T00:00:00+00:00</kml:when>
            <kml:when>2020-01-01T00:10:00+00:00</kml:when>
            <gx:coord>0.000000 0.000000</gx:coord>
            <gx:coord>1.000000 0.000000</gx:coord>
          </gx:Track>
          <gx:Track>
            <kml:when>2020-01-01T00:10:00+00:00</kml:when>
            <kml:when>2020-01-01T00:20:00+00:00</kml:when>
            <gx:coord>0.000000 1.000000</gx:coord>
            <gx:coord>1.000000 1.000000</gx:coord>
          </gx:Track>
        </gx:MultiTrack>
        """

        mt = MultiTrack.class_from_string(doc, ns="")

        assert mt.geometry == geo.MultiLineString(
            (((0.0, 0.0), (1.0, 0.0)), ((0.0, 1.0), (1.0, 1.0))),
        )
        assert "when>" in mt.to_string()
        assert (
            mt.to_string()
            == MultiTrack(
                ns="",
                id="",
                target_id="",
                extrude=None,
                tessellate=None,
                altitude_mode=None,
                tracks=[
                    Track(
                        ns="{http://www.google.com/kml/ext/2.2}",
                        id="",
                        target_id="",
                        extrude=None,
                        tessellate=None,
                        altitude_mode=None,
                        track_items=[
                            TrackItem(
                                when=datetime.datetime(
                                    2020,
                                    1,
                                    1,
                                    0,
                                    0,
                                    tzinfo=tzutc(),
                                ),
                                coord=geo.Point(0.0, 0.0),
                                angle=None,
                            ),
                            TrackItem(
                                when=datetime.datetime(
                                    2020,
                                    1,
                                    1,
                                    0,
                                    10,
                                    tzinfo=tzutc(),
                                ),
                                coord=geo.Point(1.0, 0.0),
                                angle=None,
                            ),
                        ],
                    ),
                    Track(
                        ns="{http://www.google.com/kml/ext/2.2}",
                        id="",
                        target_id="",
                        extrude=None,
                        tessellate=None,
                        altitude_mode=None,
                        track_items=[
                            TrackItem(
                                when=datetime.datetime(
                                    2020,
                                    1,
                                    1,
                                    0,
                                    10,
                                    tzinfo=tzutc(),
                                ),
                                coord=geo.Point(0.0, 1.0),
                                angle=None,
                            ),
                            TrackItem(
                                when=datetime.datetime(
                                    2020,
                                    1,
                                    1,
                                    0,
                                    20,
                                    tzinfo=tzutc(),
                                ),
                                coord=geo.Point(1.0, 1.0),
                                angle=None,
                            ),
                        ],
                    ),
                ],
                interpolate=None,
            ).to_string()
        )


class TestTrack(StdLibrary):
    """Test gx.Track."""

    def test_track_from_linestring(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))

        track = Track(
            ns="",
            id="track1",
            target_id="track2",
            altitude_mode=AltitudeMode.absolute,
            extrude=True,
            tessellate=True,
            geometry=ls,
        )

        assert "<Track " in track.to_string()
        assert 'id="track1"' in track.to_string()
        assert 'targetId="track2"' in track.to_string()
        assert "extrude>1</extrude>" in track.to_string()
        assert "tessellate>1</tessellate>" in track.to_string()
        assert "altitudeMode>absolute</altitudeMode>" in track.to_string()
        assert "coord>" in track.to_string()
        assert "angles" in track.to_string()
        assert "when" in track.to_string()
        assert "angles>" not in track.to_string()
        assert "when>" not in track.to_string()
        assert repr(track) == (
            "Track(ns='', id='track1', target_id='track2', extrude=True, "
            "tessellate=True, altitude_mode=AltitudeMode.absolute, "
            "track_items=[TrackItem(when=None, coord=Point(1, 2), angle=None), "
            "TrackItem(when=None, coord=Point(2, 0), angle=None)])"
        )

    def test_track_from_track_items(self) -> None:
        time1 = datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        angle = Angle()
        track_items = [TrackItem(when=time1, coord=geo.Point(1, 2), angle=angle)]

        track = Track(
            ns="",
            track_items=track_items,
        )

        assert "when>" in track.to_string()
        assert ">2023-01-01T00:00:00+00:00</" in track.to_string()
        assert "coord>" in track.to_string()
        assert ">1 2</" in track.to_string()
        assert "angles>" in track.to_string()
        assert ">0.0 0.0 0.0</" in track.to_string()
        assert repr(track) == (
            "Track(ns='', id=None, target_id=None, extrude=False, tessellate=False, "
            "altitude_mode=None, "
            "track_items=[TrackItem("
            "when=datetime.datetime(2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "
            "coord=Point(1, 2), angle=Angle(heading=0.0, tilt=0.0, roll=0.0))])"
        )

    def test_track_from_track_items_no_coord(self) -> None:
        time1 = datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        angle = Angle()
        track_items = [TrackItem(when=time1, coord=None, angle=angle)]

        track = Track(
            ns="",
            track_items=track_items,
        )

        assert "when>" in track.to_string()
        assert ">2023-01-01T00:00:00+00:00</" in track.to_string()
        assert "coord>" not in track.to_string()
        assert "coord" in track.to_string()
        assert "angles>" in track.to_string()
        assert ">0.0 0.0 0.0</" in track.to_string()
        assert repr(track) == (
            "Track(ns='', id=None, target_id=None, extrude=False, tessellate=False, "
            "altitude_mode=None, "
            "track_items=[TrackItem("
            "when=datetime.datetime(2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "
            "coord=None, angle=Angle(heading=0.0, tilt=0.0, roll=0.0))])"
        )

    def test_track_from_str(self) -> None:
        doc = """
            <gx:Track xmlns:gx="http://www.google.com/kml/ext/2.2"
              xmlns:kml="http://www.opengis.net/kml/2.2">
            <kml:when>2010-05-28T02:02:09Z</kml:when>
            <kml:when>2010-05-28T02:02:35Z</kml:when>
            <kml:when>2010-05-28T02:02:44Z</kml:when>
            <kml:when>2010-05-28T02:02:53Z</kml:when>
            <kml:when>2010-05-28T02:02:54Z</kml:when>
            <kml:when>2010-05-28T02:02:55Z</kml:when>
            <kml:when>2010-05-28T02:02:56Z</kml:when>
            <kml:when />
            <gx:angles>45.54676 66.2342 77.0</gx:angles>
            <gx:angles />
            <gx:angles>1 2 3</gx:angles>
            <gx:angles>1 2 3</gx:angles>
            <gx:angles>1 2 3</gx:angles>
            <gx:angles>1 2 3</gx:angles>
            <gx:angles>1 2 3</gx:angles>
            <gx:angles>1 2 3</gx:angles>
            <gx:coord>-122.207881 37.371915 156.000000</gx:coord>
            <gx:coord>-122.205712 37.373288 152.000000</gx:coord>
            <gx:coord>-122.204678 37.373939 147.000000</gx:coord>
            <gx:coord>-122.203572 37.374630 142.199997</gx:coord>
            <gx:coord />
            <gx:coord>-122.203451 37.374706 141.800003</gx:coord>
            <gx:coord>-122.203329 37.374780 141.199997</gx:coord>
            <gx:coord>-122.203207 37.374857 140.199997</gx:coord>
            </gx:Track>
        """
        expected_track = Track(
            ns="",
            id="",
            target_id="",
            extrude=None,
            tessellate=None,
            altitude_mode=None,
            track_items=[
                TrackItem(
                    when=datetime.datetime(2010, 5, 28, 2, 2, 9, tzinfo=tzutc()),
                    coord=geo.Point(-122.207881, 37.371915, 156.0),
                    angle=Angle(heading=45.54676, tilt=66.2342, roll=77.0),
                ),
                TrackItem(
                    when=datetime.datetime(2010, 5, 28, 2, 2, 35, tzinfo=tzutc()),
                    coord=geo.Point(-122.205712, 37.373288, 152.0),
                    angle=None,
                ),
                TrackItem(
                    when=datetime.datetime(2010, 5, 28, 2, 2, 44, tzinfo=tzutc()),
                    coord=geo.Point(-122.204678, 37.373939, 147.0),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=datetime.datetime(2010, 5, 28, 2, 2, 53, tzinfo=tzutc()),
                    coord=geo.Point(-122.203572, 37.37463, 142.199997),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=datetime.datetime(2010, 5, 28, 2, 2, 54, tzinfo=tzutc()),
                    coord=None,
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=datetime.datetime(2010, 5, 28, 2, 2, 55, tzinfo=tzutc()),
                    coord=geo.Point(-122.203451, 37.374706, 141.800003),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=datetime.datetime(2010, 5, 28, 2, 2, 56, tzinfo=tzutc()),
                    coord=geo.Point(-122.203329, 37.37478, 141.199997),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=None,
                    coord=geo.Point(-122.203207, 37.374857, 140.199997),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
            ],
        )

        track = Track.class_from_string(doc, ns="")

        assert track.geometry == geo.LineString(
            (
                (-122.207881, 37.371915, 156.0),
                (-122.205712, 37.373288, 152.0),
                (-122.204678, 37.373939, 147.0),
                (-122.203572, 37.37463, 142.199997),
                (-122.203451, 37.374706, 141.800003),
                (-122.203329, 37.37478, 141.199997),
                (-122.203207, 37.374857, 140.199997),
            ),
        )
        assert track.to_string() == expected_track.to_string()


class TestMultiTrack(StdLibrary):
    def test_from_multilinestring(self) -> None:
        lines = geo.MultiLineString(
            ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
        )

        mt = MultiTrack(geometry=lines, ns="")

        assert repr(mt) == repr(
            MultiTrack(
                ns="",
                id=None,
                target_id=None,
                extrude=False,
                tessellate=False,
                altitude_mode=None,
                tracks=[
                    Track(
                        ns="",
                        id=None,
                        target_id=None,
                        extrude=False,
                        tessellate=False,
                        altitude_mode=None,
                        track_items=[
                            TrackItem(when=None, coord=geo.Point(0, 0), angle=None),
                            TrackItem(when=None, coord=geo.Point(1, 1), angle=None),
                            TrackItem(when=None, coord=geo.Point(1, 2), angle=None),
                            TrackItem(when=None, coord=geo.Point(2, 2), angle=None),
                        ],
                    ),
                    Track(
                        ns="",
                        id=None,
                        target_id=None,
                        extrude=False,
                        tessellate=False,
                        altitude_mode=None,
                        track_items=[
                            TrackItem(when=None, coord=geo.Point(0.0, 0.0), angle=None),
                            TrackItem(when=None, coord=geo.Point(1.0, 2.0), angle=None),
                        ],
                    ),
                ],
            ),
        )

    def test_multitrack(self) -> None:
        track = MultiTrack(
            ns="",
            interpolate=True,
            tracks=[
                Track(
                    ns="",
                    track_items=[
                        TrackItem(when=None, coord=geo.Point(0, 0), angle=None),
                        TrackItem(when=None, coord=geo.Point(1, 1), angle=None),
                        TrackItem(when=None, coord=geo.Point(1, 2), angle=None),
                        TrackItem(when=None, coord=geo.Point(2, 2), angle=None),
                    ],
                ),
                Track(
                    ns="",
                    track_items=[
                        TrackItem(
                            when=datetime.datetime(
                                2010,
                                5,
                                28,
                                2,
                                2,
                                55,
                                tzinfo=tzutc(),
                            ),
                            coord=geo.Point(-122.203451, 37.374706, 141.800003),
                            angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                        ),
                        TrackItem(
                            when=datetime.datetime(
                                2010,
                                5,
                                28,
                                2,
                                2,
                                56,
                                tzinfo=tzutc(),
                            ),
                            coord=geo.Point(-122.203329, 37.37478, 141.199997),
                            angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                        ),
                    ],
                ),
            ],
        )

        assert track.geometry == geo.MultiLineString(
            (
                ((0, 0), (1, 1), (1, 2), (2, 2)),
                (
                    (-122.203451, 37.374706, 141.800003),
                    (-122.203329, 37.37478, 141.199997),
                ),
            ),
        )
        assert "MultiTrack>" in track.to_string()
        assert "interpolate>1</" in track.to_string()
        assert "Track>" in track.to_string()
        assert "coord>" in track.to_string()
        assert "angles>" in track.to_string()
        assert "when>" in track.to_string()


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""


class TestLxmlGetGxGeometry(Lxml, TestGetGxGeometry):
    """Test with lxml."""


class TestLxmlTrack(Lxml, TestTrack):
    """Test with lxml."""


class TestLxmlMultiTrack(Lxml, TestMultiTrack):
    """Test with lxml."""
