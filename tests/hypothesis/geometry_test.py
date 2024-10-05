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

"""Property based tests of the Geometry classes."""

import typing

from hypothesis import given
from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import line_coords

import fastkml.geometry
from fastkml.enums import AltitudeMode

eval_locals = {
    "Point": Point,
    "Polygon": Polygon,
    "LineString": LineString,
    "LinearRing": LinearRing,
    "AltitudeMode": AltitudeMode,
    "fastkml": fastkml,
}


@given(
    coords=line_coords(srs=epsg4326, min_points=1),
)
def test_coordinates_str_roundtrip(
    coords: typing.Union[
        typing.Sequence[typing.Tuple[float, float]],
        typing.Sequence[typing.Tuple[float, float, float]],
        None,
    ],
) -> None:
    coordinate = fastkml.geometry.Coordinates(coords=coords)

    new_c = fastkml.geometry.Coordinates.class_from_string(
        coordinate.to_string(precision=20),
    )

    assert coordinate.to_string(precision=10) == new_c.to_string(precision=10)


@given(
    coords=line_coords(srs=epsg4326, min_points=1),
)
def test_coordinates_repr_roundtrip(
    coords: typing.Union[
        typing.Sequence[typing.Tuple[float, float]],
        typing.Sequence[typing.Tuple[float, float, float]],
        None,
    ],
) -> None:
    coordinate = fastkml.geometry.Coordinates(coords=coords)

    new_c = eval(repr(coordinate), {}, eval_locals)  # noqa: S307

    assert coordinate == new_c
