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
from __future__ import annotations

from functools import partial

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from pygeoif.geometry import GeometryCollection
from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import MultiLineString
from pygeoif.geometry import MultiPoint
from pygeoif.geometry import MultiPolygon
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import geometry_collections
from pygeoif.hypothesis.strategies import multi_line_strings
from pygeoif.hypothesis.strategies import multi_points
from pygeoif.hypothesis.strategies import multi_polygons

import fastkml.geometry
from fastkml.enums import AltitudeMode
from fastkml.enums import Verbosity
from fastkml.validate import validate
from tests.base import Lxml
from tests.hypothesis.common import nc_name

eval_locals = {
    "Point": Point,
    "Polygon": Polygon,
    "LineString": LineString,
    "LinearRing": LinearRing,
    "AltitudeMode": AltitudeMode,
    "MultiPoint": MultiPoint,
    "MultiLineString": MultiLineString,
    "MultiPolygon": MultiPolygon,
    "GeometryCollection": GeometryCollection,
    "fastkml": fastkml,
}


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


def _test_repr_roundtrip(
    geometry: fastkml.geometry.MultiGeometry,
    cls: type[MultiPoint | MultiLineString | MultiPolygon | GeometryCollection],
) -> None:
    new_g = eval(repr(geometry), {}, eval_locals)  # noqa: S307

    assert geometry == new_g
    if geometry:
        assert type(new_g.geometry) is cls
    assert validate(element=new_g.etree_element())


def _test_geometry_str_roundtrip(
    geometry: fastkml.geometry.MultiGeometry,
    *,
    cls: type[MultiPoint | MultiLineString | MultiPolygon],
    extrude: bool | None,
    tessellate: bool | None,
    altitude_mode: AltitudeMode | None,
) -> None:
    new_g = fastkml.geometry.MultiGeometry.from_string(geometry.to_string())

    assert geometry.to_string() == new_g.to_string()
    assert geometry == new_g
    if not geometry:
        return
    assert new_g.geometry
    assert geometry.geometry
    assert type(new_g.geometry) is cls
    for g1, g2 in zip(new_g.kml_geometries, geometry.kml_geometries):
        assert g1.extrude == g2.extrude == extrude
        assert g1.altitude_mode == g2.altitude_mode == altitude_mode
        if not isinstance(g1, fastkml.geometry.Point):
            assert g1.tessellate == g2.tessellate == tessellate
    assert validate(element=new_g.etree_element())


def _test_geometry_str_roundtrip_terse(
    geometry: fastkml.geometry.MultiGeometry,
    *,
    cls: type[MultiPoint | MultiLineString | MultiPolygon],
    extrude: bool | None,
    tessellate: bool | None,
    altitude_mode: AltitudeMode | None,
) -> None:
    new_g = fastkml.geometry.MultiGeometry.from_string(
        geometry.to_string(verbosity=Verbosity.terse),
    )

    assert geometry.to_string(verbosity=Verbosity.verbose) == new_g.to_string(
        verbosity=Verbosity.verbose,
    )
    if not geometry:
        return
    assert new_g.geometry
    assert geometry.geometry
    assert type(new_g.geometry) is cls
    for new, orig in zip(new_g.kml_geometries, geometry.kml_geometries):
        if extrude:
            assert new.extrude == orig.extrude == extrude
        else:
            assert new.extrude is None
        if altitude_mode == AltitudeMode.clamp_to_ground:
            assert new.altitude_mode is None
        else:
            assert new.altitude_mode == orig.altitude_mode == altitude_mode
        if not isinstance(new, fastkml.geometry.Point):
            if tessellate:
                assert new.tessellate == orig.tessellate == tessellate
            else:
                assert new.tessellate is None
    validate(element=new_g.etree_element())


def _test_geometry_str_roundtrip_verbose(
    geometry: fastkml.geometry.MultiGeometry,
    *,
    cls: type[MultiPoint | MultiLineString | MultiPolygon],
    extrude: bool | None,
    tessellate: bool | None,
    altitude_mode: AltitudeMode | None,
) -> None:
    new_g = fastkml.geometry.MultiGeometry.from_string(
        geometry.to_string(verbosity=Verbosity.verbose),
    )

    assert geometry.to_string(verbosity=Verbosity.terse) == new_g.to_string(
        verbosity=Verbosity.terse,
    )
    if not geometry:
        return
    assert new_g.geometry
    assert geometry.geometry
    assert type(new_g.geometry) is cls
    for new, orig in zip(new_g.kml_geometries, geometry.kml_geometries):
        if isinstance(new, fastkml.geometry.MultiGeometry):
            continue
        assert not isinstance(orig, fastkml.geometry.MultiGeometry)
        if extrude:
            assert new.extrude == orig.extrude == extrude
        else:
            assert new.extrude is False
        if altitude_mode is None:
            assert new.altitude_mode == AltitudeMode.clamp_to_ground
        else:
            assert new.altitude_mode == orig.altitude_mode == altitude_mode
        if not isinstance(new, fastkml.geometry.Point):
            if tessellate:
                assert new.tessellate == orig.tessellate == tessellate
            else:
                assert new.tessellate is False
    validate(element=new_g.etree_element())


class TestLxml(Lxml):
    """Validation requires lxml."""

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_points(srs=epsg4326),
        ),
    )
    @settings(deadline=1_000)
    def test_multipoint_repr_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiPoint | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_repr_roundtrip(multi_geometry, MultiPoint)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_points(srs=epsg4326),
        ),
    )
    def test_multipoint_str_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiPoint | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip(
            multi_geometry,
            cls=MultiPoint,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_points(srs=epsg4326),
        ),
    )
    def test_multipoint_str_roundtrip_terse(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiPoint | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_terse(
            multi_geometry,
            cls=MultiPoint,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_points(srs=epsg4326),
        ),
    )
    def test_multipoint_str_roundtrip_verbose(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiPoint | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_verbose(
            multi_geometry,
            cls=MultiPoint,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_line_strings(srs=epsg4326),
        ),
    )
    def test_multilinestring_repr_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiLineString | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_repr_roundtrip(multi_geometry, MultiLineString)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_line_strings(srs=epsg4326),
        ),
    )
    def test_multilinestring_str_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiLineString | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip(
            multi_geometry,
            cls=MultiLineString,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_line_strings(srs=epsg4326),
        ),
    )
    def test_multilinestring_str_roundtrip_terse(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiLineString | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_terse(
            multi_geometry,
            cls=MultiLineString,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_line_strings(srs=epsg4326),
        ),
    )
    def test_multilinestring_str_roundtrip_verbose(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiLineString | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_verbose(
            multi_geometry,
            cls=MultiLineString,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_polygons(srs=epsg4326),
        ),
    )
    def test_multipolygon_repr_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiPolygon | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_repr_roundtrip(multi_geometry, MultiPolygon)

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_polygons(srs=epsg4326),
        ),
    )
    def test_multipolygon_str_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiPolygon | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip(
            multi_geometry,
            cls=MultiPolygon,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_polygons(srs=epsg4326),
        ),
    )
    def test_multipolygon_str_roundtrip_terse(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiPolygon | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_terse(
            multi_geometry,
            cls=MultiPolygon,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            multi_polygons(srs=epsg4326),
        ),
    )
    def test_multipolygon_str_roundtrip_verbose(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: MultiPolygon | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        _test_geometry_str_roundtrip_verbose(
            multi_geometry,
            cls=MultiPolygon,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
        )

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            geometry_collections(srs=epsg4326),
        ),
    )
    def test_geometrycollection_repr_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: GeometryCollection | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        new_mg = eval(repr(multi_geometry), {}, eval_locals)  # noqa: S307

        assert multi_geometry == new_mg
        if geometry:
            assert isinstance(
                new_mg.geometry,
                (GeometryCollection, MultiPolygon, MultiLineString, MultiPoint),
            )
        else:
            assert not new_mg

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            geometry_collections(srs=epsg4326),
        ),
    )
    def test_geometrycollection_str_roundtrip(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: GeometryCollection | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        new_mg = fastkml.geometry.MultiGeometry.from_string(
            multi_geometry.to_string(),
        )

        if geometry:
            assert isinstance(
                new_mg.geometry,
                (GeometryCollection, MultiPolygon, MultiLineString, MultiPoint),
            )
        else:
            assert not new_mg

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            geometry_collections(srs=epsg4326),
        ),
    )
    def test_geometrycollection_str_roundtrip_terse(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: GeometryCollection | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        new_mg = fastkml.geometry.MultiGeometry.from_string(
            multi_geometry.to_string(verbosity=Verbosity.terse),
        )

        if geometry:
            assert isinstance(
                new_mg.geometry,
                (GeometryCollection, MultiPolygon, MultiLineString, MultiPoint),
            )
        else:
            assert not new_mg

    @common_geometry(
        geometry=st.one_of(
            st.none(),
            geometry_collections(srs=epsg4326),
        ),
    )
    def test_geometrycollection_str_roundtrip_verbose(
        self,
        id: str | None,
        target_id: str | None,
        extrude: bool | None,
        tessellate: bool | None,
        altitude_mode: AltitudeMode | None,
        geometry: GeometryCollection | None,
    ) -> None:
        multi_geometry = fastkml.geometry.MultiGeometry(
            id=id,
            target_id=target_id,
            extrude=extrude,
            tessellate=tessellate,
            altitude_mode=altitude_mode,
            geometry=geometry,
        )

        new_mg = fastkml.geometry.MultiGeometry.from_string(
            multi_geometry.to_string(verbosity=Verbosity.verbose),
        )

        if geometry:
            assert isinstance(
                new_mg.geometry,
                (GeometryCollection, MultiPolygon, MultiLineString, MultiPoint),
            )
        else:
            assert not new_mg
