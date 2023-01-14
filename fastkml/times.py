# Copyright (C) 2012 - 2023  Christian Ledermann
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
"""Date and time handling in KML."""
import re
from datetime import date
from datetime import datetime
from typing import Optional
from typing import Union

# note that there are some ISO 8601 timeparsers at pypi
# but in my tests all of them had some errors so we rely on the
# tried and tested dateutil here which is more stable. As a side effect
# we can also parse non ISO compliant dateTimes
import dateutil.parser

import fastkml.config as config
from fastkml.base import _BaseObject
from fastkml.enums import DateTimeResolution
from fastkml.types import Element

# regular expression to parse a gYearMonth string
# year and month may be separated by a dash or not
# year is always 4 digits, month is always 2 digits
year_month = re.compile(r"^(?P<year>\d{4})(?:-?)(?P<month>\d{2})$")


class KmlDateTime:
    """A KML DateTime object.

    This class is used to parse and format KML DateTime objects.

    A KML DateTime object is a string that conforms to the ISO 8601 standard
    for date and time representation. The following formats are supported:

    - yyyy-mm-ddThh:mm:sszzzzzz
    - yyyy-mm-ddThh:mm:ss
    - yyyy-mm-dd
    - yyyy-mm
    - yyyy

    The T is the separator between the date and the time, and the time zone
    is either Z (for UTC) or zzzzzz, which represents ±hh:mm in relation to
    UTC. Additionally, the value can be expressed as a date only.

    The precision of the DateTime is dictated by the DateTime value
    which can be one of the following:

    - dateTime gives second resolution
    - date gives day resolution
    - gYearMonth gives month resolution
    - gYear gives year resolution

    The KmlDateTime class can be used to parse a KML DateTime string into a
    Python datetime object, or to format a Python datetime object into a
    KML DateTime string.

    The KmlDateTime class is used by the TimeStamp and TimeSpan classes.
    """

    def __init__(
        self,
        dt: Union[date, datetime],
        resolution: Optional[DateTimeResolution] = None,
    ):
        """Initialize a KmlDateTime object."""
        self.dt = dt
        self.resolution = resolution
        if resolution is None:
            # sourcery skip: swap-if-expression
            self.resolution = (
                DateTimeResolution.date
                if not isinstance(dt, datetime)
                else DateTimeResolution.datetime
            )

    def __bool__(self) -> bool:
        """Return True if the date or datetime is valid."""
        return isinstance(self.dt, date)

    def __eq__(self, other: object) -> bool:
        """Return True if the two objects are equal."""
        return (
            self.dt == other.dt and self.resolution == other.resolution
            if isinstance(other, KmlDateTime)
            else False
        )

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"{self.__class__.__name__}({self.dt!r}, {self.resolution})"

    def __str__(self) -> str:
        """Return the KML DateTime string representation of the object."""
        if self.resolution == DateTimeResolution.year:
            return self.dt.strftime("%Y")
        if self.resolution == DateTimeResolution.year_month:
            return self.dt.strftime("%Y-%m")
        if self.resolution == DateTimeResolution.date:
            return (
                self.dt.date().isoformat()
                if isinstance(self.dt, datetime)
                else self.dt.isoformat()
            )
        if self.resolution == DateTimeResolution.datetime:
            return self.dt.isoformat()
        raise ValueError

    @classmethod
    def parse(cls, datestr: str) -> Optional["KmlDateTime"]:
        """Parse a KML DateTime string into a KmlDateTime object."""
        resolution = None
        dt = None
        if len(datestr) == 4:
            year = int(datestr)
            dt = datetime(year, 1, 1)
            resolution = DateTimeResolution.year
        elif len(datestr) in {6, 7}:
            ym = year_month.match(datestr)
            if ym:
                year = int(ym.group("year"))
                month = int(ym.group("month"))
                dt = datetime(year, month, 1)
                resolution = DateTimeResolution.year_month
        elif len(datestr) in {8, 10}:  # 8 is YYYYMMDD, 10 is YYYY-MM-DD
            dt = dateutil.parser.parse(datestr)
            resolution = DateTimeResolution.date
        elif len(datestr) > 10:
            dt = dateutil.parser.parse(datestr)
            resolution = DateTimeResolution.datetime
        return cls(dt, resolution) if dt else None


class _TimePrimitive(_BaseObject):
    """
    This is an abstract element and cannot be used directly in a KML file.

    This element is extended by the <TimeSpan> and <TimeStamp> elements.
    https://developers.google.com/kml/documentation/kmlreference#timeprimitive
    """


class TimeStamp(_TimePrimitive):
    """Represents a single moment in time."""

    __name__ = "TimeStamp"

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        timestamp: Optional[KmlDateTime] = None,
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        self.timestamp = timestamp

    def etree_element(self) -> Element:
        element = super().etree_element()
        when = config.etree.SubElement(  # type: ignore[attr-defined]
            element, f"{self.ns}when"
        )
        when.text = str(self.timestamp)
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        when = element.find(f"{self.ns}when")
        if when is not None:
            self.timestamp = KmlDateTime.parse(when.text)


class TimeSpan(_TimePrimitive):
    """Represents an extent in time bounded by begin and end dateTimes."""

    __name__ = "TimeSpan"

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        begin: Optional[KmlDateTime] = None,
        end: Optional[KmlDateTime] = None,
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        self.begin = begin
        self.end = end

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        begin = element.find(f"{self.ns}begin")
        if begin is not None:
            self.begin = KmlDateTime.parse(begin.text)
        end = element.find(f"{self.ns}end")
        if end is not None:
            self.end = KmlDateTime.parse(end.text)

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.begin is not None:
            text = str(self.begin)
            if text:
                begin = config.etree.SubElement(  # type: ignore[attr-defined]
                    element,
                    f"{self.ns}begin",
                )
                begin.text = text
        if self.end is not None:
            text = str(self.end)
            if text:
                end = config.etree.SubElement(  # type: ignore[attr-defined]
                    element,
                    f"{self.ns}end",
                )
                end.text = text
        if self.begin == self.end is None:
            raise ValueError("Either begin, end or both must be set")
        # TODO test if end > begin
        return element
