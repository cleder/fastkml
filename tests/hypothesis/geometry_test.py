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
from functools import partial

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import line_coords
from pygeoif.hypothesis.strategies import line_strings
from pygeoif.hypothesis.strategies import points
from pygeoif.hypothesis.strategies import polygons

import fastkml.geometry
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity
from fastkml.validator import validate
from tests.base import Lxml
from tests.hypothesis.common import assert_repr_roundtrip
from tests.hypothesis.common import assert_str_roundtrip
from tests.hypothesis.strategies import nc_name

eval_locals = {
    "Point": Point,
    "Polygon": Polygon,
    "LineString": LineString,
    "LinearRing": LinearRing,
    "AltitudeMode": AltitudeMode,
    "fastkml": fastkml,
}

kml_geometry = typing.Union[
    fastkml.geometry.Point,
    fastkml.geometry.LineString,
    fastkml.geometry.Polygon,
]

coordinates = partial(
    given,
    coords=st.one_of(st.none(), line_coords(srs=epsg4326, min_points=1)),
)

common_geometry = partial(
    given,
    id=st.one_of(st.none(), nc_name()),
    target_id=st.one_of(st.none(), nc_name()),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(
        st.none(),
        st.sampled_from(
            (
                AltitudeMode.absolute,
                AltitudeMode.clamp_to_ground,
                AltitudeMode.relative_to_ground,
            ),
        ),
    ),
)


def _test_repr_roundtrip(geometry: kml_geometry) -> None:
    assert_repr_roundtrip(geometry)


def _test_geometry_str_roundtrip(geometry: kml_geometry) -> None:
    assert_str_roundtrip(geometry)


def _test_geometry_str_roundtrip_terse(geometry: kml_geometry) -> None:
    new_g = type(geometry).from_string(
        geometry.to_string(verbosity=Verbosity.terse),
    )

    assert validate(element=new_g.etree_element())
    assert geometry.to_string(verbosity=Verbosity.verbose) == new_g.to_string(
        verbosity=Verbosity.verbose,
    )
    assert geometry.geometry == new_g.geometry
    if geometry.altitude_mode == AltitudeMode.clamp_to_ground:
        assert new_g.altitude_mode is None
    else:
        assert new_g.altitude_mode == geometry.altitude_mode
    if geometry.extrude:
        assert new_g.extrude is True
    else:
        assert new_g.extrude is None
    if hasattr(geometry, "tessellate"):
        assert not isinstance(geometry, fastkml.geometry.Point)
        if geometry.tessellate:
            assert new_g.tessellate is True
        else:
            assert new_g.tessellate is None


def _test_geometry_str_roundtrip_verbose(geometry: kml_geometry) -> None:
    new_g = type(geometry).from_string(
        geometry.to_string(verbosity=Verbosity.verbose),
    )

    assert validate(element=new_g.etree_element())
    assert geometry.to_string(verbosity=Verbosity.terse) == new_g.to_string(
        verbosity=Verbosity.terse,
    )
    assert geometry.geometry == new_g.geometry
    assert new_g.altitude_mode is not None
    if geometry.altitude_mode is None:
        assert new_g.altitude_mode == AltitudeMode.clamp_to_ground
    if geometry.extrude is None:
        assert new_g.extrude is False
    else:
        assert new_g.extrude == geometry.extrude
    if hasattr(geometry, "tessellate"):
        assert not isinstance(geometry, fastkml.geometry.Point)
        if geometry.tessellate is None:
            assert new_g.tessellate is False
        else:
            assert new_g.tessellate == geometry.tessellate


class TestLxml(Lxml):

    @coordinates()
    @settings(deadline=None)
    def test_coordinates_str_roundtrip(
        self,
        coords: typing.Union[
            typing.Sequence[typing.Tuple[float, float]],
            typing.Sequence[typing.Tuple[float, float, float]],
            None,
        ],
    ) -> None:
        coordinate = fastkml.geometry.Coordinates(coords=coords)

        new_c = fastkml.geometry.Coordinates.from_string(
            coordinate.to_string(precision=20),
        )

        assert coordinate.to_string(precision=10) == new_c.to_string(precision=10)
        assert validate(element=new_c.etree_element())

    @coordinates()
    def test_coordinates_repr_roundtrip(
        self,
        coords: typing.Union[
            typing.Sequence[typing.Tuple[float, float]],
            typing.Sequence[typing.Tuple[float, float, float]],
            None,
        ],
    ) -> None:
        coordinate = fastkml.geometry.Coordinates(coords=coords)

        new_c = eval(repr(coordinate), {}, eval_locals)  # noqa: S307

        assert coordinate == new_c
        assert validate(element=new_c.etree_element())

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            points(srs=epsg4326),
        ),
    )
    def test_point_repr_roundtrip(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        tessellate: typing.Optional[bool],  # noqa: ARG002
        geometry: typing.Optional[Point],
    ) -> None:
        point = fastkml.geometry.Point(
            id=id,
            target_id=target_id,
            extrude=extrude,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_repr_roundtrip(point)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            points(srs=epsg4326),
        ),
    )
    def test_point_str_roundtrip(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],  # noqa: ARG002
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

        _test_geometry_str_roundtrip(point)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            points(srs=epsg4326),
        ),
    )
    def test_point_str_roundtrip_terse(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],  # noqa: ARG002
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

        _test_geometry_str_roundtrip_terse(point)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            points(srs=epsg4326),
        ),
    )
    def test_point_str_roundtrip_verbose(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],  # noqa: ARG002
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

        _test_geometry_str_roundtrip_verbose(point)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            line_strings(srs=epsg4326),
        ),
    )
    def test_linestring_repr_roundtrip(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        geometry: typing.Optional[LineString],
    ) -> None:
        line = fastkml.geometry.LineString(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_repr_roundtrip(line)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            line_strings(srs=epsg4326),
        ),
    )
    def test_linestring_str_roundtrip(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        geometry: typing.Optional[LineString],
    ) -> None:
        line = fastkml.geometry.LineString(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip(line)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            line_strings(srs=epsg4326),
        ),
    )
    def test_linestring_str_roundtrip_terse(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        geometry: typing.Optional[LineString],
    ) -> None:
        line = fastkml.geometry.LineString(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_terse(line)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            line_strings(srs=epsg4326),
        ),
    )
    def test_linestring_str_roundtrip_verbose(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        geometry: typing.Optional[LineString],
    ) -> None:
        line = fastkml.geometry.LineString(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_verbose(line)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            polygons(srs=epsg4326),
        ),
    )
    def test_polygon_repr_roundtrip(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        geometry: typing.Optional[Polygon],
    ) -> None:
        polygon = fastkml.geometry.Polygon(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_repr_roundtrip(polygon)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            polygons(srs=epsg4326),
        ),
    )
    def test_polygon_str_roundtrip(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        geometry: typing.Optional[Polygon],
    ) -> None:
        polygon = fastkml.geometry.Polygon(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip(polygon)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            polygons(srs=epsg4326),
        ),
    )
    def test_polygon_str_roundtrip_terse(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        geometry: typing.Optional[Polygon],
    ) -> None:
        polygon = fastkml.geometry.Polygon(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_terse(polygon)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            polygons(srs=epsg4326),
        ),
    )
    def test_polygon_str_roundtrip_verbose(
        self,
        id: typing.Optional[str],
        target_id: typing.Optional[str],
        extrude: typing.Optional[bool],
        tessellate: typing.Optional[bool],
        altitude_mode: typing.Optional[AltitudeMode],
        geometry: typing.Optional[Polygon],
    ) -> None:
        polygon = fastkml.geometry.Polygon(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_verbose(polygon)
