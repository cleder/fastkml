# Copyright (C) 2022 - 2023 Christian Ledermann
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

"""Test the times classes."""
import datetime

import pytest
from dateutil.tz import tzoffset
from dateutil.tz import tzutc

import fastkml as kml
from fastkml.enums import DateTimeResolution
from fastkml.times import KmlDateTime
from tests.base import Lxml
from tests.base import StdLibrary


class TestDateTime(StdLibrary):
    """KmlDateTime implementation is independent of XML parser."""

    def test_kml_datetime_year(self):
        dt = datetime.datetime(2000, 1, 1)

        kdt = KmlDateTime(dt, DateTimeResolution.year)

        assert kdt.resolution == DateTimeResolution.year
        assert str(kdt) == "2000"
        assert bool(kdt)

    def test_kml_datetime_year_month(self):
        dt = datetime.datetime(2000, 3, 1)

        kdt = KmlDateTime(dt, DateTimeResolution.year_month)

        assert kdt.resolution == DateTimeResolution.year_month
        assert str(kdt) == "2000-03"
        assert bool(kdt)

    def test_kml_datetime_date(self):
        dt = datetime.datetime.now()

        kdt = KmlDateTime(dt, DateTimeResolution.date)

        assert kdt.resolution == DateTimeResolution.date
        assert str(kdt) == dt.date().isoformat()
        assert bool(kdt)

    def test_kml_datetime_date_implicit(self):
        dt = datetime.date.today()

        kdt = KmlDateTime(dt)

        assert kdt.resolution == DateTimeResolution.date
        assert str(kdt) == dt.isoformat()
        assert bool(kdt)

    def test_kml_datetime_datetime(self):
        dt = datetime.datetime.now()

        kdt = KmlDateTime(dt, DateTimeResolution.datetime)

        assert kdt.resolution == DateTimeResolution.datetime
        assert str(kdt) == dt.isoformat()
        assert bool(kdt)

    def test_kml_datetime_datetime_implicit(self):
        dt = datetime.datetime.now()

        kdt = KmlDateTime(dt)

        assert kdt.resolution == DateTimeResolution.datetime
        assert str(kdt) == dt.isoformat()
        assert bool(kdt)

    def test_kml_datetime_no_datetime(self):
        """When we pass dt as None bool() should return False."""
        kdt = KmlDateTime(None)

        assert kdt.resolution == DateTimeResolution.date
        assert not bool(kdt)
        with pytest.raises(AttributeError):
            str(kdt)

    def test_parse_year(self):
        dt = KmlDateTime.parse("2000")

        assert dt.resolution == DateTimeResolution.year
        assert dt.dt == datetime.datetime(2000, 1, 1)

    def test_parse_year_0(self):
        with pytest.raises(ValueError):
            KmlDateTime.parse("0000")

    def test_parse_year_month(self):
        dt = KmlDateTime.parse("2000-03")

        assert dt.resolution == DateTimeResolution.year_month
        assert dt.dt == datetime.datetime(2000, 3, 1)

    def test_parse_year_month_no_dash(self):
        dt = KmlDateTime.parse("200004")

        assert dt.resolution == DateTimeResolution.year_month
        assert dt.dt == datetime.datetime(2000, 4, 1)

    def test_parse_year_month_0(self):
        with pytest.raises(ValueError):
            KmlDateTime.parse("2000-00")

    def test_parse_year_month_13(self):
        with pytest.raises(ValueError):
            KmlDateTime.parse("2000-13")

    def test_parse_year_month_day(self):
        dt = KmlDateTime.parse("2000-03-01")

        assert dt.resolution == DateTimeResolution.date
        assert dt.dt == datetime.datetime(2000, 3, 1)

    def test_parse_year_month_day_no_dash(self):
        dt = KmlDateTime.parse("20000401")

        assert dt.resolution == DateTimeResolution.date
        assert dt.dt == datetime.datetime(2000, 4, 1)

    def test_parse_year_month_day_0(self):
        with pytest.raises(ValueError):
            KmlDateTime.parse("2000-05-00")

    def test_parse_datetime_utc(self):
        dt = KmlDateTime.parse("1997-07-16T07:30:15Z")

        assert dt.resolution == DateTimeResolution.datetime
        assert dt.dt == datetime.datetime(1997, 7, 16, 7, 30, 15, tzinfo=tzutc())

    def test_parse_datetime_with_tz(self):
        dt = KmlDateTime.parse("1997-07-16T07:30:15+01:00")

        assert dt.resolution == DateTimeResolution.datetime
        assert dt.dt == datetime.datetime(
            1997, 7, 16, 7, 30, 15, tzinfo=tzoffset(None, 3600)
        )

    def test_parse_datetime_with_tz_no_colon(self):
        dt = KmlDateTime.parse("1997-07-16T07:30:15+0100")

        assert dt.resolution == DateTimeResolution.datetime
        assert dt.dt == datetime.datetime(
            1997, 7, 16, 7, 30, 15, tzinfo=tzoffset(None, 3600)
        )

    def test_parse_datetime_no_tz(self):
        dt = KmlDateTime.parse("1997-07-16T07:30:15")

        assert dt.resolution == DateTimeResolution.datetime
        assert dt.dt == datetime.datetime(1997, 7, 16, 7, 30, 15)

    def test_parse_datetime_empty(self):
        assert KmlDateTime.parse("") is None

    def test_parse_year_month_5(self):
        """Test that a single digit month is invalid."""
        assert KmlDateTime.parse("19973") is None


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_timestamp(self):
        now = datetime.datetime.now()
        dt = KmlDateTime(now)
        ts = kml.TimeStamp(timestamp=dt)
        assert ts.timestamp.dt == now
        assert ts.timestamp.resolution == DateTimeResolution.datetime
        assert "TimeStamp>" in str(ts.to_string())
        assert "when>" in str(ts.to_string())
        assert now.isoformat() in str(ts.to_string())
        y2k = KmlDateTime(datetime.date(2000, 1, 1))
        ts = kml.TimeStamp(timestamp=y2k)
        assert ts.timestamp == y2k
        assert "2000-01-01" in str(ts.to_string())

    def test_timespan(self):
        now = KmlDateTime(datetime.datetime.now())
        y2k = KmlDateTime(datetime.datetime(2000, 1, 1))
        ts = kml.TimeSpan(end=now, begin=y2k)
        assert ts.end == now
        assert ts.begin == y2k
        assert "TimeSpan>" in str(ts.to_string())
        assert "begin>" in str(ts.to_string())
        assert "end>" in str(ts.to_string())
        assert now.dt.isoformat() in str(ts.to_string())
        assert y2k.dt.isoformat() in str(ts.to_string())
        ts.end = None
        assert now.dt.isoformat() not in str(ts.to_string())
        assert y2k.dt.isoformat() in str(ts.to_string())
        ts.begin = None
        pytest.raises(ValueError, ts.to_string)

    def test_feature_timestamp(self):
        now = datetime.datetime.now()
        f = kml.Document()
        f.time_stamp = KmlDateTime(now)
        assert f.time_stamp.dt == now
        assert now.isoformat() in str(f.to_string())
        assert "TimeStamp>" in str(f.to_string())
        assert "when>" in str(f.to_string())
        f.time_stamp = KmlDateTime(now.date())
        assert now.date().isoformat() in str(f.to_string())
        assert now.isoformat() not in str(f.to_string())
        f.time_stamp = None
        assert "TimeStamp>" not in str(f.to_string())

    def test_feature_timespan(self):
        now = datetime.datetime.now()
        y2k = datetime.datetime(2000, 1, 1)
        f = kml.Document()
        f.begin = KmlDateTime(y2k)
        f.end = KmlDateTime(now)
        assert f.begin == KmlDateTime(y2k)
        assert f.end == KmlDateTime(now)
        assert now.isoformat() in str(f.to_string())
        assert "2000-01-01" in str(f.to_string())
        assert "TimeSpan>" in str(f.to_string())
        assert "begin>" in str(f.to_string())
        assert "end>" in str(f.to_string())
        f.end = None
        assert now.isoformat() not in str(f.to_string())
        assert "2000-01-01" in str(f.to_string())
        assert "TimeSpan>" in str(f.to_string())
        assert "begin>" in str(f.to_string())
        assert "end>" not in str(f.to_string())
        f.begin = None
        assert "TimeSpan>" not in str(f.to_string())

    def test_feature_timespan_stamp(self):
        now = datetime.datetime.now()
        y2k = datetime.date(2000, 1, 1)
        f = kml.Document()
        f.begin = KmlDateTime(y2k)
        f.end = KmlDateTime(now)
        assert now.isoformat() in str(f.to_string())
        assert "2000-01-01" in str(f.to_string())
        assert "TimeSpan>" in str(f.to_string())
        assert "begin>" in str(f.to_string())
        assert "end>" in str(f.to_string())
        assert "TimeStamp>" not in str(f.to_string())
        assert "when>" not in str(f.to_string())
        # when we set a timestamp an existing timespan will be deleted
        f.time_stamp = KmlDateTime(now)
        assert now.isoformat() in str(f.to_string())
        assert "TimeStamp>" in str(f.to_string())
        assert "when>" in str(f.to_string())
        assert "2000-01-01" not in str(f.to_string())
        assert "TimeSpan>" not in str(f.to_string())
        assert "begin>" not in str(f.to_string())
        assert "end>" not in str(f.to_string())
        # when we set a timespan an existing timestamp will be deleted
        f.end = y2k
        assert now.isoformat() not in str(f.to_string())
        assert "2000-01-01" in str(f.to_string())
        assert "TimeSpan>" in str(f.to_string())
        assert "begin>" not in str(f.to_string())
        assert "end>" in str(f.to_string())
        assert "TimeStamp>" not in str(f.to_string())
        assert "when>" not in str(f.to_string())
        # We manipulate our Feature so it has timespan and stamp
        ts = kml.TimeStamp(timestamp=now)
        f._timestamp = ts
        # this raises an exception as only either timespan or timestamp
        # are allowed not both
        pytest.raises(ValueError, f.to_string)

    def test_read_timestamp(self):
        ts = kml.TimeStamp(ns="")
        doc = """
        <TimeStamp>
          <when>1997</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        assert ts.timestamp.resolution == DateTimeResolution.year
        assert ts.timestamp.dt == datetime.datetime(1997, 1, 1, 0, 0)
        doc = """
        <TimeStamp>
          <when>1997-07</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        assert ts.timestamp.resolution == DateTimeResolution.year_month
        assert ts.timestamp.dt == datetime.datetime(1997, 7, 1, 0, 0)
        doc = """
        <TimeStamp>
          <when>199808</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        assert ts.timestamp.resolution == DateTimeResolution.year_month
        assert ts.timestamp.dt == datetime.datetime(1998, 8, 1, 0, 0)
        doc = """
        <TimeStamp>
          <when>1997-07-16</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        assert ts.timestamp.resolution == DateTimeResolution.date
        assert ts.timestamp.dt == datetime.datetime(1997, 7, 16, 0, 0)
        # dateTime (YYYY-MM-DDThh:mm:ssZ)
        # Here, T is the separator between the calendar and the hourly notation
        # of time, and Z indicates UTC. (Seconds are required.)
        doc = """
        <TimeStamp>
          <when>1997-07-16T07:30:15Z</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        assert ts.timestamp.resolution == DateTimeResolution.datetime
        assert ts.timestamp.dt == datetime.datetime(
            1997, 7, 16, 7, 30, 15, tzinfo=tzutc()
        )
        doc = """
        <TimeStamp>
          <when>1997-07-16T10:30:15+03:00</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        assert ts.timestamp.resolution == DateTimeResolution.datetime
        assert ts.timestamp.dt == datetime.datetime(
            1997, 7, 16, 10, 30, 15, tzinfo=tzoffset(None, 10800)
        )

    def test_read_timespan(self):
        ts = kml.TimeSpan(ns="")
        doc = """
        <TimeSpan>
            <begin>1876-08-01</begin>
            <end>1997-07-16T07:30:15Z</end>
        </TimeSpan>
        """

        ts.from_string(doc)
        assert ts.begin.resolution == DateTimeResolution.date
        assert ts.begin.dt == datetime.datetime(1876, 8, 1, 0, 0)
        assert ts.end.resolution == DateTimeResolution.datetime
        assert ts.end.dt == datetime.datetime(1997, 7, 16, 7, 30, 15, tzinfo=tzutc())

    def test_featurefromstring(self):
        d = kml.Document(ns="")
        doc = """<Document>
          <name>Document.kml</name>
          <open>1</open>
          <TimeStamp>
            <when>1997-07-16T10:30:15+03:00</when>
          </TimeStamp>
          <TimeSpan>
            <begin>1876-08-01</begin>
            <end>1997-07-16T07:30:15Z</end>
          </TimeSpan>
        </Document>"""

        d.from_string(doc)


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
