# Copyright (C) 2023  Christian Ledermann
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
"""Mixins for the KML classes."""
import logging
from typing import Optional

from fastkml.times import KmlDateTime
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp

logger = logging.getLogger(__name__)


class TimeMixin:

    _timespan: Optional[TimeSpan] = None
    _timestamp: Optional[TimeStamp] = None

    @property
    def time_stamp(self) -> Optional[KmlDateTime]:
        """This just returns the datetime portion of the timestamp"""
        return self._timestamp.timestamp if self._timestamp is not None else None

    @time_stamp.setter
    def time_stamp(self, timestamp: Optional[KmlDateTime]) -> None:
        if self._timestamp is None:
            self._timestamp = TimeStamp(timestamp=timestamp)
        elif timestamp is None:
            self._timestamp = None
        else:
            self._timestamp.timestamp = timestamp
        if self._timespan and self._timestamp:
            logger.warning("Setting a TimeStamp, TimeSpan deleted")
            self._timespan = None

    @property
    def begin(self) -> Optional[KmlDateTime]:
        return self._timespan.begin if self._timespan is not None else None

    @begin.setter
    def begin(self, dt: Optional[KmlDateTime]) -> None:
        if self._timespan is None:
            self._timespan = TimeSpan(begin=dt)
        elif dt is None and self._timespan.end is None:
            self._timespan = None
        else:
            self._timespan.begin = dt
        if self._timespan and self._timestamp:
            logger.warning("Setting a TimeSpan, TimeStamp deleted")
            self._timestamp = None

    @property
    def end(self) -> Optional[KmlDateTime]:
        return self._timespan.end if self._timespan is not None else None

    @end.setter
    def end(self, dt: Optional[KmlDateTime]) -> None:
        if self._timespan is None:
            self._timespan = TimeSpan(end=dt)
        elif dt is None and self._timespan.begin is None:
            self._timespan = None
        else:
            self._timespan.end = dt
        if self._timespan and self._timestamp:
            logger.warning("Setting a TimeSpan, TimeStamp deleted")
            self._timestamp = None
