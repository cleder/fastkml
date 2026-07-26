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
Round-trip the models/ Model/Alias/ResourceMap fixtures.

The remaining fixtures here (model_relative_target.kml, a real <kml> document,
is covered in document_test.py) are all bare `kml:Model` fragments, parsed via
fastkml.model.Model.from_string(). All three reference on-disk asset paths
(cube.dae/un.dae, ../../img/_01.jpg, ...) that fastkml never checks --
Alias/ResourceMap are pure data, no filesystem access -- so the "missing
asset" [ERROR] intent behind these fixtures isn't, and can't be, caught this
way.
"""

import fastkml.validator
from fastkml.model import Model
from tests.base import Lxml
from tests.ogc_conformance._helpers import KMLFILEDIR
from tests.ogc_conformance._helpers import xmldiff

MODELSDIR = KMLFILEDIR / "models"

# All three fixtures use an empty `<Location />` element; fastkml's __bool__
# convention (see docs/contributing.rst) treats content-less elements as
# falsy and omits them from serialized output -- documented, not a bug.
_EMPTY_LOCATION_DROPPED = 1


class TestLxml(Lxml):
    """Test with lxml."""

    def test_model_alias_target_missing(self) -> None:
        """[ERROR]: Alias/targetHref ("03.jpg") has no matching asset on disk."""
        fixture = MODELSDIR / "Model-AliasTargetMissing.xml"
        expected = fixture.read_bytes()

        model = Model.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(model.to_string(), expected)

        assert len(diff) == _EMPTY_LOCATION_DROPPED, diff
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_model_resource_map_invalid(self) -> None:
        """[ERROR]: one of three Aliases' sourceHref has no matching asset on disk."""
        fixture = MODELSDIR / "Model-ResourceMap-Invalid.xml"
        expected = fixture.read_bytes()

        model = Model.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(model.to_string(), expected)

        assert len(diff) == _EMPTY_LOCATION_DROPPED, diff
        assert fastkml.validator.validate(file_to_validate=fixture)

    def test_model_resource_map(self) -> None:
        """
        Single Alias, positive/minimal case in this fixture group.

        Its comment is a stale copy-paste ("[ERROR] kml:Alias with missing
        sourceHref") from the other two files in this group -- the sourceHref
        here isn't actually missing.
        """
        fixture = MODELSDIR / "Model-ResourceMap.xml"
        expected = fixture.read_bytes()

        model = Model.from_string(fixture.read_text(encoding="utf-8"))
        diff = xmldiff(model.to_string(), expected)

        assert len(diff) == _EMPTY_LOCATION_DROPPED, diff
        assert fastkml.validator.validate(file_to_validate=fixture)
