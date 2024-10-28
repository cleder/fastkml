# Copyright (C) 2024  Christian Ledermann
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

"""Common functionality for property based tests."""

import re
import string
from functools import partial

from hypothesis import strategies as st

from fastkml.validate import get_schema_parser

get_schema_parser()
ID_TEXT = string.ascii_letters + string.digits + string.punctuation
nc_name = partial(
    st.from_regex,
    regex=re.compile(r"^[A-Za-z_][\w.-]*$"),
    alphabet=ID_TEXT,
)
