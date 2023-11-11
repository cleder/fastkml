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
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import arrow

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.enums import DateTimeResolution
from fastkml.enums import Verbosity
from fastkml.types import Element

# regular expression to parse a gYearMonth string
# year and month may be separated by a dash or not
# year is always 4 digits, month is always 2 digits
year_month_day = re.compile(
    r"^(?P<year>\d{4})(?:-)?(?P<month>\d{2})?(?:-)?(?P<day>\d{2})?$",
)


class KmlDateTime:
    """
    A KML DateTime object.

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
    ) -> None:
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
        year_month_day_match = year_month_day.match(datestr)
        if year_month_day_match:
            year = int(year_month_day_match.group("year"))
            month = int(year_month_day_match.group("month") or 1)
            day = int(year_month_day_match.group("day") or 1)
            dt = arrow.get(year, month, day).datetime
            resolution = DateTimeResolution.date
            if year_month_day_match.group("day") is None:
                resolution = DateTimeResolution.year_month
            if year_month_day_match.group("month") is None:
                resolution = DateTimeResolution.year
        elif len(datestr) > 10:
            dt = arrow.get(datestr).datetime
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
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        timestamp: Optional[KmlDateTime] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.timestamp = timestamp

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        when = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}when",
        )
        when.text = str(self.timestamp)
        return element

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
        when = element.find(f"{ns}when")
        if when is not None:
            kwargs["timestamp"] = KmlDateTime.parse(when.text)
        return kwargs


class TimeSpan(_TimePrimitive):
    """Represents an extent in time bounded by begin and end dateTimes."""

    __name__ = "TimeSpan"

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        begin: Optional[KmlDateTime] = None,
        end: Optional[KmlDateTime] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.begin = begin
        self.end = end

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
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
            msg = "Either begin, end or both must be set"
            raise ValueError(msg)
        # TODO test if end > begin
        return element

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
        begin = element.find(f"{ns}begin")
        if begin is not None:
            kwargs["begin"] = KmlDateTime.parse(begin.text)
        end = element.find(f"{ns}end")
        if end is not None:
            kwargs["end"] = KmlDateTime.parse(end.text)
        return kwargs
