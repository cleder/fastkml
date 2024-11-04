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

"""Test the __repr__ and __eq__ methods."""
import difflib
from textwrap import wrap
from typing import Final

from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon

import fastkml
from fastkml.enums import AltitudeMode
from fastkml.enums import PairKey
from tests.base import Lxml
from tests.base import StdLibrary

eval_locals = {
    "Point": Point,
    "Polygon": Polygon,
    "LineString": LineString,
    "LinearRing": LinearRing,
    "AltitudeMode": AltitudeMode,
    "PairKey": PairKey,
    "fastkml": fastkml,
}


class TestRepr(StdLibrary):
    clean_doc: Final = fastkml.kml.KML(
        ns="{http://www.opengis.net/kml/2.2}",
        name_spaces={
            "kml": "{http://www.opengis.net/kml/2.2}",
            "atom": "{http://www.w3.org/2005/Atom}",
            "gx": "{http://www.google.com/kml/ext/2.2}",
        },
        features=[
            fastkml.containers.Document(
                ns="{http://www.opengis.net/kml/2.2}",
                name_spaces={
                    "kml": "{http://www.opengis.net/kml/2.2}",
                    "atom": "{http://www.w3.org/2005/Atom}",
                    "gx": "{http://www.google.com/kml/ext/2.2}",
                },
                id="doc-001",
                target_id="",
                name="Vestibulum eleifend lobortis lorem.",
                visibility=None,
                isopen=None,
                atom_link=None,
                atom_author=None,
                address=None,
                phone_number=None,
                snippet=None,
                description=None,
                view=None,
                times=None,
                style_url=None,
                styles=[
                    fastkml.styles.Style(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="style-001",
                        target_id="",
                        styles=[
                            fastkml.styles.IconStyle(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="",
                                target_id="",
                                color=None,
                                color_mode=None,
                                scale=None,
                                heading=None,
                                icon=fastkml.links.Icon(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="",
                                    target_id="",
                                    href="http://barcelona.galdos.local/svn1/sqa/ets-kml/main/test/data/ogc-kml/images/red-stars.png",
                                    refresh_mode=None,
                                    refresh_interval=None,
                                    view_refresh_mode=None,
                                    view_refresh_time=None,
                                    view_bound_scale=None,
                                    view_format=None,
                                    http_query=None,
                                ),
                                hot_spot=None,
                            ),
                        ],
                    ),
                    fastkml.styles.Style(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="style-002",
                        target_id="",
                        styles=[
                            fastkml.styles.IconStyle(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="",
                                target_id="",
                                color=None,
                                color_mode=None,
                                scale=None,
                                heading=None,
                                icon=fastkml.links.Icon(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="",
                                    target_id="",
                                    href="http://barcelona.galdos.local/svn1/sqa/ets-kml/main/test/data/ogc-kml/images/wht-blank.png",
                                    refresh_mode=None,
                                    refresh_interval=None,
                                    view_refresh_mode=None,
                                    view_refresh_time=None,
                                    view_bound_scale=None,
                                    view_format=None,
                                    http_query=None,
                                ),
                                hot_spot=None,
                            ),
                        ],
                    ),
                    fastkml.styles.Style(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="khStyle712",
                        target_id="",
                        styles=[
                            fastkml.styles.IconStyle(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="khIconStyle716",
                                target_id="",
                                color=None,
                                color_mode=None,
                                scale=None,
                                heading=None,
                                icon=fastkml.links.Icon(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="",
                                    target_id="",
                                    href="http://barcelona.galdos.local/svn1/sqa/ets-kml/main/test/data/ogc-kml/images/9.png",
                                    refresh_mode=None,
                                    refresh_interval=None,
                                    view_refresh_mode=None,
                                    view_refresh_time=None,
                                    view_bound_scale=None,
                                    view_format=None,
                                    http_query=None,
                                ),
                                hot_spot=None,
                            ),
                        ],
                    ),
                    fastkml.styles.Style(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="khStyle887",
                        target_id="",
                        styles=[
                            fastkml.styles.LineStyle(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="khLineStyle890",
                                target_id="",
                                color="7fffffff",
                                color_mode=None,
                                width=None,
                            ),
                            fastkml.styles.PolyStyle(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="khPolyStyle889",
                                target_id="",
                                color="7fa7ce9e",
                                color_mode=None,
                                fill=None,
                                outline=None,
                            ),
                        ],
                    ),
                    fastkml.styles.StyleMap(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="stylemap-001",
                        target_id="",
                        pairs=[
                            fastkml.styles.Pair(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="",
                                target_id="",
                                key=PairKey.normal,
                                style=fastkml.styles.StyleUrl(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="",
                                    target_id="",
                                    url="#style-002",
                                ),
                            ),
                            fastkml.styles.Pair(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="",
                                target_id="",
                                key=PairKey.highlight,
                                style=fastkml.styles.StyleUrl(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="",
                                    target_id="",
                                    url="#style-001",
                                ),
                            ),
                        ],
                    ),
                ],
                region=None,
                extended_data=None,
                features=[
                    fastkml.containers.Folder(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="Folder-001",
                        target_id="",
                        name="Nanaimo, BC",
                        visibility=None,
                        isopen=None,
                        atom_link=None,
                        atom_author=None,
                        address=None,
                        phone_number=None,
                        snippet=None,
                        description=None,
                        view=fastkml.views.LookAt(
                            ns="{http://www.opengis.net/kml/2.2}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            id="",
                            target_id="",
                            longitude=-123.9336542173363,
                            latitude=49.16692307094711,
                            altitude=None,
                            heading=-126.0570028967645,
                            tilt=61.61116895973212,
                            range=359.3753895394523,
                            altitude_mode=AltitudeMode.relative_to_ground,
                            time_primitive=None,
                        ),
                        times=None,
                        style_url=None,
                        styles=[],
                        region=None,
                        extended_data=None,
                        features=[
                            fastkml.containers.Folder(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="",
                                target_id="",
                                name="Downtown Virtual Tours",
                                visibility=None,
                                isopen=None,
                                atom_link=None,
                                atom_author=None,
                                address=None,
                                phone_number=None,
                                snippet=None,
                                description=None,
                                view=None,
                                times=None,
                                style_url=None,
                                styles=[],
                                region=None,
                                extended_data=None,
                                features=[
                                    fastkml.features.Placemark(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        id="",
                                        target_id="",
                                        name="HBC Bastion",
                                        visibility=None,
                                        isopen=None,
                                        atom_link=None,
                                        atom_author=None,
                                        address=None,
                                        phone_number=None,
                                        snippet=None,
                                        description='<a target="_new" href="http://citymap.nanaimo.ca/virtual_tours/viewnode.cfm?File_ID=8">Launch Virtual Tour</a>',
                                        view=None,
                                        times=None,
                                        style_url=fastkml.styles.StyleUrl(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            url="#khStyle712",
                                        ),
                                        styles=[],
                                        region=None,
                                        extended_data=None,
                                        kml_geometry=fastkml.geometry.Point(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            extrude=None,
                                            altitude_mode=AltitudeMode.relative_to_ground,
                                            kml_coordinates=fastkml.geometry.Coordinates(
                                                ns="{http://www.opengis.net/kml/2.2}",
                                                name_spaces={
                                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                                    "atom": "{http://www.w3.org/2005/Atom}",
                                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                                },
                                                coords=[
                                                    (-123.93563168, 49.16716103, 5.0),
                                                ],
                                            ),
                                        ),
                                    ),
                                    fastkml.features.Placemark(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        id="",
                                        target_id="",
                                        name="Building",
                                        visibility=None,
                                        isopen=None,
                                        atom_link=None,
                                        atom_author=None,
                                        address=None,
                                        phone_number=None,
                                        snippet=None,
                                        description=None,
                                        view=None,
                                        times=None,
                                        style_url=fastkml.styles.StyleUrl(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            url="#khStyle887",
                                        ),
                                        styles=[],
                                        region=None,
                                        extended_data=None,
                                        kml_geometry=fastkml.geometry.Polygon(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            extrude=True,
                                            tessellate=None,
                                            altitude_mode=AltitudeMode.absolute,
                                            outer_boundary=fastkml.geometry.OuterBoundaryIs(
                                                ns="{http://www.opengis.net/kml/2.2}",
                                                name_spaces={
                                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                                    "atom": "{http://www.w3.org/2005/Atom}",
                                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                                },
                                                kml_geometry=fastkml.geometry.LinearRing(
                                                    ns="{http://www.opengis.net/kml/2.2}",
                                                    name_spaces={
                                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                                        "atom": "{http://www.w3.org/2005/Atom}",
                                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                                    },
                                                    id="",
                                                    target_id="",
                                                    extrude=None,
                                                    tessellate=None,
                                                    altitude_mode=None,
                                                    geometry=LinearRing(
                                                        (
                                                            (
                                                                -123.940449937288,
                                                                49.16927524669021,
                                                                17.0,
                                                            ),
                                                            (
                                                                -123.940493701601,
                                                                49.1694596207446,
                                                                17.0,
                                                            ),
                                                            (
                                                                -123.940356261489,
                                                                49.16947180231761,
                                                                17.0,
                                                            ),
                                                            (
                                                                -123.940306243823,
                                                                49.1692917061711,
                                                                17.0,
                                                            ),
                                                            (
                                                                -123.940449937288,
                                                                49.16927524669021,
                                                                17.0,
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                    fastkml.features.Placemark(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        id="",
                                        target_id="",
                                        name="Building",
                                        visibility=None,
                                        isopen=None,
                                        atom_link=None,
                                        atom_author=None,
                                        address=None,
                                        phone_number=None,
                                        snippet=None,
                                        description=None,
                                        view=None,
                                        times=None,
                                        style_url=fastkml.styles.StyleUrl(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            url="#khStyle887",
                                        ),
                                        styles=[],
                                        region=None,
                                        extended_data=None,
                                        kml_geometry=fastkml.geometry.Polygon(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            extrude=True,
                                            tessellate=None,
                                            altitude_mode=AltitudeMode.absolute,
                                            outer_boundary=fastkml.geometry.OuterBoundaryIs(
                                                ns="{http://www.opengis.net/kml/2.2}",
                                                name_spaces={
                                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                                    "atom": "{http://www.w3.org/2005/Atom}",
                                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                                },
                                                kml_geometry=fastkml.geometry.LinearRing(
                                                    ns="{http://www.opengis.net/kml/2.2}",
                                                    name_spaces={
                                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                                        "atom": "{http://www.w3.org/2005/Atom}",
                                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                                    },
                                                    id="",
                                                    target_id="",
                                                    extrude=None,
                                                    tessellate=None,
                                                    altitude_mode=None,
                                                    geometry=LinearRing(
                                                        (
                                                            (
                                                                -123.940122952744,
                                                                49.1691287039003,
                                                                18.0,
                                                            ),
                                                            (
                                                                -123.940137225952,
                                                                49.16920143662431,
                                                                18.0,
                                                            ),
                                                            (
                                                                -123.939995940886,
                                                                49.16921364907441,
                                                                18.0,
                                                            ),
                                                            (
                                                                -123.939979331833,
                                                                49.16914300389781,
                                                                18.0,
                                                            ),
                                                            (
                                                                -123.940122952744,
                                                                49.1691287039003,
                                                                18.0,
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                    fastkml.features.Placemark(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        id="",
                                        target_id="",
                                        name="Building",
                                        visibility=None,
                                        isopen=None,
                                        atom_link=None,
                                        atom_author=None,
                                        address=None,
                                        phone_number=None,
                                        snippet=None,
                                        description=None,
                                        view=None,
                                        times=None,
                                        style_url=fastkml.styles.StyleUrl(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            url="#khStyle887",
                                        ),
                                        styles=[],
                                        region=None,
                                        extended_data=None,
                                        kml_geometry=fastkml.geometry.Polygon(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            extrude=True,
                                            tessellate=None,
                                            altitude_mode=AltitudeMode.absolute,
                                            outer_boundary=fastkml.geometry.OuterBoundaryIs(
                                                ns="{http://www.opengis.net/kml/2.2}",
                                                name_spaces={
                                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                                    "atom": "{http://www.w3.org/2005/Atom}",
                                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                                },
                                                kml_geometry=fastkml.geometry.LinearRing(
                                                    ns="{http://www.opengis.net/kml/2.2}",
                                                    name_spaces={
                                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                                        "atom": "{http://www.w3.org/2005/Atom}",
                                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                                    },
                                                    id="",
                                                    target_id="",
                                                    extrude=None,
                                                    tessellate=None,
                                                    altitude_mode=None,
                                                    geometry=LinearRing(
                                                        (
                                                            (
                                                                -123.940353238527,
                                                                49.1688284179789,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940328496557,
                                                                49.1688539816849,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940305627051,
                                                                49.1688410371204,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.94029136599,
                                                                49.1688525752424,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940275724243,
                                                                49.16884496803361,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940267212761,
                                                                49.16885547002801,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940250998683,
                                                                49.1688475077284,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.94024045302,
                                                                49.1688581162214,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940221737029,
                                                                49.1688494547939,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940211083364,
                                                                49.1688603339744,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940178900168,
                                                                49.1688453966693,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940163692655,
                                                                49.1688607198336,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940136059186,
                                                                49.1688470945275,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940162391523,
                                                                49.1688218776622,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940122367227,
                                                                49.1688289487997,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940128827323,
                                                                49.1688475131544,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940088186399,
                                                                49.16885189119151,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940058889981,
                                                                49.1687743342294,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940146366884,
                                                                49.16876417866831,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940150570466,
                                                                49.16876513375031,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940183311773,
                                                                49.16875578354081,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940200543746,
                                                                49.168763737562,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940211624266,
                                                                49.16875150585231,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940229767887,
                                                                49.1687598121941,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940240426635,
                                                                49.1687492027812,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940256088782,
                                                                49.1687578890722,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940267772273,
                                                                49.1687476310603,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940282259105,
                                                                49.1687539885572,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940301511045,
                                                                49.1687371934515,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940335907902,
                                                                49.1687555303004,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940313690715,
                                                                49.1687770262802,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940345414677,
                                                                49.1687916075398,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940321043389,
                                                                49.16881285125181,
                                                                15.0,
                                                            ),
                                                            (
                                                                -123.940353238527,
                                                                49.1688284179789,
                                                                15.0,
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                    fastkml.features.Placemark(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        id="",
                                        target_id="",
                                        name="Building",
                                        visibility=None,
                                        isopen=None,
                                        atom_link=None,
                                        atom_author=None,
                                        address=None,
                                        phone_number=None,
                                        snippet=None,
                                        description=None,
                                        view=None,
                                        times=None,
                                        style_url=fastkml.styles.StyleUrl(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            url="#khStyle887",
                                        ),
                                        styles=[],
                                        region=None,
                                        extended_data=None,
                                        kml_geometry=fastkml.geometry.Polygon(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            extrude=True,
                                            tessellate=None,
                                            altitude_mode=AltitudeMode.absolute,
                                            outer_boundary=fastkml.geometry.OuterBoundaryIs(
                                                ns="{http://www.opengis.net/kml/2.2}",
                                                name_spaces={
                                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                                    "atom": "{http://www.w3.org/2005/Atom}",
                                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                                },
                                                kml_geometry=fastkml.geometry.LinearRing(
                                                    ns="{http://www.opengis.net/kml/2.2}",
                                                    name_spaces={
                                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                                        "atom": "{http://www.w3.org/2005/Atom}",
                                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                                    },
                                                    id="",
                                                    target_id="",
                                                    extrude=None,
                                                    tessellate=None,
                                                    altitude_mode=None,
                                                    geometry=LinearRing(
                                                        (
                                                            (
                                                                -123.935755404797,
                                                                49.1660852779118,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.93582067022,
                                                                49.1660311465527,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.935800492118,
                                                                49.1660168302278,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.936039795526,
                                                                49.165822245592,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.936064357298,
                                                                49.1658350873476,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.936179746682,
                                                                49.1657457438265,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.936369720217,
                                                                49.1657486103712,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.936512648837,
                                                                49.1658300134091,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.936229647663,
                                                                49.16604662814821,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.936209525388,
                                                                49.1660352793624,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.935976452504,
                                                                49.16621236606521,
                                                                25.0,
                                                            ),
                                                            (
                                                                -123.935755404797,
                                                                49.1660852779118,
                                                                25.0,
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                            inner_boundaries=[
                                                fastkml.geometry.InnerBoundaryIs(
                                                    ns="{http://www.opengis.net/kml/2.2}",
                                                    name_spaces={
                                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                                        "atom": "{http://www.w3.org/2005/Atom}",
                                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                                    },
                                                    kml_geometry=fastkml.geometry.LinearRing(
                                                        ns="{http://www.opengis.net/kml/2.2}",
                                                        name_spaces={
                                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                                            "atom": "{http://www.w3.org/2005/Atom}",
                                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                                        },
                                                        id="",
                                                        target_id="",
                                                        extrude=None,
                                                        tessellate=None,
                                                        altitude_mode=None,
                                                        geometry=LinearRing(
                                                            (
                                                                (
                                                                    -123.935774273544,
                                                                    49.1660841356946,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935975080821,
                                                                    49.16619960613241,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936199121569,
                                                                    49.1660294278725,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936199903082,
                                                                    49.16602888191441,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936200797694,
                                                                    49.1660283350392,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936201694,
                                                                    49.16602787808731,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936202592002,
                                                                    49.16602751105871,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936203603103,
                                                                    49.1660271431131,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936204615898,
                                                                    49.16602686509071,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936205743487,
                                                                    49.1660266760745,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936206871076,
                                                                    49.1660264870584,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.93620800036,
                                                                    49.16602638796551,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936209129645,
                                                                    49.1660262888725,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936210260625,
                                                                    49.1660262797028,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.9362113933,
                                                                    49.1660263604563,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936212527671,
                                                                    49.16602653113311,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936213548944,
                                                                    49.1660267027268,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.93621468501,
                                                                    49.16602696332681,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936215707978,
                                                                    49.1660272248437,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936216732642,
                                                                    49.1660275762838,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936217645904,
                                                                    49.16602801856421,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936218559165,
                                                                    49.16602846084461,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936228164518,
                                                                    49.1660339590587,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936493324423,
                                                                    49.1658309795689,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936364459423,
                                                                    49.1657575567936,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936186026871,
                                                                    49.1657548664825,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936074872463,
                                                                    49.1658408480101,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936074315451,
                                                                    49.1658413022105,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936073532244,
                                                                    49.1658417582446,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936072637635,
                                                                    49.1658423051187,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936071739635,
                                                                    49.1658426721463,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936070728538,
                                                                    49.16584304009081,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.93606971744,
                                                                    49.1658434080353,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936068589855,
                                                                    49.16584359705011,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936067577062,
                                                                    49.16584387507131,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936066447782,
                                                                    49.1658439741628,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936065318501,
                                                                    49.1658440732543,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936064187525,
                                                                    49.1658440824226,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936063054855,
                                                                    49.1658440016676,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936061922184,
                                                                    49.1658439209126,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936060787817,
                                                                    49.16584375023431,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936059653451,
                                                                    49.1658435795561,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936058628792,
                                                                    49.1658432281144,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936057605828,
                                                                    49.1658429665961,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936056692572,
                                                                    49.1658425243144,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936055779315,
                                                                    49.1658420820327,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.936041957201,
                                                                    49.165834909184,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.93581858271,
                                                                    49.1660164138055,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935830850283,
                                                                    49.1660251282083,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.93583153904,
                                                                    49.1660256622482,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935832229491,
                                                                    49.1660262862113,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935832806845,
                                                                    49.166026911091,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.9358332711,
                                                                    49.16602753688741,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935833737051,
                                                                    49.1660282526069,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935833976805,
                                                                    49.16602897015971,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935834216559,
                                                                    49.1660296877125,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935834343216,
                                                                    49.1660304061819,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935834471567,
                                                                    49.1660312145745,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935834372027,
                                                                    49.1660319348771,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935834272488,
                                                                    49.16603265517961,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935833946752,
                                                                    49.16603337731541,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935833621016,
                                                                    49.16603409945121,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935833295281,
                                                                    49.166034821587,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935832741654,
                                                                    49.1660354556328,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935832188028,
                                                                    49.1660360896785,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935831521303,
                                                                    49.1660367246408,
                                                                    25.0,
                                                                ),
                                                                (
                                                                    -123.935774273544,
                                                                    49.1660841356946,
                                                                    25.0,
                                                                ),
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    fastkml.features.Placemark(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="",
                        target_id="",
                        name="General Motors Place",
                        visibility=None,
                        isopen=None,
                        atom_link=fastkml.atom.Link(
                            ns="{http://www.w3.org/2005/Atom}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            href="http://en.wikipedia.org/wiki/General_Motors_Place",
                            rel="related",
                            type="text/html",
                            hreflang="en",
                            title="Wikipedia entry",
                            length=None,
                        ),
                        atom_author=fastkml.atom.Author(
                            ns="{http://www.w3.org/2005/Atom}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            name="Phineas Fogg",
                            uri=None,
                            email=None,
                        ),
                        address=None,
                        phone_number="tel:+1-604-899-7400",
                        snippet=None,
                        description="General Motors Place (), sponsored by General Motors Canada,\n      is an indoor arena at 800 Griffiths Way in Vancouver, British Columbia,\n      Canada. Completed in 1995 at a cost of CAD $160 million in private\n      financing, the arena is home to the Vancouver Canucks of the NHL, and\n      was formerly home to the Vancouver Grizzlies of the NBA and the Vancouver\n      Ravens of the NLL. The Grizzlies have since moved to Memphis. The arena\n      seats 18,630 for ice hockey and 19,193 for basketball. It has 88 luxury suites,\n      12 hospitality suites, and 2,195 club seats. The arena replaced the\n      Pacific Coliseum as the main venue for events in Vancouver.",
                        view=None,
                        times=None,
                        style_url=None,
                        styles=[],
                        region=None,
                        extended_data=None,
                        kml_geometry=fastkml.geometry.Point(
                            ns="{http://www.opengis.net/kml/2.2}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            id="",
                            target_id="",
                            extrude=None,
                            altitude_mode=None,
                            kml_coordinates=fastkml.geometry.Coordinates(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                coords=[(-123.1097, 49.2774, 0.0)],
                            ),
                        ),
                    ),
                    fastkml.features.Placemark(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="VFS",
                        target_id="",
                        name="Vancouver Film Studios",
                        visibility=None,
                        isopen=None,
                        atom_link=fastkml.atom.Link(
                            ns="{http://www.w3.org/2005/Atom}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            href="http://www.vancouverfilmstudios.com/",
                            rel="related",
                            type="text/html",
                            hreflang="en",
                            title="Welcome to Vancouver Film Studios",
                            length=None,
                        ),
                        atom_author=None,
                        address="3500 Cornett Rd, Vancouver, BC, Canada",
                        phone_number=None,
                        snippet=None,
                        description="Situated on nearly two city blocks of land just fifteen minutes from\n          downtown Vancouver, British Columbia, Vancouver Film Studios (VFS) is\n          Canada's premier motion picture production complex.",
                        view=fastkml.views.LookAt(
                            ns="{http://www.opengis.net/kml/2.2}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            id="",
                            target_id="",
                            longitude=-123.0281012076333,
                            latitude=49.26140654323342,
                            altitude=0.0,
                            heading=0.0,
                            tilt=51.96,
                            range=301.9568,
                            altitude_mode=AltitudeMode.relative_to_ground,
                            time_primitive=None,
                        ),
                        times=None,
                        style_url=None,
                        styles=[
                            fastkml.styles.StyleMap(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                id="",
                                target_id="",
                                pairs=[
                                    fastkml.styles.Pair(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        id="",
                                        target_id="",
                                        key=PairKey.normal,
                                        style=fastkml.styles.Style(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            styles=[
                                                fastkml.styles.IconStyle(
                                                    ns="{http://www.opengis.net/kml/2.2}",
                                                    name_spaces={
                                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                                        "atom": "{http://www.w3.org/2005/Atom}",
                                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                                    },
                                                    id="",
                                                    target_id="",
                                                    color=None,
                                                    color_mode=None,
                                                    scale=None,
                                                    heading=None,
                                                    icon=fastkml.links.Icon(
                                                        ns="{http://www.opengis.net/kml/2.2}",
                                                        name_spaces={
                                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                                            "atom": "{http://www.w3.org/2005/Atom}",
                                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                                        },
                                                        id="",
                                                        target_id="",
                                                        href="http://maps.google.com/mapfiles/kml/paddle/go.png",
                                                        refresh_mode=None,
                                                        refresh_interval=None,
                                                        view_refresh_mode=None,
                                                        view_refresh_time=None,
                                                        view_bound_scale=None,
                                                        view_format=None,
                                                        http_query=None,
                                                    ),
                                                    hot_spot=None,
                                                ),
                                            ],
                                        ),
                                    ),
                                    fastkml.styles.Pair(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        id="",
                                        target_id="",
                                        key=PairKey.highlight,
                                        style=fastkml.styles.Style(
                                            ns="{http://www.opengis.net/kml/2.2}",
                                            name_spaces={
                                                "kml": "{http://www.opengis.net/kml/2.2}",
                                                "atom": "{http://www.w3.org/2005/Atom}",
                                                "gx": "{http://www.google.com/kml/ext/2.2}",
                                            },
                                            id="",
                                            target_id="",
                                            styles=[
                                                fastkml.styles.IconStyle(
                                                    ns="{http://www.opengis.net/kml/2.2}",
                                                    name_spaces={
                                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                                        "atom": "{http://www.w3.org/2005/Atom}",
                                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                                    },
                                                    id="",
                                                    target_id="",
                                                    color=None,
                                                    color_mode=None,
                                                    scale=1.3,
                                                    heading=None,
                                                    icon=fastkml.links.Icon(
                                                        ns="{http://www.opengis.net/kml/2.2}",
                                                        name_spaces={
                                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                                            "atom": "{http://www.w3.org/2005/Atom}",
                                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                                        },
                                                        id="",
                                                        target_id="",
                                                        href="http://maps.google.com/mapfiles/kml/paddle/go.png",
                                                        refresh_mode=None,
                                                        refresh_interval=None,
                                                        view_refresh_mode=None,
                                                        view_refresh_time=None,
                                                        view_bound_scale=None,
                                                        view_format=None,
                                                        http_query=None,
                                                    ),
                                                    hot_spot=None,
                                                ),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ],
                        region=None,
                        extended_data=fastkml.data.ExtendedData(
                            ns="{http://www.opengis.net/kml/2.2}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            id="ed-001",
                            target_id="",
                            elements=[
                                fastkml.data.Data(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="",
                                    target_id="",
                                    name="nStages",
                                    value="13",
                                    display_name="Number of sound stages",
                                ),
                                fastkml.data.Data(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="",
                                    target_id="",
                                    name="helipad",
                                    value="yes",
                                    display_name="Helipad?",
                                ),
                            ],
                        ),
                        kml_geometry=fastkml.geometry.Point(
                            ns="{http://www.opengis.net/kml/2.2}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            id="",
                            target_id="",
                            extrude=None,
                            altitude_mode=None,
                            kml_coordinates=fastkml.geometry.Coordinates(
                                ns="{http://www.opengis.net/kml/2.2}",
                                name_spaces={
                                    "kml": "{http://www.opengis.net/kml/2.2}",
                                    "atom": "{http://www.w3.org/2005/Atom}",
                                    "gx": "{http://www.google.com/kml/ext/2.2}",
                                },
                                coords=[(-123.028369, 49.26107900000001, 0.0)],
                            ),
                        ),
                    ),
                    fastkml.features.Placemark(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="",
                        target_id="",
                        name=None,
                        visibility=None,
                        isopen=None,
                        atom_link=None,
                        atom_author=None,
                        address=None,
                        phone_number=None,
                        snippet=None,
                        description="Navigation buoys in Vancouver harbour",
                        view=None,
                        times=None,
                        style_url=None,
                        styles=[],
                        region=None,
                        extended_data=None,
                        kml_geometry=fastkml.geometry.MultiGeometry(
                            ns="{http://www.opengis.net/kml/2.2}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            id="geom-001",
                            target_id="",
                            kml_geometries=[
                                fastkml.geometry.Point(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="b385.5",
                                    target_id="",
                                    extrude=None,
                                    altitude_mode=None,
                                    kml_coordinates=fastkml.geometry.Coordinates(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        coords=[(-123.3215766, 49.2760338, 0.0)],
                                    ),
                                ),
                                fastkml.geometry.Point(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="b386",
                                    target_id="",
                                    extrude=None,
                                    altitude_mode=None,
                                    kml_coordinates=fastkml.geometry.Coordinates(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        coords=[(-123.2643704, 49.3301853, 0.0)],
                                    ),
                                ),
                                fastkml.geometry.Point(
                                    ns="{http://www.opengis.net/kml/2.2}",
                                    name_spaces={
                                        "kml": "{http://www.opengis.net/kml/2.2}",
                                        "atom": "{http://www.w3.org/2005/Atom}",
                                        "gx": "{http://www.google.com/kml/ext/2.2}",
                                    },
                                    id="b386.3",
                                    target_id="",
                                    extrude=None,
                                    altitude_mode=None,
                                    kml_coordinates=fastkml.geometry.Coordinates(
                                        ns="{http://www.opengis.net/kml/2.2}",
                                        name_spaces={
                                            "kml": "{http://www.opengis.net/kml/2.2}",
                                            "atom": "{http://www.w3.org/2005/Atom}",
                                            "gx": "{http://www.google.com/kml/ext/2.2}",
                                        },
                                        coords=[(-123.2477084, 49.2890857, 0.0)],
                                    ),
                                ),
                            ],
                        ),
                    ),
                    fastkml.features.Placemark(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="",
                        target_id="",
                        name="Rivière des Outaouais",
                        visibility=None,
                        isopen=True,
                        atom_link=None,
                        atom_author=None,
                        address=None,
                        phone_number=None,
                        snippet=None,
                        description="Vue du ciel, la rivière des Outaouais est le principal élément naturel\n          de la vallée du même nom. Cette splendide rivière, la deuxième plus\n          grande dans l'est du Canada, possède un bassin hydrographique de 140 000\n          km2 et s'étend sure plus de 1 271 km, en majeure partie dans le Bouclier\n          canadien.",
                        view=None,
                        times=None,
                        style_url=None,
                        styles=[],
                        region=None,
                        extended_data=None,
                        kml_geometry=fastkml.geometry.LineString(
                            ns="{http://www.opengis.net/kml/2.2}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            id="ed-003",
                            target_id="",
                            extrude=None,
                            tessellate=None,
                            altitude_mode=None,
                            geometry=LineString(
                                (
                                    (-74.08, 45.45, 19.0),
                                    (-74.25, 45.51, 23.0),
                                    (-74.33, 45.51, 22.0),
                                    (-74.36, 45.55, 22.0),
                                    (-74.39, 45.57, 29.0),
                                    (-74.44, 45.57, 35.0),
                                    (-74.48, 45.6, 35.0),
                                    (-74.52, 45.59, 32.0),
                                    (-74.55, 45.6, 32.0),
                                    (-74.6, 45.62, 32.0),
                                ),
                            ),
                        ),
                    ),
                    fastkml.features.Placemark(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="place-100",
                        target_id="",
                        name=None,
                        visibility=None,
                        isopen=None,
                        atom_link=None,
                        atom_author=None,
                        address=None,
                        phone_number=None,
                        snippet=None,
                        description="Sampling loop",
                        view=None,
                        times=None,
                        style_url=None,
                        styles=[],
                        region=None,
                        extended_data=None,
                        kml_geometry=fastkml.geometry.LinearRing(
                            ns="{http://www.opengis.net/kml/2.2}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            id="",
                            target_id="",
                            extrude=None,
                            tessellate=False,
                            altitude_mode=None,
                            geometry=LinearRing(
                                (
                                    (-65.679, 47.43),
                                    (-65.73, 47.456),
                                    (-65.72, 47.461),
                                    (-65.669, 47.439),
                                    (-65.679, 47.43),
                                ),
                            ),
                        ),
                    ),
                    fastkml.features.Placemark(
                        ns="{http://www.opengis.net/kml/2.2}",
                        name_spaces={
                            "kml": "{http://www.opengis.net/kml/2.2}",
                            "atom": "{http://www.w3.org/2005/Atom}",
                            "gx": "{http://www.google.com/kml/ext/2.2}",
                        },
                        id="VPL",
                        target_id="",
                        name="Vancouver Public Library",
                        visibility=None,
                        isopen=None,
                        atom_link=fastkml.atom.Link(
                            ns="{http://www.w3.org/2005/Atom}",
                            name_spaces={
                                "kml": "{http://www.opengis.net/kml/2.2}",
                                "atom": "{http://www.w3.org/2005/Atom}",
                                "gx": "{http://www.google.com/kml/ext/2.2}",
                            },
                            href="http://www.vpl.ca/",
                            rel="related",
                            type="text/html",
                            hreflang="en",
                            title="Vancouver Public Library - Home",
                            length=None,
                        ),
                        atom_author=None,
                        address=None,
                        phone_number=None,
                        snippet=None,
                        description="Funded by the City of Vancouver, Vancouver Public Library is the third\n          largest public library system in Canada, with over 373,000 cardholders\n          and more than 9 million items borrowed annually. Today, with exceptional\n          collections, services and technologies offered at 22 branches and an\n          extensive virtual library, VPL is accessible to all citizens of Vancouver.",
                        view=None,
                        times=None,
                        style_url=None,
                        styles=[],
                        region=None,
                        extended_data=None,
                        kml_geometry=None,
                    ),
                ],
                schemata=[],
            ),
        ],
    )

    def diff_compare(self, a: str, b: str) -> None:
        """Compare two strings and print the differences."""
        differ = difflib.Differ()
        for line, d in enumerate(differ.compare(a.split(), b.split())):
            if d[0] in ("+", "-"):
                print(line, d)  # noqa: T201

        for i, chunk in enumerate(zip(wrap(a, 100), wrap(b, 100))):
            if chunk[0] != chunk[1]:
                print(i * 100)  # noqa: T201
                print(chunk[0])  # noqa: T201
                print(chunk[1])  # noqa: T201

    def test_repr(self) -> None:
        """Test the __repr__ method."""
        new_doc = eval(repr(self.clean_doc), {}, eval_locals)  # noqa: S307

        assert new_doc == self.clean_doc
        assert repr(new_doc) == repr(self.clean_doc)

    def test_str(self) -> None:
        """Test the __str__ method."""
        assert str(self.clean_doc) == self.clean_doc.to_string()

    def test_eq_str_round_trip(self) -> None:
        """Test the equality of the original and the round-tripped document."""
        new_doc = fastkml.KML.from_string(self.clean_doc.to_string(precision=15))

        assert str(self.clean_doc) == str(new_doc)
        assert repr(new_doc) == repr(self.clean_doc)
        # srict equality is not a given new_doc == self.clean_doc


class TestReprLxml(Lxml, TestRepr):
    """Test the __repr__ and __str__ methods of the KML document with lxml."""
