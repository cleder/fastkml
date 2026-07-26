# Copyright (C) 2012 - 2025  Christian Ledermann
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
Configure the tests.

Register the hypothesis 'exhaustive' profile to run 10 thousand examples.
Run this profile with ``pytest --hypothesis-profile=exhaustive``
"""

from hypothesis import HealthCheck
from hypothesis import settings

settings.register_profile(
    "exhaustive",
    max_examples=10_000,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile(
    "coverage",
    max_examples=10,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile("ci", suppress_health_check=[HealthCheck.too_slow])
