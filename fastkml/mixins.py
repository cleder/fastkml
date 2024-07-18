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
from typing import Union

from fastkml.times import KmlDateTime
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp

logger = logging.getLogger(__name__)


class TimeMixin:
    """Mixin for classes that have a time element."""

    times: Optional[Union[TimeSpan, TimeStamp]] = None

    @property
    def time_stamp(self) -> Optional[KmlDateTime]:
        """Return the timestamp."""
        return self.times.timestamp if isinstance(self.times, TimeStamp) else None

    @property
    def begin(self) -> Optional[KmlDateTime]:
        """Return the start time of a time span."""
        return self.times.begin if isinstance(self.times, TimeSpan) else None

    @property
    def end(self) -> Optional[KmlDateTime]:
        """Return the end time of a time span."""
        return self.times.end if isinstance(self.times, TimeSpan) else None
