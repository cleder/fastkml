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
import string
import typing

from hypothesis import given
from hypothesis import strategies as st
from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import line_coords
from pygeoif.hypothesis.strategies import points

import fastkml.geometry
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity

eval_locals = {
    "Point": Point,
    "Polygon": Polygon,
    "LineString": LineString,
    "LinearRing": LinearRing,
    "AltitudeMode": AltitudeMode,
    "fastkml": fastkml,
}

ID_TEXT = string.ascii_letters + string.digits + string.punctuation


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


@given(
    id=st.one_of(st.none(), st.text(alphabet=string.printable)),
    target_id=st.one_of(st.none(), st.text(alphabet=string.printable)),
    extrude=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        points(srs=epsg4326),
    ),
)
def test_point_repr_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[Point],
) -> None:
    point = fastkml.geometry.Point(
        id=id,
        target_id=target_id,
        extrude=extrude,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_p = eval(repr(point), {}, eval_locals)  # noqa: S307

    assert point == new_p


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        points(srs=epsg4326),
    ),
)
def test_point_str_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[Point],
) -> None:
    point = fastkml.geometry.Point(
        id=id,
        target_id=target_id,
        extrude=extrude,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_p = fastkml.geometry.Point.class_from_string(point.to_string())

    assert point.to_string() == new_p.to_string()
    assert point.geometry == new_p.geometry


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        points(srs=epsg4326),
    ),
)
def test_point_str_roundtrip_terse(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[Point],
) -> None:
    point = fastkml.geometry.Point(
        id=id,
        target_id=target_id,
        extrude=extrude,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_p = fastkml.geometry.Point.class_from_string(
        point.to_string(precision=15, verbosity=Verbosity.terse),
    )

    assert (new_p.altitude_mode is None) or (
        new_p.altitude_mode != AltitudeMode.clamp_to_ground
    )
    assert (new_p.extrude is None) or (new_p.extrude is True)
    assert point.to_string(verbosity=Verbosity.verbose, precision=6) == new_p.to_string(
        verbosity=Verbosity.verbose,
        precision=6,
    )


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        points(srs=epsg4326),
    ),
)
def test_point_str_roundtrip_verbose(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[Point],
) -> None:
    point = fastkml.geometry.Point(
        id=id,
        target_id=target_id,
        extrude=extrude,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_p = fastkml.geometry.Point.class_from_string(
        point.to_string(verbosity=Verbosity.verbose),
    )

    assert isinstance(new_p.altitude_mode, AltitudeMode)
    assert isinstance(new_p.extrude, bool)
    assert point.to_string(verbosity=Verbosity.terse, precision=16) == new_p.to_string(
        verbosity=Verbosity.terse,
        precision=16,
    )
