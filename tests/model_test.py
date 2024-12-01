# Copyright (C) 2021 - 2023  Christian Ledermann
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

"""Test the kml overlay classes."""

from pygeoif.geometry import Point

import fastkml.links
import fastkml.model
from fastkml.enums import AltitudeMode
from tests.base import Lxml
from tests.base import StdLibrary


class TestModel(StdLibrary):
    def test_from_string(self) -> None:
        doc = (
            '<Model xmlns="http://www.opengis.net/kml/2.2">'
            "<altitudeMode>absolute</altitudeMode>"
            "<Location>"
            "<longitude>-123.115776547816</longitude>"
            "<latitude>49.279804095564</latitude>"
            "<altitude>21.614010375743</altitude>"
            "</Location>"
            "<Scale><x>1</x><y>1</y><z>1</z></Scale>"
            "<Link><href>http://barcelona.galdos.local/files/PublicLibrary.dae</href></Link>"
            '<ResourceMap id="map01">'
            "<Alias>"
            "<targetHref>http://barcelona.galdos.local/images/Concrete2.jpg</targetHref>"
            "<sourceHref>../images/Concrete.jpg</sourceHref>"
            "</Alias>"
            "</ResourceMap>"
            "</Model>"
        )

        model = fastkml.model.Model.from_string(doc)
        assert model.altitude_mode == AltitudeMode.absolute
        assert model.geometry == Point(
            -123.115776547816,
            49.279804095564,
            21.614010375743,
        )
        assert model == fastkml.model.Model(
            altitude_mode=AltitudeMode.absolute,
            location=fastkml.model.Location(
                altitude=21.614010375743,
                latitude=49.279804095564,
                longitude=-123.115776547816,
            ),
            orientation=None,
            scale=fastkml.model.Scale(
                x=1.0,
                y=1.0,
                z=1.0,
            ),
            link=fastkml.links.Link(
                href="http://barcelona.galdos.local/files/PublicLibrary.dae",
            ),
            resource_map=fastkml.model.ResourceMap(
                aliases=[
                    fastkml.model.Alias(
                        target_href="http://barcelona.galdos.local/images/Concrete2.jpg",
                        source_href="../images/Concrete.jpg",
                    ),
                ],
            ),
        )


class TestModelLxml(TestModel, Lxml):
    pass
