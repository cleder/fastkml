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

import pygeoif as geo
import pytest
from pygeoif.geometry import Polygon

from fastkml import containers
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
        doc = kml.KML.from_string(
            """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
          <LinearRing>
            <coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,0.0</coordinates>
          </LinearRing>
        </Placemark> </kml>""",
        )
        doc2 = kml.KML.from_string(doc.to_string())
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
        k2 = kml.KML.from_string(k.to_string(), ns="")
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
        k = kml.KML.from_string(doc)
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


class TestParseKMLNone(StdLibrary):
    def test_kml_parse(self) -> None:
        empty_placemark = KMLFILEDIR / "emptyPlacemarkWithoutId.xml"

        doc = kml.KML.parse(file=empty_placemark, ns="None")

        assert doc.ns == "None"


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""


class TestLxmlParseKML(Lxml, TestParseKML):
    """Test with Lxml."""

    def test_from_string_with_unbound_prefix_strict(self) -> None:
        doc = io.StringIO(
            '<kml xmlns="http://www.opengis.net/kml/2.2">'
            "<Placemark><ExtendedData>"
            "<lc:attachment>image.png</lc:attachment>"
            "</ExtendedData>"
            "</Placemark> </kml>",
        )

        with pytest.raises(
            AssertionError,
            match="^Element 'lc:attachment': This element is not expected.",
        ):
            kml.KML.parse(doc, ns="{http://www.opengis.net/kml/2.2}")

    def test_from_string_with_unbound_prefix_relaxed(self) -> None:
        doc = io.StringIO(
            '<kml xmlns="http://www.opengis.net/kml/2.2">'
            "<Placemark><ExtendedData>"
            "<lc:attachment>image.png</lc:attachment>"
            "</ExtendedData>"
            "</Placemark> </kml>",
        )
        k = kml.KML.parse(doc, strict=False)
        assert len(k.features) == 1
        assert isinstance(k.features[0], features.Placemark)

    def test_from_string_with_unbound_prefix_strict_no_validate(self) -> None:
        doc = io.StringIO(
            '<kml xmlns="http://www.opengis.net/kml/2.2">'
            "<Placemark><ExtendedData>"
            "<lc:attachment>image.png</lc:attachment>"
            "</ExtendedData>"
            "</Placemark> </kml>",
        )
        k = kml.KML.parse(doc, ns="{http://www.opengis.net/kml/2.2}", validate=False)
        assert len(k.features) == 1
        assert isinstance(k.features[0], features.Placemark)


class TestKmlFromString:
    def test_document(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document targetId="someTargetId">
          <name>Document.kml</name>
          <open>1</open>
          <Style id="exampleStyleDocument">
            <LabelStyle>
              <color>ff0000cc</color>
            </LabelStyle>
          </Style>
          <Placemark>
            <name>Document Feature 1</name>
            <styleUrl>#exampleStyleDocument</styleUrl>
            <Point>
              <coordinates>-122.371,37.816,0</coordinates>
            </Point>
          </Placemark>
          <Placemark targetId="someTargetId">
            <name>Document Feature 2</name>
            <styleUrl>#exampleStyleDocument</styleUrl>
            <Point>
              <coordinates>-122.370,37.817,0</coordinates>
            </Point>
          </Placemark>
        </Document>
        </kml>"""

        k = kml.KML.from_string(doc)
        assert len(k.features) == 1
        assert len(k.features[0].features) == 2
        k2 = kml.KML.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_folders(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Folder>
          <name>Folder.kml</name>
          <open>1</open>
          <description>
            A folder is a container that can hold multiple other objects
          </description>
          <Placemark>
            <name>Folder object 1 (Placemark)</name>
            <Point>
              <coordinates>-122.377588,37.830266,0</coordinates>
            </Point>
          </Placemark>
          <Placemark>
            <name>Folder object 2 (Polygon)</name>
            <Polygon>
              <outerBoundaryIs>
                <LinearRing>
                  <coordinates>
                    -122.377830,37.830445,0
                    -122.377576,37.830631,0
                    -122.377840,37.830642,0
                    -122.377830,37.830445,0
                  </coordinates>
                </LinearRing>
              </outerBoundaryIs>
            </Polygon>
          </Placemark>
          <Placemark>
            <name>Folder object 3 (Path)</name>
            <LineString>
              <tessellate>1</tessellate>
              <coordinates>
                -122.378009,37.830128,0 -122.377885,37.830379,0
              </coordinates>
            </LineString>
          </Placemark>
        </Folder>
        </kml>"""

        k = kml.KML.from_string(doc)
        assert len(k.features) == 1
        assert len(k.features[0].features) == 3
        k2 = kml.KML.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_placemark(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
          <Placemark>
            <name>Simple placemark</name>
            <description>Attached to the ground. Intelligently places itself
               at the height of the underlying terrain.</description>
            <Point>
              <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
            </Point>
          </Placemark>
        </kml>"""

        k = kml.KML.from_string(doc)
        assert len(k.features) == 1
        assert k.features[0].name == "Simple placemark"
        k2 = kml.KML.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_polygon(self) -> None:
        doc = """
        <kml xmlns="http://www.opengis.net/kml/2.2">
          <Placemark>
            <name>South Africa</name>
            <Polygon>
              <outerBoundaryIs>
                <LinearRing>
                  <coordinates>
                    31.521,-29.257,0
                    31.326,-29.402,0
                    30.902,-29.91,0
                    30.623,-30.424,0
                    30.056,-31.14,0
                    28.926,-32.172,0
                    28.22,-32.772,0
                    27.465,-33.227,0
                    26.419,-33.615,0
                    25.91,-33.667,0
                    25.781,-33.945,0
                    25.173,-33.797,0
                    24.678,-33.987,0
                    23.594,-33.794,0
                    22.988,-33.916,0
                    22.574,-33.864,0
                    21.543,-34.259,0
                    20.689,-34.417,0
                    20.071,-34.795,0
                    19.616,-34.819,0
                    19.193,-34.463,0
                    18.855,-34.444,0
                    18.425,-33.998,0
                    18.377,-34.137,0
                    18.244,-33.868,0
                    18.25,-33.281,0
                    17.925,-32.611,0
                    18.248,-32.429,0
                    18.222,-31.662,0
                    17.567,-30.726,0
                    17.064,-29.879,0
                    17.063,-29.876,0
                    16.345,-28.577,0
                    16.824,-28.082,0
                    17.219,-28.356,0
                    17.387,-28.784,0
                    17.836,-28.856,0
                    18.465,-29.045,0
                    19.002,-28.972,0
                    19.895,-28.461,0
                    19.896,-24.768,0
                    20.166,-24.918,0
                    20.759,-25.868,0
                    20.666,-26.477,0
                    20.89,-26.829,0
                    21.606,-26.727,0
                    22.106,-26.28,0
                    22.58,-25.979,0
                    22.824,-25.5,0
                    23.312,-25.269,0
                    23.734,-25.39,0
                    24.211,-25.67,0
                    25.025,-25.72,0
                    25.665,-25.487,0
                    25.766,-25.175,0
                    25.942,-24.696,0
                    26.486,-24.616,0
                    26.786,-24.241,0
                    27.119,-23.574,0
                    28.017,-22.828,0
                    29.432,-22.091,0
                    29.839,-22.102,0
                    30.323,-22.272,0
                    30.66,-22.152,0
                    31.191,-22.252,0
                    31.67,-23.659,0
                    31.931,-24.369,0
                    31.752,-25.484,0
                    31.838,-25.843,0
                    31.333,-25.66,0
                    31.044,-25.731,0
                    30.95,-26.023,0
                    30.677,-26.398,0
                    30.686,-26.744,0
                    31.283,-27.286,0
                    31.868,-27.178,0
                    32.072,-26.734,0
                    32.83,-26.742,0
                    32.58,-27.47,0
                    32.462,-28.301,0
                    32.203,-28.752,0
                    31.521,-29.257,0
                  </coordinates>
                </LinearRing>
              </outerBoundaryIs>
              <innerBoundaryIs>
                <LinearRing>
                  <coordinates>
                    28.978,-28.956,0
                    28.542,-28.648,0
                    28.074,-28.851,0
                    27.533,-29.243,0
                    26.999,-29.876,0
                    27.749,-30.645,0
                    28.107,-30.546,0
                    28.291,-30.226,0
                    28.848,-30.07,0
                    29.018,-29.744,0
                    29.325,-29.257,0
                    28.978,-28.956,0
                  </coordinates>
                </LinearRing>
              </innerBoundaryIs>
            </Polygon>
          </Placemark>
        </kml>"""

        k = kml.KML.from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].geometry, Polygon)
        k2 = kml.KML.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_multipoints(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark id="feat_2">
            <name>MultiPoint</name>
            <styleUrl>#stylesel_9</styleUrl>
            <MultiGeometry id="geom_0">
                <Point id="geom_5">
                    <coordinates>16,-35,0.0</coordinates>
                </Point>
                <Point id="geom_6">
                    <coordinates>16,-33,0.0</coordinates>
                </Point>
                <Point id="geom_7">
                    <coordinates>16,-31,0.0</coordinates>
                </Point>
                <Point id="geom_8">
                    <coordinates>16,-29,0.0</coordinates>
                </Point>
                <Point id="geom_9">
                    <coordinates>16,-27,0.0</coordinates>
                </Point>
                <Point id="geom_10">
                    <coordinates>16,-25,0.0</coordinates>
                </Point>
                <Point id="geom_11">
                    <coordinates>16,-23,0.0</coordinates>
                </Point>
                <Point id="geom_12">
                    <coordinates>16,-21,0.0</coordinates>
                </Point>
                <Point id="geom_15">
                    <coordinates>18,-35,0.0</coordinates>
                </Point>
                <Point id="geom_16">
                    <coordinates>18,-33,0.0</coordinates>
                </Point>
                <Point id="geom_17">
                    <coordinates>18,-31,0.0</coordinates>
                </Point>
                <Point id="geom_18">
                    <coordinates>18,-29,0.0</coordinates>
                </Point>
            </MultiGeometry>
        </Placemark></kml>"""

        k = kml.KML.from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].geometry, geo.MultiPoint)
        assert len(list(k.features[0].geometry.geoms)) == 12
        k2 = kml.KML.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_snippet(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
        <Snippet maxLines="2" >Short Desc</Snippet>
        </Placemark> </kml>"""

        k = kml.KML.from_string(doc)
        assert k.features[0].snippet.text == "Short Desc"
        assert k.features[0].snippet.max_lines == 2
        k.features[0].snippet = features.Snippet(
            text="Another Snippet",
            max_lines=3,
        )
        assert 'maxLines="3"' in k.to_string()
        k.features[0].snippet = features.Snippet(text="Another Snippet")
        assert "maxLines" not in k.to_string()
        assert "Another Snippet" in k.to_string()
        k.features[0].snippet = features.Snippet(text="Different Snippet")
        assert "maxLines" not in k.to_string()
        assert "Different Snippet" in k.to_string()
        k.features[0].snippet = features.Snippet(text="", max_lines=4)
        assert "Snippet" not in k.to_string()

    def test_address(self) -> None:
        doc = Document.from_string(
            """
        <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2" id="pm-id">
            <kml:name>pm-name</kml:name>
            <kml:description>pm-description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:address>1600 Amphitheatre Parkway,...</kml:address>
        </kml:Document>
        """,
        )

        doc2 = Document.from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()

    def test_phone_number(self) -> None:
        doc = Document.from_string(
            """
        <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2" id="pm-id">
            <kml:name>pm-name</kml:name>
            <kml:description>pm-description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:phoneNumber>+1 234 567 8901</kml:phoneNumber>
        </kml:Document>
        """,
        )

        doc2 = Document.from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()

    def test_groundoverlay(self) -> None:
        doc = kml.KML.from_string(
            """
            <kml xmlns="http://www.opengis.net/kml/2.2">
              <Folder>
                <name>Ground Overlays</name>
                <description>Examples of ground overlays</description>
                <GroundOverlay>
                  <name>Large-scale overlay on terrain</name>
                  <description>Overlay shows Mount Etna erupting
                      on July 13th, 2001.</description>
                  <Icon>
                    <href>http://developers.google.com/kml/etna.jpg</href>
                  </Icon>
                  <LatLonBox>
                    <north>37.91904192681665</north>
                    <south>37.46543388598137</south>
                    <east>15.35832653742206</east>
                    <west>14.60128369746704</west>
                    <rotation>-0.1556640799496235</rotation>
                  </LatLonBox>
                </GroundOverlay>
              </Folder>
            </kml>
            """,
        )

        doc2 = kml.KML.from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()
