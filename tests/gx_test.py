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
import pytest
from dateutil.tz import tzoffset
from dateutil.tz import tzutc

from fastkml.gx import Angle
from fastkml.gx import MultiTrack
from fastkml.gx import Track
from fastkml.gx import TrackItem
from fastkml.times import KmlDateTime
from tests.base import Lxml
from tests.base import StdLibrary


class TestGetGxGeometry(StdLibrary):
    def test_track(self) -> None:
        doc = """<gx:Track xmlns:kml="http://www.opengis.net/kml/2.2"
                xmlns:gx="http://www.google.com/kml/ext/2.2">
            <when>2020-01-01T00:00:00Z</when>
            <when>2020-01-01T00:10:00Z</when>
            <gx:coord>0.000000 0.000000</gx:coord>
            <gx:coord>1.000000 1.000000</gx:coord>
        </gx:Track>"""
        g = Track.from_string(doc, ns="")

        assert g.geometry.__geo_interface__ == {
            "type": "LineString",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": ((0.0, 0.0), (1.0, 1.0)),
        }

    def test_track_etree_element(self) -> None:
        g = Track()

        g.etree_element()

        assert g.track_items == []

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

        mt = MultiTrack.from_string(doc)

        assert mt.geometry == geo.MultiLineString(
            (((0.0, 0.0), (1.0, 0.0)), ((0.0, 1.0), (1.0, 1.0))),
        )
        assert "when>" in mt.to_string()
        assert mt == MultiTrack(
            tracks=[
                Track(
                    track_items=[
                        TrackItem(
                            when=KmlDateTime(
                                dt=datetime.datetime(
                                    2020,
                                    1,
                                    1,
                                    0,
                                    0,
                                    tzinfo=tzoffset(None, 0),
                                ),
                            ),
                            coord=geo.Point(0.0, 0.0),
                            angle=Angle(heading=0.0, tilt=0.0, roll=0.0),
                        ),
                        TrackItem(
                            when=KmlDateTime(
                                dt=datetime.datetime(
                                    2020,
                                    1,
                                    1,
                                    0,
                                    10,
                                    tzinfo=tzoffset(None, 0),
                                ),
                            ),
                            coord=geo.Point(1.0, 0.0),
                            angle=Angle(heading=0.0, tilt=0.0, roll=0.0),
                        ),
                    ],
                ),
                Track(
                    track_items=[
                        TrackItem(
                            when=KmlDateTime(
                                dt=datetime.datetime(
                                    2020,
                                    1,
                                    1,
                                    0,
                                    10,
                                    tzinfo=tzoffset(None, 0),
                                ),
                            ),
                            coord=geo.Point(0.0, 1.0),
                            angle=Angle(heading=0.0, tilt=0.0, roll=0.0),
                        ),
                        TrackItem(
                            when=KmlDateTime(
                                dt=datetime.datetime(
                                    2020,
                                    1,
                                    1,
                                    0,
                                    20,
                                    tzinfo=tzoffset(None, 0),
                                ),
                            ),
                            coord=geo.Point(1.0, 1.0),
                            angle=Angle(heading=0.0, tilt=0.0, roll=0.0),
                        ),
                    ],
                ),
            ],
        )


class TestTrack(StdLibrary):
    """Test gx.Track."""

    def test_track_from_track_items(self) -> None:
        time1 = KmlDateTime(
            datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
        )
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

    def test_track_from_whens_and_coords(self) -> None:
        whens = [
            KmlDateTime(
                datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
            ),
        ]
        coords = [(1, 2)]

        track = Track(
            whens=whens,
            coords=coords,
        )

        assert "when>" in track.to_string()
        assert ">2023-01-01T00:00:00+00:00</" in track.to_string()
        assert "coord>" in track.to_string()
        assert ">1 2</" in track.to_string()
        assert track.coords == ((1, 2),)

    def test_track_from_whens_and_coords_and_track_items(self) -> None:
        whens = [
            KmlDateTime(
                datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
            ),
        ]
        coords = [(1, 2)]
        time1 = KmlDateTime(
            datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
        )
        angle = Angle()
        track_items = [TrackItem(when=time1, coord=geo.Point(1, 2), angle=angle)]

        with pytest.raises(
            ValueError,
            match="^Cannot specify both geometry and track_items$",
        ):
            Track(
                whens=whens,
                coords=coords,
                track_items=track_items,
            )

    def test_track_precision(self) -> None:
        track = Track(
            id="x",
            target_id="y",
            altitude_mode=None,
            track_items=[
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 9, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.207881, 37.371915, 156.0),
                    angle=Angle(heading=45.54676, tilt=66.2342, roll=77.0),
                ),
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 35, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.205712, 37.373288, 152.0),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
            ],
        )

        xml = track.to_string(precision=2)
        assert "angles>45.55 66.23 77.00</" in xml
        assert "angles>1.00 2.00 3.00</" in xml
        assert "coord>-122.21 37.37 156.00</" in xml
        assert "coord>-122.21 37.37 152.00</" in xml

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
            <kml:when>2010-05-28T02:02:57Z</kml:when>
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
            <gx:coord>-112.203451 37.374690 141.800000</gx:coord>
            <gx:coord>-122.203451 37.374706 141.800003</gx:coord>
            <gx:coord>-122.203329 37.374780 141.199997</gx:coord>
            <gx:coord>-122.203207 37.374857 140.199997</gx:coord>
            </gx:Track>
        """
        expected_track = Track(
            ns="{http://www.google.com/kml/ext/2.2}",
            name_spaces={
                "kml": "{http://www.opengis.net/kml/2.2}",
                "atom": "{http://www.w3.org/2005/Atom}",
                "gx": "{http://www.google.com/kml/ext/2.2}",
            },
            id="",
            target_id="",
            altitude_mode=None,
            track_items=[
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 9, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.207881, 37.371915, 156.0),
                    angle=Angle(heading=45.54676, tilt=66.2342, roll=77.0),
                ),
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 35, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.205712, 37.373288, 152.0),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 44, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.204678, 37.373939, 147.0),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 53, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.203572, 37.37463, 142.199997),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 54, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-112.203451, 37.37469, 141.8),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 55, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.203451, 37.374706, 141.800003),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 56, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.203329, 37.37478, 141.199997),
                    angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                ),
                TrackItem(
                    when=KmlDateTime(
                        dt=datetime.datetime(2010, 5, 28, 2, 2, 57, tzinfo=tzutc()),
                    ),
                    coord=geo.Point(-122.203207, 37.374857, 140.199997),
                    angle=Angle(heading=0.0, tilt=0.0, roll=0.0),
                ),
            ],
        )

        track = Track.from_string(doc)

        assert track.geometry == geo.LineString(
            (
                (-122.207881, 37.371915, 156.0),
                (-122.205712, 37.373288, 152.0),
                (-122.204678, 37.373939, 147.0),
                (-122.203572, 37.37463, 142.199997),
                (-112.203451, 37.37469, 141.8),
                (-122.203451, 37.374706, 141.800003),
                (-122.203329, 37.37478, 141.199997),
                (-122.203207, 37.374857, 140.199997),
            ),
        )

        assert track.to_string() == expected_track.to_string()

    def test_track_from_str_invalid_when(self) -> None:
        doc = """
            <gx:Track xmlns:gx="http://www.google.com/kml/ext/2.2"
              xmlns:kml="http://www.opengis.net/kml/2.2">
            <kml:when>2010-02-32T02:02:09Z</kml:when>
            <gx:angles>45.54676 66.2342 77.0</gx:angles>
            <gx:coord>-122.207881 37.371915 156.000000</gx:coord>
            </gx:Track>
        """

        track = Track.from_string(doc, strict=False)

        assert track.track_items == []

    def test_track_from_str_invalid_coord(self) -> None:
        doc = """
            <gx:Track xmlns:gx="http://www.google.com/kml/ext/2.2"
              xmlns:kml="http://www.opengis.net/kml/2.2">
            <kml:when>2010-02-14T02:02:09Z</kml:when>
            <gx:angles>45.54676 66.2342 77.0</gx:angles>
            <gx:coord>XYZ 37.371915 156.000000</gx:coord>
            </gx:Track>
        """

        track = Track.from_string(doc, strict=False)

        assert track.track_items == []

    def test_track_from_str_extended_data(self) -> None:
        doc = (
            '<gx:Track xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<when>2010-05-28T02:02:09Z</when>"
            "<when>2010-05-28T02:02:35Z</when>"
            "<when>2010-05-28T02:02:44Z</when>"
            "<when>2010-05-28T02:02:53Z</when>"
            "<when>2010-05-28T02:02:54Z</when>"
            "<when>2010-05-28T02:02:55Z</when>"
            "<when>2010-05-28T02:02:56Z</when>"
            "<gx:coord>-122.207881 37.371915 156.000000</gx:coord>"
            "<gx:coord>-122.205712 37.373288 152.000000</gx:coord>"
            "<gx:coord>-122.204678 37.373939 147.000000</gx:coord>"
            "<gx:coord>-122.203572 37.374630 142.199997</gx:coord>"
            "<gx:coord>-122.203451 37.374706 141.800003</gx:coord>"
            "<gx:coord>-122.203329 37.374780 141.199997</gx:coord>"
            "<gx:coord>-122.203207 37.374857 140.199997</gx:coord>"
            "<kml:ExtendedData>"
            '<kml:SchemaData schemaUrl="#schema">'
            '<gx:SimpleArrayData name="cadence">'
            "<gx:value>86</gx:value>"
            "<gx:value>103</gx:value>"
            "<gx:value>108</gx:value>"
            "<gx:value>113</gx:value>"
            "<gx:value>113</gx:value>"
            "<gx:value>113</gx:value>"
            "<gx:value>113</gx:value>"
            "</gx:SimpleArrayData>"
            '<gx:SimpleArrayData name="heartrate">'
            "<gx:value>181</gx:value>"
            "<gx:value>177</gx:value>"
            "<gx:value>175</gx:value>"
            "<gx:value>173</gx:value>"
            "<gx:value>173</gx:value>"
            "<gx:value>173</gx:value>"
            "<gx:value>173</gx:value>"
            "</gx:SimpleArrayData>"
            '<gx:SimpleArrayData name="power">'
            "<gx:value>327.0</gx:value>"
            "<gx:value>177.0</gx:value>"
            "<gx:value>179.0</gx:value>"
            "<gx:value>162.0</gx:value>"
            "<gx:value>166.0</gx:value>"
            "<gx:value>177.0</gx:value>"
            "<gx:value>183.0</gx:value>"
            "</gx:SimpleArrayData>"
            "</kml:SchemaData>"
            "</kml:ExtendedData>"
            "</gx:Track>"
        )
        track = Track.from_string(doc)
        assert track.extended_data == ""


class TestMultiTrack(StdLibrary):
    """Test gx.MultiTrack."""

    def test_multitrack(self) -> None:
        track = MultiTrack(
            ns="",
            interpolate=True,
            tracks=[
                Track(
                    ns="",
                    track_items=[
                        TrackItem(
                            when=KmlDateTime(
                                datetime.datetime(
                                    2010,
                                    5,
                                    28,
                                    2,
                                    2,
                                    55,
                                    tzinfo=tzutc(),
                                ),
                            ),
                            coord=geo.Point(0, 0),
                            angle=None,
                        ),
                        TrackItem(
                            when=KmlDateTime(
                                datetime.datetime(
                                    2010,
                                    5,
                                    28,
                                    2,
                                    2,
                                    56,
                                    tzinfo=tzutc(),
                                ),
                            ),
                            coord=geo.Point(1, 1),
                            angle=None,
                        ),
                        TrackItem(
                            when=KmlDateTime(
                                datetime.datetime(
                                    2010,
                                    5,
                                    28,
                                    2,
                                    2,
                                    57,
                                    tzinfo=tzutc(),
                                ),
                            ),
                            coord=geo.Point(1, 2),
                            angle=None,
                        ),
                        TrackItem(
                            when=KmlDateTime(
                                datetime.datetime(
                                    2010,
                                    5,
                                    28,
                                    2,
                                    2,
                                    58,
                                    tzinfo=tzutc(),
                                ),
                            ),
                            coord=geo.Point(2, 2),
                            angle=None,
                        ),
                    ],
                ),
                Track(
                    ns="",
                    track_items=[
                        TrackItem(
                            when=KmlDateTime(
                                datetime.datetime(
                                    2010,
                                    5,
                                    28,
                                    2,
                                    2,
                                    55,
                                    tzinfo=tzutc(),
                                ),
                            ),
                            coord=geo.Point(-122.203451, 37.374706, 141.800003),
                            angle=Angle(heading=1.0, tilt=2.0, roll=3.0),
                        ),
                        TrackItem(
                            when=KmlDateTime(
                                datetime.datetime(
                                    2010,
                                    5,
                                    28,
                                    2,
                                    2,
                                    56,
                                    tzinfo=tzutc(),
                                ),
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


class TestLxmlGetGxGeometry(Lxml, TestGetGxGeometry):
    """Test with lxml."""


class TestLxmlTrack(Lxml, TestTrack):
    """Test with lxml."""


class TestLxmlMultiTrack(Lxml, TestMultiTrack):
    """Test with lxml."""
