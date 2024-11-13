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

"""Custom hypothesis strategies for testing."""

import datetime
import re
import string
from functools import partial
from typing import Final
from urllib.parse import urlencode

from hypothesis import strategies as st
from hypothesis.extra.dateutil import timezones
from pygeoif.hypothesis import strategies as geo_st

import fastkml.enums
import fastkml.gx
import fastkml.links
import fastkml.styles
from fastkml.times import KmlDateTime
from fastkml.views import LatLonAltBox
from fastkml.views import Lod

ID_TEXT: Final = string.ascii_letters + string.digits + ".-_"

nc_name = partial(
    st.from_regex,
    regex=re.compile(r"^[A-Za-z_][\w.-]*$"),
    alphabet=ID_TEXT,
    fullmatch=True,
)

href_langs = partial(
    st.from_regex,
    regex=re.compile(r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?$"),
    alphabet=f"{string.ascii_letters}-{string.digits}",
    fullmatch=True,
)

media_types = partial(
    st.from_regex,
    regex=re.compile(r"^[a-zA-Z0-9-]+/[a-zA-Z0-9-]+$"),
    alphabet=f"{string.ascii_letters}/-{string.digits}",
    fullmatch=True,
)

xml_text = partial(
    st.text,
    alphabet=st.characters(min_codepoint=1, blacklist_categories=("Cc", "Cs")),
)

uri_text = partial(
    st.from_regex,
    regex=re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://([^/?#]*)([^#]*)(#.*)?$"),
    alphabet=f"{string.ascii_letters}{string.digits}+-._~:/?#[]@!$&'()*+,;=%",
    fullmatch=True,
)

kml_datetimes = partial(
    st.builds,
    KmlDateTime,
    dt=st.one_of(
        st.dates(
            min_value=datetime.date(2000, 1, 1),
            max_value=datetime.date(2050, 1, 1),
        ),
        st.datetimes(
            allow_imaginary=False,
            timezones=timezones(),
            min_value=datetime.datetime(2000, 1, 1),  # noqa: DTZ001
            max_value=datetime.datetime(2050, 1, 1),  # noqa: DTZ001
        ),
    ),
    resolution=st.one_of(
        st.none(),
        st.one_of(st.none(), st.sampled_from(fastkml.enums.DateTimeResolution)),
    ),
)

geometries = partial(
    st.one_of,
    (
        geo_st.points(srs=geo_st.epsg4326),
        geo_st.line_strings(srs=geo_st.epsg4326),
        geo_st.linear_rings(srs=geo_st.epsg4326),
        geo_st.polygons(srs=geo_st.epsg4326),
        geo_st.multi_points(srs=geo_st.epsg4326),
        geo_st.multi_line_strings(srs=geo_st.epsg4326),
        geo_st.multi_polygons(srs=geo_st.epsg4326),
    ),
)
lods = partial(
    st.builds,
    Lod,
    min_lod_pixels=st.integers(),
    max_lod_pixels=st.integers(),
    min_fade_extent=st.integers(),
    max_fade_extent=st.integers(),
)

lat_lon_alt_boxes = partial(
    st.builds,
    LatLonAltBox,
    north=st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=90),
    south=st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=90),
    east=st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=180),
    west=st.floats(allow_nan=False, allow_infinity=False, min_value=0, max_value=180),
    min_altitude=st.floats(allow_nan=False, allow_infinity=False).filter(
        lambda x: x != 0,
    ),
    max_altitude=st.floats(allow_nan=False, allow_infinity=False).filter(
        lambda x: x != 0,
    ),
    altitude_mode=st.sampled_from(fastkml.enums.AltitudeMode),
)

kml_colors = partial(
    st.text,
    alphabet=string.hexdigits,
    min_size=8,
    max_size=8,
)

styles = partial(
    st.one_of,
    st.builds(
        fastkml.styles.LabelStyle,
        color=kml_colors(),
        color_mode=st.sampled_from(fastkml.enums.ColorMode),
        scale=st.floats(allow_nan=False, allow_infinity=False),
    ),
    st.builds(
        fastkml.styles.LineStyle,
        color=kml_colors(),
        color_mode=st.sampled_from(fastkml.enums.ColorMode),
        width=st.floats(allow_nan=False, allow_infinity=False, min_value=0),
    ),
    st.builds(
        fastkml.styles.PolyStyle,
        color=kml_colors(),
        color_mode=st.sampled_from(fastkml.enums.ColorMode),
        fill=st.booleans(),
        outline=st.booleans(),
    ),
    st.builds(
        fastkml.styles.BalloonStyle,
        bg_color=kml_colors(),
        text_color=kml_colors(),
        text=xml_text(min_size=1, max_size=256).filter(lambda x: x.strip() != ""),
        display_mode=st.sampled_from(fastkml.enums.DisplayMode),
    ),
)

track_items = partial(
    st.builds,
    fastkml.gx.TrackItem,
    angle=st.builds(
        fastkml.gx.Angle,
        heading=st.floats(allow_nan=False, allow_infinity=False),
        roll=st.floats(allow_nan=False, allow_infinity=False),
        tilt=st.floats(allow_nan=False, allow_infinity=False),
    ),
    coord=geo_st.points(srs=geo_st.epsg4326),
    when=kml_datetimes(),
)


@st.composite
def query_strings(draw: st.DrawFn) -> str:
    params = draw(
        st.dictionaries(
            keys=st.text(alphabet=string.ascii_letters, min_size=1),
            values=st.text(alphabet=string.printable),
        ),
    )
    return urlencode(params)
