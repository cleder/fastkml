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

from collections.abc import Sequence

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
from tests.base import Lxml
from tests.base import PyUppsala
from tests.hypothesis.common import _validate_if_supported
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

kml_geometry = (
    fastkml.geometry.Point | fastkml.geometry.LineString | fastkml.geometry.Polygon
)

coordinates = {
    "coords": st.one_of(st.none(), line_coords(srs=epsg4326, min_points=1)),
}

common_geometry = {
    "id": st.one_of(st.none(), nc_name()),
    "target_id": st.one_of(st.none(), nc_name()),
    "extrude": st.one_of(st.none(), st.booleans()),
    "tessellate": st.one_of(st.none(), st.booleans()),
    "altitude_mode": st.one_of(
        st.none(),
        st.sampled_from(
            AltitudeMode,
        ),
    ),
}


def _test_repr_roundtrip(geometry: kml_geometry) -> None:
    assert_repr_roundtrip(geometry)


def _test_geometry_str_roundtrip(geometry: kml_geometry) -> None:
    assert_str_roundtrip(geometry)


def _test_geometry_str_roundtrip_terse(geometry: kml_geometry) -> None:
    new_g = type(geometry).from_string(
        geometry.to_string(verbosity=Verbosity.terse),
    )

    _validate_if_supported(new_g)
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

    _validate_if_supported(new_g)
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


class _Tests:
    @given(**coordinates)
    @settings(deadline=None)
    def test_coordinates_str_roundtrip(
        self,
        coords: Sequence[tuple[float, float]]
        | Sequence[tuple[float, float, float]]
        | None,
    ) -> None:
        coordinate = fastkml.geometry.Coordinates(coords=coords)

        new_c = fastkml.geometry.Coordinates.from_string(
            coordinate.to_string(precision=20),
        )

        assert coordinate.to_string(precision=10) == new_c.to_string(precision=10)
        _validate_if_supported(new_c)

    @given(**coordinates)
    def test_coordinates_repr_roundtrip(
        self,
        coords: Sequence[tuple[float, float]]
        | Sequence[tuple[float, float, float]]
        | None,
    ) -> None:
        coordinate = fastkml.geometry.Coordinates(coords=coords)

        new_c = eval(repr(coordinate), {}, eval_locals)  # noqa: S307

        assert coordinate == new_c
        _validate_if_supported(new_c)

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            points(srs=epsg4326),
        ),
    )
    def test_point_repr_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        altitude_mode: AltitudeMode | None,
        tessellate: bool | None,  # noqa: ARG002
        geometry: Point | None,
    ) -> None:
        point = fastkml.geometry.Point(
            id=id,
            target_id=target_id,
            extrude=extrude,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_repr_roundtrip(point)

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            points(srs=epsg4326),
        ),
    )
    def test_point_str_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,  # noqa: ARG002
        altitude_mode: AltitudeMode | None,
        geometry: Point | None,
    ) -> None:
        point = fastkml.geometry.Point(
            id=id,
            target_id=target_id,
            extrude=extrude,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip(point)

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            points(srs=epsg4326),
        ),
    )
    def test_point_str_roundtrip_terse(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,  # noqa: ARG002
        altitude_mode: AltitudeMode | None,
        geometry: Point | None,
    ) -> None:
        point = fastkml.geometry.Point(
            id=id,
            target_id=target_id,
            extrude=extrude,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_terse(point)

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            points(srs=epsg4326),
        ),
    )
    def test_point_str_roundtrip_verbose(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,  # noqa: ARG002
        altitude_mode: AltitudeMode | None,
        geometry: Point | None,
    ) -> None:
        point = fastkml.geometry.Point(
            id=id,
            target_id=target_id,
            extrude=extrude,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_verbose(point)

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            line_strings(srs=epsg4326),
        ),
    )
    def test_linestring_repr_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: LineString | None,
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

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            line_strings(srs=epsg4326),
        ),
    )
    def test_linestring_str_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: LineString | None,
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

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            line_strings(srs=epsg4326),
        ),
    )
    def test_linestring_str_roundtrip_terse(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: LineString | None,
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

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            line_strings(srs=epsg4326),
        ),
    )
    def test_linestring_str_roundtrip_verbose(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: LineString | None,
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

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            polygons(srs=epsg4326),
        ),
    )
    def test_polygon_repr_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: Polygon | None,
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

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            polygons(srs=epsg4326),
        ),
    )
    def test_polygon_str_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: Polygon | None,
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

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            polygons(srs=epsg4326),
        ),
    )
    def test_polygon_str_roundtrip_terse(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: Polygon | None,
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

    @given(
        **common_geometry,
        geometry=st.one_of(
            st.none(),
            polygons(srs=epsg4326),
        ),
    )
    def test_polygon_str_roundtrip_verbose(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: Polygon | None,
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


class TestLxml(Lxml, _Tests):
    """Test with lxml."""


class TestPyUppsala(PyUppsala, _Tests):
    """Test with pyuppsala."""
