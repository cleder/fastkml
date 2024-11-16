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
"""
Date and time handling in KML.

Any Feature in KML can have time data associated with it.
This time data has the effect of restricting the visibility of the data set to a given
time period or point in time.

https://developers.google.com/kml/documentation/time
"""

import re
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import arrow

from fastkml import config
from fastkml.enums import DateTimeResolution
from fastkml.helpers import datetime_subelement
from fastkml.helpers import datetime_subelement_kwarg
from fastkml.kml_base import _BaseObject
from fastkml.registry import RegistryItem
from fastkml.registry import registry

__all__ = ["KmlDateTime", "TimeSpan", "TimeStamp", "adjust_date_to_resolution"]

# regular expression to parse a gYearMonth string
# year and month may be separated by an optional dash
# year is always 4 digits, month, day is always 2 digits
year_month_day = re.compile(
    r"^(?P<year>\d{4})(?:-)?(?P<month>\d{2})?(?:-)?(?P<day>\d{2})?$",
)


def adjust_date_to_resolution(
    dt: Union[date, datetime],
    resolution: Optional[DateTimeResolution] = None,
) -> Union[date, datetime]:
    """
    Adjust the date or datetime to the specified resolution.

    This function adjusts the date or datetime to the specified resolution.
    If the resolution is not specified, the function will return the date or
    datetime as is.

    The function will return the date if the resolution is set to year,
    year_month, or date. If the resolution is set to datetime, the function
    will return the datetime as is.

    Args:
    ----
        dt : Union[date, datetime]
            The date or datetime to adjust.
        resolution : Optional[DateTimeResolution], optional
            The resolution to adjust the date or datetime to, by default None.

    Returns:
    -------
        Union[date, datetime]
            The adjusted date or datetime.

    """
    if resolution == DateTimeResolution.year:
        return date(dt.year, 1, 1)
    if resolution == DateTimeResolution.year_month:
        return date(dt.year, dt.month, 1)
    return (
        dt.date()
        if isinstance(dt, datetime) and resolution != DateTimeResolution.datetime
        else dt
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
        """
        Initialize a KmlDateTime object.

        Args:
        ----
            dt : Union[date, datetime]
                The date or datetime to adjust.
            resolution : Optional[DateTimeResolution], optional
                The resolution to adjust the date or datetime to, by default None.

        """
        if resolution is None:
            # sourcery skip: swap-if-expression
            resolution = (
                DateTimeResolution.date
                if not isinstance(dt, datetime)
                else DateTimeResolution.datetime
            )
        self.dt = adjust_date_to_resolution(dt, resolution)
        self.resolution = (
            DateTimeResolution.date
            if not isinstance(self.dt, datetime)
            and resolution == DateTimeResolution.datetime
            else resolution
        )

    def __repr__(self) -> str:
        """Create a string (c)representation for KmlDateTime."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"dt={self.dt!r}, "
            f"resolution={self.resolution}, "
            ")"
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
        return self.dt.isoformat()

    @classmethod
    def parse(cls, datestr: str) -> Optional["KmlDateTime"]:
        """Parse a KML DateTime string into a KmlDateTime object."""
        resolution = None
        dt = None
        if year_month_day_match := year_month_day.match(datestr):
            year = int(year_month_day_match.group("year"))
            month = int(year_month_day_match.group("month") or 1)
            day = int(year_month_day_match.group("day") or 1)
            dt = date(year, month, day)
            resolution = DateTimeResolution.date
            if year_month_day_match.group("day") is None:
                resolution = DateTimeResolution.year_month
            if year_month_day_match.group("month") is None:
                resolution = DateTimeResolution.year
            return cls(dt, resolution)
        return cls(arrow.get(datestr).datetime, DateTimeResolution.datetime)

    @classmethod
    def get_ns_id(cls) -> str:
        """Return the namespace ID."""
        return config.KML


class _TimePrimitive(_BaseObject):
    """
    Abstract element that cannot be used directly in a KML file.

    This element is extended by the <TimeSpan> and <TimeStamp> elements.
    https://developers.google.com/kml/documentation/kmlreference#timeprimitive
    """


class TimeStamp(_TimePrimitive):
    """
    Represents a single moment in time.

    https://developers.google.com/kml/documentation/kmlreference#timestamp
    """

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        timestamp: Optional[KmlDateTime] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the Times class.

        Args:
        ----
            ns : str, optional
                The namespace for the element, by default None.
            name_spaces : dict[str, str], optional
                The dictionary of namespace prefixes and URIs, by default None.
            id : str, optional
                The ID of the element, by default None.
            target_id : str, optional
                The target ID of the element, by default None.
            timestamp : KmlDateTime, optional
                The timestamp of the element, by default None.
            **kwargs : Any
                Additional keyword arguments.

        Returns:
        -------
            None

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.timestamp = timestamp

    def __repr__(self) -> str:
        """Create a string (c)representation for TimeStamp."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"timestamp={self.timestamp!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """Return True if the timestamp is valid."""
        return bool(self.timestamp)


registry.register(
    TimeStamp,
    item=RegistryItem(
        ns_ids=("kml", "gx", ""),
        classes=(KmlDateTime,),
        attr_name="timestamp",
        node_name="when",
        get_kwarg=datetime_subelement_kwarg,
        set_element=datetime_subelement,
    ),
)


class TimeSpan(_TimePrimitive):
    """
    Represents an extent in time bounded by begin and end dateTimes.

    https://developers.google.com/kml/documentation/kmlreference#timespan
    """

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        begin: Optional[KmlDateTime] = None,
        end: Optional[KmlDateTime] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the Times class.

        Args:
        ----
            ns (Optional[str]): The namespace for the element.
            name_spaces (Optional[Dict[str, str]]): The dictionary of namespace prefixes
                and URIs.
            id (Optional[str]): The ID of the element.
            target_id (Optional[str]): The target ID of the element.
            begin (Optional[KmlDateTime]): The begin time.
            end (Optional[KmlDateTime]): The end time.
            **kwargs (Any): Additional keyword arguments.

        Returns:
        -------
            None

        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            **kwargs,
        )
        self.begin = begin
        self.end = end

    def __repr__(self) -> str:
        """Create a string (c)representation for TimeSpan."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"begin={self.begin!r}, "
            f"end={self.end!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """Return True if the begin or end date is valid."""
        return bool(self.begin) or bool(self.end)


registry.register(
    TimeSpan,
    item=RegistryItem(
        ns_ids=("kml", "gx", ""),
        classes=(KmlDateTime,),
        attr_name="begin",
        node_name="begin",
        get_kwarg=datetime_subelement_kwarg,
        set_element=datetime_subelement,
    ),
)
registry.register(
    TimeSpan,
    item=RegistryItem(
        ns_ids=("kml", "gx", ""),
        classes=(KmlDateTime,),
        attr_name="end",
        node_name="end",
        get_kwarg=datetime_subelement_kwarg,
        set_element=datetime_subelement,
    ),
)
