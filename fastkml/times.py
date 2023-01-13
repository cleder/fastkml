"""Date and time handling in KML."""
import re
from datetime import date
from datetime import datetime
from typing import Optional
from typing import Tuple
from typing import Union

# note that there are some ISO 8601 timeparsers at pypi
# but in my tests all of them had some errors so we rely on the
# tried and tested dateutil here which is more stable. As a side effect
# we can also parse non ISO compliant dateTimes
import dateutil.parser

import fastkml.config as config
from fastkml.base import _BaseObject
from fastkml.types import Element

# regular expression to parse a gYearMonth string
# year and month may be separated by a dash or not
# year is always 4 digits, month is always 2 digits
# capture groups are named year and month, the dash is not captured
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
        resolution: Optional[str] = None,
    ):
        """Initialize a KmlDateTime object."""
        self.dt = dt
        self.resolution = resolution
        if resolution is None:
            # sourcery skip: swap-if-expression
            self.resolution = "date" if not isinstance(dt, datetime) else "dateTime"

    def __str__(self) -> str:
        """Return the KML DateTime string representation of the object."""
        if self.resolution == "gYear":
            return self.dt.strftime("%Y")
        if self.resolution == "gYearMonth":
            return self.dt.strftime("%Y-%m")
        if self.resolution == "date":
            return (
                self.dt.date().isoformat()
                if isinstance(self.dt, datetime)
                else self.dt.isoformat()
            )
        if self.resolution == "dateTime":
            return self.dt.isoformat()
        raise ValueError

    @classmethod
    def parse(cls, datestr: str) -> "KmlDateTime":
        """Parse a KML DateTime string into a KmlDateTime object."""
        resolution = None
        dt = None
        if len(datestr) == 4:
            year = int(datestr)
            dt = datetime(year, 1, 1)
            resolution = "gYear"
        elif len(datestr) in {6, 7}:
            ym = year_month.match(datestr)
            if ym:
                year = int(ym.group("year"))
                month = int(ym.group("month"))
                dt = datetime(year, month, 1)
                resolution = "gYearMonth"
        elif len(datestr) in {8, 10}:  # 8 is YYYYMMDDS
            dt = dateutil.parser.parse(datestr)
            resolution = "date"
        elif len(datestr) > 10:
            dt = dateutil.parser.parse(datestr)
            resolution = "dateTime"
        if dt is None:
            raise ValueError
        return cls(dt, resolution)


class _TimePrimitive(_BaseObject):
    """The dateTime is defined according to XML Schema time.
    The value can be expressed as yyyy-mm-ddThh:mm:sszzzzzz, where T is
    the separator between the date and the time, and the time zone is
    either Z (for UTC) or zzzzzz, which represents ±hh:mm in relation to
    UTC. Additionally, the value can be expressed as a date only.

    The precision of the dateTime is dictated by the dateTime value
    which can be one of the following:

    - dateTime gives second resolution
    - date gives day resolution
    - gYearMonth gives month resolution
    - gYear gives year resolution

    https://developers.google.com/kml/documentation/kmlreference#timeprimitive
    """

    RESOLUTIONS = ["gYear", "gYearMonth", "date", "dateTime"]

    def get_resolution(
        self,
        dt: Optional[Union[date, datetime]],
        resolution: Optional[str] = None,
    ) -> Optional[str]:
        if resolution:
            if resolution not in self.RESOLUTIONS:
                raise ValueError
            else:
                return resolution
        elif isinstance(dt, datetime):
            resolution = "dateTime"
        elif isinstance(dt, date):
            resolution = "date"
        else:
            resolution = None
        return resolution

    def parse_str(self, datestr: str) -> Tuple[datetime, str]:
        if len(datestr) == 4:
            year = int(datestr)
            return datetime(year, 1, 1), "gYear"
        if len(datestr) in {6, 7}:
            ym = year_month.match(datestr)
            if ym:
                year = int(ym.group("year"))
                month = int(ym.group("month"))
                return datetime(year, month, 1), "gYearMonth"
        if len(datestr) in {8, 10}:  # 8 is YYYYMMDDS
            return dateutil.parser.parse(datestr), "date"
        if len(datestr) > 10:
            return dateutil.parser.parse(datestr), "dateTime"
        raise ValueError

    def date_to_string(
        self,
        dt: Optional[Union[date, datetime]],
        resolution: Optional[str] = None,
    ) -> Optional[str]:
        if isinstance(dt, (date, datetime)):
            resolution = self.get_resolution(dt, resolution)
            if resolution == "gYear":
                return dt.strftime("%Y")
            elif resolution == "gYearMonth":
                return dt.strftime("%Y-%m")
            elif resolution == "date":
                return (
                    dt.date().isoformat()
                    if isinstance(dt, datetime)
                    else dt.isoformat()
                )
            elif resolution == "dateTime":
                return dt.isoformat()
        return None


class TimeStamp(_TimePrimitive):
    """Represents a single moment in time."""

    __name__ = "TimeStamp"
    timestamp: Optional[Tuple[datetime, str]] = None

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        timestamp: Optional[Union[date, datetime]] = None,
        resolution: Optional[str] = None,
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        resolution = self.get_resolution(timestamp, resolution)
        self.timestamp = (timestamp, resolution)

    def etree_element(self) -> Element:
        element = super().etree_element()
        when = config.etree.SubElement(  # type: ignore[attr-defined]
            element, f"{self.ns}when"
        )
        when.text = self.date_to_string(*self.timestamp)
        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        when = element.find(f"{self.ns}when")
        if when is not None:
            self.timestamp = self.parse_str(when.text)


class TimeSpan(_TimePrimitive):
    """Represents an extent in time bounded by begin and end dateTimes."""

    __name__ = "TimeSpan"
    begin = None
    end = None

    def __init__(
        self,
        ns: Optional[str] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        begin: Optional[Union[date, datetime]] = None,
        begin_res: None = None,
        end: Optional[Union[date, datetime]] = None,
        end_res: None = None,
    ) -> None:
        super().__init__(ns=ns, id=id, target_id=target_id)
        if begin:
            resolution = self.get_resolution(begin, begin_res)
            self.begin = [begin, resolution]
        if end:
            resolution = self.get_resolution(end, end_res)
            self.end = [end, resolution]

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        begin = element.find(f"{self.ns}begin")
        if begin is not None:
            self.begin = self.parse_str(begin.text)
        end = element.find(f"{self.ns}end")
        if end is not None:
            self.end = self.parse_str(end.text)

    def etree_element(self) -> Element:
        element = super().etree_element()
        if self.begin is not None:
            text = self.date_to_string(*self.begin)
            if text:
                begin = config.etree.SubElement(element, f"{self.ns}begin")
                begin.text = text
        if self.end is not None:
            text = self.date_to_string(*self.end)
            if text:
                end = config.etree.SubElement(element, f"{self.ns}end")
                end.text = text
        if self.begin == self.end is None:
            raise ValueError("Either begin, end or both must be set")
        # TODO test if end > begin
        return element
