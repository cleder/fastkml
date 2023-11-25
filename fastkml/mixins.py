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
    _times: Optional[Union[TimeSpan, TimeStamp]] = None

    @property
    def time_stamp(self) -> Optional[KmlDateTime]:
        """This just returns the datetime portion of the timestamp."""
        return self._times.timestamp if isinstance(self._times, TimeStamp) else None

    @property
    def begin(self) -> Optional[KmlDateTime]:
        return self._times.begin if isinstance(self._times, TimeSpan) else None

    @property
    def end(self) -> Optional[KmlDateTime]:
        return self._times.end if isinstance(self._times, TimeSpan) else None
