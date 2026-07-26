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
Round-trip the views/ LookAt fixtures.

All 5 fixtures (including the nominally-good "-Ok" one) fail identically at
default fastkml.kml.KML.parse() settings: their element order
(longitude, latitude, [altitude], range, tilt, heading, [altitudeMode]) does
not match the order fastkml's bundled ogckml22.xsd requires for LookAtType
(longitude, latitude, altitude, heading, tilt, range, altitudeModeGroup) --
confirmed independently against raw lxml.etree.XMLSchema, so this is a
fixture/XSD-order mismatch, not a fastkml bug. Because every fixture fails
the same way, there is no pass/fail distinction to test here for the
altitude/altitudeMode semantics each is nominally about; each test below
asserts today's actual, uniform failure, with a comment on what the fixture
was *meant* to probe.
"""

import pytest

import fastkml.kml
import fastkml.validator
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR

VIEWSDIR = KMLFILEDIR / "views"

_ELEMENT_ORDER_ERROR = "Element '{http://www.opengis.net/kml/2.2}tilt'"


class TestLxml(Lxml):
    """Test with lxml."""

    def test_look_at_clamp_to_ground(self) -> None:
        """Meant to test altitudeMode=clampToGround with tilt/heading/range set."""
        fixture = VIEWSDIR / "LookAt-ClampToGround.xml"

        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.kml.KML.parse(fixture)
        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.validator.validate(file_to_validate=fixture)

    def test_look_at_error(self) -> None:
        """[ERROR]: altitudeMode=absolute but altitude is missing."""
        fixture = VIEWSDIR / "LookAt-Error.xml"

        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.kml.KML.parse(fixture)
        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.validator.validate(file_to_validate=fixture)

    def test_look_at_missing_altitude_mode_and_altitude(self) -> None:
        """Meant to test that omitting both altitude and altitudeMode is legal."""
        fixture = VIEWSDIR / "LookAt-MissingAltitudeModeAndAltitude.xml"

        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.kml.KML.parse(fixture)
        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.validator.validate(file_to_validate=fixture)

    def test_look_at_missing_altitude_mode(self) -> None:
        """Meant to test altitude set without an explicit altitudeMode."""
        fixture = VIEWSDIR / "LookAt-MissingAltitudeMode.xml"

        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.kml.KML.parse(fixture)
        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.validator.validate(file_to_validate=fixture)

    def test_look_at_ok(self) -> None:
        """The nominal known-good case: altitude and altitudeMode both set."""
        fixture = VIEWSDIR / "LookAt-Ok.xml"

        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.kml.KML.parse(fixture)
        with pytest.raises(AssertionError, match=_ELEMENT_ORDER_ERROR):
            fastkml.validator.validate(file_to_validate=fixture)
