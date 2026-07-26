# Copyright (C) 2025  Christian Ledermann
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
"""Shared helpers for the OGC KML 2.2 Conformance Test Suite fixture tests."""

import pathlib
from typing import Any

from xmldiff import main

BASEDIR = pathlib.Path(__file__).parent
KMLFILEDIR = BASEDIR / "data" / "kml"


def xmldiff(actual: str | bytes, expected: str | bytes) -> list[Any]:
    """
    Diff two XML documents.

    Returns the list of xmldiff.actions items needed to turn `actual` into
    `expected` -- an empty list means the two documents are identical.

    Deliberately doesn't use an xmldiff formatter: xmldiff's formatters raise
    a TypeError on any action touching the default (unprefixed) namespace
    (`InsertNamespace`/`DeleteNamespace` with `prefix=None`), which most of
    these fixtures trigger.
    """
    return main.diff_texts(actual, expected)
