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

ID_TEXT = string.ascii_letters + string.digits + string.punctuation


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_points(srs=epsg4326),
    ),
)
def test_multipoint_repr_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiPoint],
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
        assert isinstance(new_mg.geometry, MultiPoint)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_points(srs=epsg4326),
    ),
)
def test_multipoint_str_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiPoint],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(),
    )

    assert multi_geometry.to_string() == new_mg.to_string()
    assert multi_geometry == new_mg
    if geometry:
        assert isinstance(new_mg.geometry, MultiPoint)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_points(srs=epsg4326),
    ),
)
def test_multipoint_str_roundtrip_terse(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiPoint],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(verbosity=Verbosity.terse),
    )

    assert multi_geometry.to_string(verbosity=Verbosity.verbose) == new_mg.to_string(
        verbosity=Verbosity.verbose,
    )
    if geometry:
        assert isinstance(new_mg.geometry, MultiPoint)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_points(srs=epsg4326),
    ),
)
def test_multipoint_str_roundtrip_verbose(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiPoint],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(verbosity=Verbosity.verbose),
    )

    assert multi_geometry.to_string(verbosity=Verbosity.verbose) == new_mg.to_string(
        verbosity=Verbosity.verbose,
    )
    if geometry:
        assert isinstance(new_mg.geometry, MultiPoint)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_line_strings(srs=epsg4326),
    ),
)
def test_multilinestring_repr_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiLineString],
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
        assert isinstance(new_mg.geometry, MultiLineString)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_line_strings(srs=epsg4326),
    ),
)
def test_multilinestring_str_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiLineString],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(),
    )

    assert multi_geometry.to_string() == new_mg.to_string()
    assert multi_geometry == new_mg
    if geometry:
        assert isinstance(new_mg.geometry, MultiLineString)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_line_strings(srs=epsg4326),
    ),
)
def test_multilinestring_str_roundtrip_terse(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiLineString],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(verbosity=Verbosity.terse),
    )

    assert multi_geometry.to_string(verbosity=Verbosity.verbose) == new_mg.to_string(
        verbosity=Verbosity.verbose,
    )
    if geometry:
        assert isinstance(new_mg.geometry, MultiLineString)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_line_strings(srs=epsg4326),
    ),
)
def test_multilinestring_str_roundtrip_verbose(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiLineString],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(verbosity=Verbosity.verbose),
    )

    assert multi_geometry.to_string(verbosity=Verbosity.verbose) == new_mg.to_string(
        verbosity=Verbosity.verbose,
    )
    if geometry:
        assert isinstance(new_mg.geometry, MultiLineString)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_polygons(srs=epsg4326),
    ),
)
def test_multipolygon_repr_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiPolygon],
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
        assert isinstance(new_mg.geometry, MultiPolygon)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_polygons(srs=epsg4326),
    ),
)
def test_multipolygon_str_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiPolygon],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(),
    )

    assert multi_geometry.to_string() == new_mg.to_string()
    assert multi_geometry == new_mg
    if geometry:
        assert isinstance(new_mg.geometry, MultiPolygon)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_polygons(srs=epsg4326),
    ),
)
def test_multipolygon_str_roundtrip_terse(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiPolygon],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(verbosity=Verbosity.terse),
    )

    assert multi_geometry.to_string(verbosity=Verbosity.verbose) == new_mg.to_string(
        verbosity=Verbosity.verbose,
    )
    if geometry:
        assert isinstance(new_mg.geometry, MultiPolygon)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        multi_polygons(srs=epsg4326),
    ),
)
def test_multipolygon_str_roundtrip_verbose(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[MultiPolygon],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(verbosity=Verbosity.verbose),
    )

    assert multi_geometry.to_string(verbosity=Verbosity.verbose) == new_mg.to_string(
        verbosity=Verbosity.verbose,
    )
    if geometry:
        assert isinstance(new_mg.geometry, MultiPolygon)


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        geometry_collections(srs=epsg4326),
    ),
)
def test_geometrycollection_repr_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[GeometryCollection],
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


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        geometry_collections(srs=epsg4326),
    ),
)
def test_geometrycollection_str_roundtrip(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[GeometryCollection],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(),
    )

    if geometry:
        assert isinstance(
            new_mg.geometry,
            (GeometryCollection, MultiPolygon, MultiLineString, MultiPoint),
        )
    else:
        assert not new_mg


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        geometry_collections(srs=epsg4326),
    ),
)
def test_geometrycollection_str_roundtrip_terse(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[GeometryCollection],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(verbosity=Verbosity.terse),
    )

    if geometry:
        assert isinstance(
            new_mg.geometry,
            (GeometryCollection, MultiPolygon, MultiLineString, MultiPoint),
        )
    else:
        assert not new_mg


@given(
    id=st.one_of(st.none(), st.text(alphabet=ID_TEXT)),
    target_id=st.one_of(st.none(), st.text(ID_TEXT)),
    extrude=st.one_of(st.none(), st.booleans()),
    tessellate=st.one_of(st.none(), st.booleans()),
    altitude_mode=st.one_of(st.none(), st.sampled_from(AltitudeMode)),
    geometry=st.one_of(
        st.none(),
        geometry_collections(srs=epsg4326),
    ),
)
def test_geometrycollection_str_roundtrip_verbose(
    id: typing.Optional[str],
    target_id: typing.Optional[str],
    extrude: typing.Optional[bool],
    tessellate: typing.Optional[bool],
    altitude_mode: typing.Optional[AltitudeMode],
    geometry: typing.Optional[GeometryCollection],
) -> None:
    multi_geometry = fastkml.geometry.MultiGeometry(
        id=id,
        target_id=target_id,
        extrude=extrude,
        tessellate=tessellate,
        altitude_mode=altitude_mode,
        geometry=geometry,
    )

    new_mg = fastkml.geometry.MultiGeometry.class_from_string(
        multi_geometry.to_string(verbosity=Verbosity.verbose),
    )

    if geometry:
        assert isinstance(
            new_mg.geometry,
            (GeometryCollection, MultiPolygon, MultiLineString, MultiPoint),
        )
    else:
        assert not new_mg
