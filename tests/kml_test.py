# Copyright (C) 2022 -2024  Christian Ledermann
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

"""Test the kml class."""
import io
import pathlib
from unittest.mock import patch

import pygeoif as geo
import pytest

from fastkml import containers
from fastkml import config
from fastkml import features
from fastkml import kml
from fastkml.containers import Document
from fastkml.features import Placemark
from tests.base import Lxml
from tests.base import StdLibrary

BASEDIR = pathlib.Path(__file__).parent
KMLFILEDIR = BASEDIR / "ogc_conformance" / "data" / "kml"


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_linarring_placemark(self) -> None:
        doc = kml.KML.class_from_string(
            """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
          <LinearRing>
            <coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,0.0</coordinates>
          </LinearRing>
        </Placemark> </kml>""",
        )
        doc2 = kml.KML.class_from_string(doc.to_string())
        assert isinstance(doc.features[0].geometry, geo.LinearRing)
        assert doc.to_string() == doc2.to_string()

    def test_kml(self) -> None:
        """Kml file without contents."""
        k = kml.KML(ns="")
        assert k.features == []
        assert (
            k.to_string().strip().replace(" ", "")
            == '<kmlxmlns="http://www.opengis.net/kml/2.2"/>'
        )
        k2 = kml.KML.class_from_string(k.to_string(), ns="")
        assert k.to_string() == k2.to_string()

    def test_kml_with_document(self) -> None:
        """Kml file with document/folder/placemark/polygon."""
        doc = (
            '<kml xmlns="http://www.opengis.net/kml/2.2">'
            '<Document id="root_doc">'
            "<Folder><name>test</name>"
            "<Placemark>"
            "<Polygon>"
            "<outerBoundaryIs>"
            "<LinearRing><coordinates>"
            "-93.7426720226024,57.4519411370713 -93.6051809086549,49.4316261567984 "
            "-80.8643376828499,49.5232868994301 -81.2309806533767,57.4519411370713 "
            "-81.2309806533767,57.4519411370713 -93.7426720226024,57.4519411370713"
            "</coordinates></LinearRing>"
            "</outerBoundaryIs>"
            "<innerBoundaryIs>"
            "<LinearRing><coordinates>"
            "-91.8663227028478,56.050879726904 -91.7704563496718,53.9897531336206 "
            "-90.1407283456804,54.0856194867966 -90.0927951690924,56.002946550316 "
            "-91.8663227028478,56.050879726904"
            "</coordinates></LinearRing>"
            "</innerBoundaryIs>"
            "<innerBoundaryIs>"
            "<LinearRing><coordinates>"
            "-85.4912102166459,55.90708019714 -85.4912102166459,54.0376863102086 "
            "-83.8135490360665,54.0856194867966 -83.9094153892425,55.90708019714 "
            "-85.4912102166459,55.90708019714</coordinates></LinearRing>"
            "</innerBoundaryIs>"
            "</Polygon>"
            "</Placemark>"
            "</Folder>"
            "</Document></kml>"
        )
        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0], Document)
        assert len(k.features[0].features) == 1
        assert isinstance(k.features[0].features[0], containers.Folder)
        assert len(k.features[0].features[0].features) == 1
        assert isinstance(k.features[0].features[0].features[0], features.Placemark)
        assert isinstance(k.features[0].features[0].features[0].geometry, geo.Polygon)
        assert len(list(k.features[0].features[0].features[0].geometry.interiors)) == 2


class TestParseKML(StdLibrary):
    def test_parse_kml(self) -> None:
        empty_placemark = KMLFILEDIR / "emptyPlacemarkWithoutId.xml"

        doc = kml.KML.parse(empty_placemark)

        assert doc == kml.KML(
            ns="{http://www.opengis.net/kml/2.2}",
            features=[
                Document(
                    ns="{http://www.opengis.net/kml/2.2}",
                    id="doc-001",
                    target_id="",
                    name="Vestibulum eleifend lobortis lorem.",
                    features=[
                        Placemark(
                            ns="{http://www.opengis.net/kml/2.2}",
                        ),
                    ],
                    schemata=[],
                ),
            ],
        )

    def test_parse_kml_filename(self) -> None:
        empty_placemark = str(KMLFILEDIR / "emptyPlacemarkWithoutId.xml")

        doc = kml.KML.parse(empty_placemark)

        assert doc == kml.KML(
            ns="{http://www.opengis.net/kml/2.2}",
            features=[
                Document(
                    ns="{http://www.opengis.net/kml/2.2}",
                    id="doc-001",
                    target_id="",
                    name="Vestibulum eleifend lobortis lorem.",
                    features=[
                        Placemark(
                            ns="{http://www.opengis.net/kml/2.2}",
                        ),
                    ],
                    schemata=[],
                ),
            ],
        )

    def test_parse_kml_fileobject(self) -> None:
        empty_placemark = KMLFILEDIR / "emptyPlacemarkWithoutId.xml"
        with empty_placemark.open() as f:
            doc = kml.KML.parse(f)

        assert doc == kml.KML(
            ns="{http://www.opengis.net/kml/2.2}",
            features=[
                Document(
                    ns="{http://www.opengis.net/kml/2.2}",
                    id="doc-001",
                    target_id="",
                    name="Vestibulum eleifend lobortis lorem.",
                    features=[
                        Placemark(
                            ns="{http://www.opengis.net/kml/2.2}",
                        ),
                    ],
                    schemata=[],
                ),
            ],
        )
    
    @patch('fastkml.config.etree')
    def test_kml_etree_element(self, mock_etree) -> None:

        mock_etree.__all__ = ['LXML_VERSION']
        empty_placemark = KMLFILEDIR / "emptyPlacemarkWithoutId.xml"

        doc = kml.KML.parse(empty_placemark)

        assert doc.etree_element() == config.etree.Element( f"{doc.ns}{doc.get_tag_name()}", nsmap={None: doc.ns[1:-1]},)

    def test_kml_append(self) -> None:
        empty_placemark = KMLFILEDIR / "emptyPlacemarkWithoutId.xml"

        doc = kml.KML.parse(empty_placemark)

        with pytest.raises(ValueError):
            doc.append(doc)

class TestParseKMLNone(StdLibrary):
    def test_kml_parse(self) -> None:
        empty_placemark = KMLFILEDIR / "emptyPlacemarkWithoutId.xml"

        doc = kml.KML.parse(file=empty_placemark, ns="None")

        assert doc.ns == "None"

class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""


class TestLxmlParseKML(Lxml, TestParseKML):
    """Test with Lxml."""

    def test_from_string_with_unbound_prefix(self) -> None:
        doc = io.StringIO(
            '<kml xmlns="http://www.opengis.net/kml/2.2">'
            "<Placemark><ExtendedData>"
            "<lc:attachment>image.png</lc:attachment>"
            "</ExtendedData>"
            "</Placemark> </kml>",
        )
        k = kml.KML.parse(doc, ns="{http://www.opengis.net/kml/2.2}")
        assert len(k.features) == 1
        assert isinstance(k.features[0], features.Placemark)
