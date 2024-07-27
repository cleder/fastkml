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
from fastkml.enums import DateTimeResolution
from fastkml.enums import Verbosity
from fastkml.kml_base import _BaseObject
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
            dt = arrow.get(year, month, day).datetime
            resolution = DateTimeResolution.date
            if year_month_day_match.group("day") is None:
                resolution = DateTimeResolution.year_month
            if year_month_day_match.group("month") is None:
                resolution = DateTimeResolution.year
        elif len(datestr) > 10:  # noqa: PLR2004
            dt = arrow.get(datestr).datetime
            resolution = DateTimeResolution.datetime
        return cls(dt, resolution) if dt else None


class _TimePrimitive(_BaseObject):
    """
    Abstract element that cannot be used directly in a KML file.

    This element is extended by the <TimeSpan> and <TimeStamp> elements.
    https://developers.google.com/kml/documentation/kmlreference#timeprimitive
    """


class TimeStamp(_TimePrimitive):
    """Represents a single moment in time."""

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

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        """
        Create an ElementTree element representing the TimeStamp object.

        Args:
        ----
            precision (Optional[int]): The precision of the timestamp.
            verbosity (Verbosity): The verbosity level of the element.

        Returns:
        -------
            Element: The ElementTree element representing the TimeStamp object.

        """
        element = super().etree_element(precision=precision, verbosity=verbosity)
        when = config.etree.SubElement(
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

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        """
        Create an Element object representing the time interval.

        Args:
        ----
            precision (Optional[int]): The precision of the time values.
            verbosity (Verbosity): The verbosity level for the element.

        Returns:
        -------
            Element: The created Element object.

        """
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.begin is not None:  # noqa: SIM102
            if text := str(self.begin):
                begin = config.etree.SubElement(
                    element,
                    f"{self.ns}begin",
                )
                begin.text = text
        if self.end is not None:  # noqa: SIM102
            if text := str(self.end):
                end = config.etree.SubElement(
                    element,
                    f"{self.ns}end",
                )
                end.text = text
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
