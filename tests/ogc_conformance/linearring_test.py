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
"""
Round-trip the two bare <LinearRing> fragments in the OGC conformance suite.

Both fixtures' root element is a bare `kml:LinearRing`, not a full <kml>
document, so fastkml.kml.KML.parse() is the wrong entry point -- it would
silently return an empty <kml/> stub, discarding the content with no
exception. The correct entry point for a bare geometry fragment is the
element class's own from_string() (which takes decoded text, not bytes).
"""

from xmldiff import actions

import fastkml.validator
from fastkml.geometry import LinearRing
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR
from tests.ogc_conformance._helpers import xmldiff


class TestLxml(Lxml):
    """Test with lxml."""

    def test_linear_ring_with_1d_tuple(self) -> None:
        """
        A coordinate tuple missing its latitude ("-118.0," with nothing after it).

        This is a genuine parser edge case, not just a formatting difference:
        fastkml's coordinate splitting merges the malformed 1D tuple with the
        next one ("-118.0," + "-118.0,50.0" -> "-118.0,-118.0,50.0"), silently
        changing the ring from 5 tuples to 4 -- pygeoif then refuses to build a
        geometry from the result at all (`.geometry` is None). Pinned here as
        documented, known-lossy behavior, not something to silently accept.
        """
        fixture = KMLFILEDIR / "LinearRingWith1DTuple.kml"
        expected = fixture.read_bytes()

        geom = LinearRing.from_string(fixture.read_text(encoding="utf-8"))
        actual = geom.to_string()

        assert geom.geometry is None
        diff = xmldiff(actual, expected)
        assert diff == [
            actions.InsertNamespace(prefix=None, uri="http://www.opengis.net/kml/2.2"),
            actions.DeleteNamespace(prefix="kml"),
            actions.UpdateTextIn(
                node="/kml:LinearRing/kml:coordinates[1]",
                text="-124.0,50.0 -124.0,46.0 -118.0,  -118.0,50.0 -124.0,50.0",
                oldtext="-124.0,50.0 -124.0,46.0 -118.0,-118.0,50.0 -124.0,50.0",
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_linear_ring_with_invalid_lat(self) -> None:
        """
        A coordinate with latitude 92.0, outside the -90..90 range.

        The XSD types lat/lon as plain xsd:double, so it can't express a range
        constraint, and fastkml doesn't add one either -- the out-of-range
        value round-trips through untouched (only cosmetic reformatting:
        namespace prefix, and "92" gaining a decimal point).
        """
        fixture = KMLFILEDIR / "LinearRingWithInvalidLat.kml"
        expected = fixture.read_bytes()

        geom = LinearRing.from_string(fixture.read_text(encoding="utf-8"))
        actual = geom.to_string()

        assert geom.geometry is not None
        assert geom.geometry.coords[3] == (-118.0, 92.0)
        diff = xmldiff(actual, expected)
        assert diff == [
            actions.InsertNamespace(prefix=None, uri="http://www.opengis.net/kml/2.2"),
            actions.DeleteNamespace(prefix="kml"),
            actions.UpdateTextIn(
                node="/kml:LinearRing/kml:coordinates[1]",
                text="-124.0,50.0 -124.0,46.0 -118.0,46.0  -118.0,92 -124.0,50.0",
                oldtext="-124.0,50.0 -124.0,46.0 -118.0,46.0 -118.0,92.0 -124.0,50.0",
            ),
        ]
        assert fastkml.validator.validate(file_to_validate=fixture)
