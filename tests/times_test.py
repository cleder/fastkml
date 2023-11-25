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

    def test_kml_datetime_year(self) -> None:
        dt = datetime.datetime(2000, 1, 1)

        kdt = KmlDateTime(dt, DateTimeResolution.year)

        assert kdt.resolution == DateTimeResolution.year
        assert str(kdt) == "2000"
        assert bool(kdt)

    def test_kml_datetime_year_month(self) -> None:
        dt = datetime.datetime(2000, 3, 1)

        kdt = KmlDateTime(dt, DateTimeResolution.year_month)

        assert kdt.resolution == DateTimeResolution.year_month
        assert str(kdt) == "2000-03"
        assert bool(kdt)

    def test_kml_datetime_date(self) -> None:
        dt = datetime.datetime.now()

        kdt = KmlDateTime(dt, DateTimeResolution.date)

        assert kdt.resolution == DateTimeResolution.date
        assert str(kdt) == dt.date().isoformat()
        assert bool(kdt)

    def test_kml_datetime_date_implicit(self) -> None:
        dt = datetime.date.today()

        kdt = KmlDateTime(dt)

        assert kdt.resolution == DateTimeResolution.date
        assert str(kdt) == dt.isoformat()
        assert bool(kdt)

    def test_kml_datetime_datetime(self) -> None:
        dt = datetime.datetime.now()

        kdt = KmlDateTime(dt, DateTimeResolution.datetime)

        assert kdt.resolution == DateTimeResolution.datetime
        assert str(kdt) == dt.isoformat()
        assert bool(kdt)

    def test_kml_datetime_datetime_implicit(self) -> None:
        dt = datetime.datetime.now()

        kdt = KmlDateTime(dt)

        assert kdt.resolution == DateTimeResolution.datetime
        assert str(kdt) == dt.isoformat()
        assert bool(kdt)

    def test_kml_datetime_no_datetime(self) -> None:
        """When we pass dt as None bool() should return False."""
        kdt = KmlDateTime(None)

        assert kdt.resolution == DateTimeResolution.date
        assert not bool(kdt)
        with pytest.raises(AttributeError):
            str(kdt)

    def test_parse_year(self) -> None:
        dt = KmlDateTime.parse("2000")

        assert dt.resolution == DateTimeResolution.year
        assert dt.dt == datetime.datetime(2000, 1, 1, tzinfo=tzutc())

    def test_parse_year_0(self) -> None:
        with pytest.raises(ValueError):
            KmlDateTime.parse("0000")

    def test_parse_year_month(self) -> None:
        dt = KmlDateTime.parse("2000-03")

        assert dt.resolution == DateTimeResolution.year_month
        assert dt.dt == datetime.datetime(2000, 3, 1, tzinfo=tzutc())

    def test_parse_year_month_no_dash(self) -> None:
        dt = KmlDateTime.parse("200004")

        assert dt.resolution == DateTimeResolution.year_month
        assert dt.dt == datetime.datetime(2000, 4, 1, tzinfo=tzutc())

    def test_parse_year_month_0(self) -> None:
        with pytest.raises(ValueError):
            KmlDateTime.parse("2000-00")

    def test_parse_year_month_13(self) -> None:
        with pytest.raises(ValueError):
            KmlDateTime.parse("2000-13")

    def test_parse_year_month_day(self) -> None:
        dt = KmlDateTime.parse("2000-03-01")

        assert dt.resolution == DateTimeResolution.date
        assert dt.dt == datetime.datetime(2000, 3, 1, tzinfo=tzutc())

    def test_parse_year_month_day_no_dash(self) -> None:
        dt = KmlDateTime.parse("20000401")

        assert dt.resolution == DateTimeResolution.date
        assert dt.dt == datetime.datetime(2000, 4, 1, tzinfo=tzutc())

    def test_parse_year_month_day_0(self) -> None:
        with pytest.raises(ValueError):
            KmlDateTime.parse("2000-05-00")

    def test_parse_datetime_utc(self) -> None:
        dt = KmlDateTime.parse("1997-07-16T07:30:15Z")

        assert dt.resolution == DateTimeResolution.datetime
        assert dt.dt == datetime.datetime(1997, 7, 16, 7, 30, 15, tzinfo=tzutc())

    def test_parse_datetime_with_tz(self) -> None:
        dt = KmlDateTime.parse("1997-07-16T07:30:15+01:00")

        assert dt.resolution == DateTimeResolution.datetime
        assert dt.dt == datetime.datetime(
            1997,
            7,
            16,
            7,
            30,
            15,
            tzinfo=tzoffset(None, 3600),
        )

    def test_parse_datetime_with_tz_no_colon(self) -> None:
        dt = KmlDateTime.parse("1997-07-16T07:30:15+0100")

        assert dt.resolution == DateTimeResolution.datetime
        assert dt.dt == datetime.datetime(
            1997,
            7,
            16,
            7,
            30,
            15,
            tzinfo=tzoffset(None, 3600),
        )

    def test_parse_datetime_no_tz(self) -> None:
        dt = KmlDateTime.parse("1997-07-16T07:30:15")

        assert dt.resolution == DateTimeResolution.datetime
        assert dt.dt == datetime.datetime(1997, 7, 16, 7, 30, 15, tzinfo=tzutc())

    def test_parse_datetime_empty(self) -> None:
        assert KmlDateTime.parse("") is None

    def test_parse_year_month_5(self) -> None:
        """Test that a single digit month is invalid."""
        assert KmlDateTime.parse("19973") is None


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_timestamp(self) -> None:
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

    def test_timespan(self) -> None:
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

    def test_feature_timestamp(self) -> None:
        now = datetime.datetime.now()
        f = kml.Document()
        f._times = kml.TimeStamp(timestamp=KmlDateTime(now))
        assert f.time_stamp.dt == now
        assert now.isoformat() in str(f.to_string())
        assert "TimeStamp>" in str(f.to_string())
        assert "when>" in str(f.to_string())
        f._times = kml.TimeStamp(timestamp=KmlDateTime(now.date()))
        assert now.date().isoformat() in str(f.to_string())
        assert now.isoformat() not in str(f.to_string())
        f._times = None
        assert "TimeStamp>" not in str(f.to_string())

    @pytest.mark.skip(reason="not yet implemented")
    def test_feature_timespan(self) -> None:
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

    def test_read_timestamp_year(self) -> None:
        doc = """
        <TimeStamp>
          <when>1997</when>
        </TimeStamp>
        """

        ts = kml.TimeStamp.class_from_string(doc, ns="")

        assert ts.timestamp.resolution == DateTimeResolution.year
        assert ts.timestamp.dt == datetime.datetime(1997, 1, 1, 0, 0, tzinfo=tzutc())

    def test_read_timestamp_year_month(self) -> None:
        doc = """
        <TimeStamp>
          <when>1997-07</when>
        </TimeStamp>
        """

        ts = kml.TimeStamp.class_from_string(doc, ns="")

        assert ts.timestamp.resolution == DateTimeResolution.year_month
        assert ts.timestamp.dt == datetime.datetime(1997, 7, 1, 0, 0, tzinfo=tzutc())

    def test_read_timestamp_ym_no_hyphen(self) -> None:
        doc = """
        <TimeStamp>
          <when>199808</when>
        </TimeStamp>
        """

        ts = kml.TimeStamp.class_from_string(doc, ns="")

        assert ts.timestamp.resolution == DateTimeResolution.year_month
        assert ts.timestamp.dt == datetime.datetime(1998, 8, 1, 0, 0, tzinfo=tzutc())

    def test_read_timestamp_ymd(self) -> None:
        doc = """
        <TimeStamp>
          <when>1997-07-16</when>
        </TimeStamp>
        """

        ts = kml.TimeStamp.class_from_string(doc, ns="")

        assert ts.timestamp.resolution == DateTimeResolution.date
        assert ts.timestamp.dt == datetime.datetime(1997, 7, 16, 0, 0, tzinfo=tzutc())

    def test_read_timestamp_utc(self) -> None:
        # dateTime (YYYY-MM-DDThh:mm:ssZ)
        # Here, T is the separator between the calendar and the hourly notation
        # of time, and Z indicates UTC. (Seconds are required.)
        doc = """
        <TimeStamp>
          <when>1997-07-16T07:30:15Z</when>
        </TimeStamp>
        """

        ts = kml.TimeStamp.class_from_string(doc, ns="")

        assert ts.timestamp.resolution == DateTimeResolution.datetime
        assert ts.timestamp.dt == datetime.datetime(
            1997,
            7,
            16,
            7,
            30,
            15,
            tzinfo=tzutc(),
        )

    def test_read_timestamp_utc_offset(self) -> None:
        doc = """
        <TimeStamp>
          <when>1997-07-16T10:30:15+03:00</when>
        </TimeStamp>
        """

        ts = kml.TimeStamp.class_from_string(doc, ns="")

        assert ts.timestamp.resolution == DateTimeResolution.datetime
        assert ts.timestamp.dt == datetime.datetime(
            1997,
            7,
            16,
            10,
            30,
            15,
            tzinfo=tzoffset(None, 10800),
        )

    def test_read_timespan(self) -> None:
        doc = """
        <TimeSpan>
            <begin>1876-08-01</begin>
            <end>1997-07-16T07:30:15Z</end>
        </TimeSpan>
        """

        ts = kml.TimeSpan.class_from_string(doc, ns="")

        assert ts.begin.resolution == DateTimeResolution.date
        assert ts.begin.dt == datetime.datetime(1876, 8, 1, 0, 0, tzinfo=tzutc())
        assert ts.end.resolution == DateTimeResolution.datetime
        assert ts.end.dt == datetime.datetime(1997, 7, 16, 7, 30, 15, tzinfo=tzutc())

    def test_featurefromstring(self) -> None:
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

        d = kml.Document.class_from_string(doc, ns="")

        assert d.time_stamp.dt == datetime.datetime(
            1997,
            7,
            16,
            10,
            30,
            15,
            tzinfo=tzoffset(None, 10800),
        )


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""
