# Copyright (C) 2012 -2022 Christian Ledermann
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
import xml.etree.ElementTree

import pytest
from pygeoif.geometry import LinearRing
from pygeoif.geometry import MultiPoint
from pygeoif.geometry import Polygon

from fastkml import atom
from fastkml import base
from fastkml import config
from fastkml import kml
from fastkml import styles
from fastkml.enums import AltitudeMode
from fastkml.enums import ColorMode
from fastkml.enums import DisplayMode

try:
    import lxml

    LXML = True
except ImportError:
    LXML = False


class TestBaseClasses:
    """
    BaseClasses  must raise a NotImplementedError on etree_element
    and a TypeError on from_element.
    """

    def setup_method(self) -> None:
        """Always test with the same parser."""
        config.set_etree_implementation(xml.etree.ElementTree)
        config.set_default_namespaces()

    def test_base_object(self) -> None:
        bo = base._BaseObject(id="id0")
        assert bo.id == "id0"
        assert bo.ns == config.KMLNS
        assert bo.target_id is None
        assert bo.__name__ == ""
        bo.target_id = "target"
        assert bo.target_id == "target"
        bo.ns = ""
        bo.id = None
        assert bo.id is None
        assert not bo.ns
        pytest.raises(NotImplementedError, bo.etree_element)
        element = config.etree.Element(f"{config.KMLNS}Base")
        pytest.raises(TypeError, bo.from_element)
        pytest.raises(TypeError, bo.from_element, element)
        bo.__name__ = "NotABaseObject"
        pytest.raises(TypeError, bo.from_element, element)
        # Note that we can coax baseclasses not to throw errors
        bo.__name__ = "Base"
        bo.ns = config.KMLNS
        bo.from_element(element)
        assert bo.id is None
        assert bo.ns == config.KMLNS
        assert bo.etree_element() is not None
        assert len(bo.to_string()) > 1

    def test_feature(self) -> None:
        f = kml._Feature(name="A Feature")
        pytest.raises(NotImplementedError, f.etree_element)
        assert f.name == "A Feature"
        assert f.visibility == 1
        assert f.isopen == 0
        assert f._atom_author is None
        assert f._atom_link is None
        assert f.address is None
        # self.assertEqual(f.phoneNumber, None)
        assert f._snippet is None
        assert f.description is None
        assert f._style_url is None
        assert f._styles == []
        assert f._timespan is None
        assert f._timestamp is None
        # self.assertEqual(f.region, None)
        # self.assertEqual(f.extended_data, None)

        f.__name__ = "Feature"
        f.style_url = "#default"
        assert "Feature>" in str(f.to_string())
        assert "#default" in str(f.to_string())

    def test_container(self) -> None:
        f = kml._Container(name="A Container")
        # apparently you can add documents to containes
        # d = kml.Document()
        # self.assertRaises(TypeError, f.append, d)
        p = kml.Placemark()
        f.append(p)
        pytest.raises(NotImplementedError, f.etree_element)

    def test_overlay(self) -> None:
        o = kml._Overlay(name="An Overlay")
        assert o._color is None
        assert o._draw_order is None
        assert o._icon is None
        pytest.raises(NotImplementedError, o.etree_element)


class TestBuildKml:
    """Build a simple KML File."""

    def setup_method(self) -> None:
        """Always test with the same parser."""
        config.set_etree_implementation(xml.etree.ElementTree)
        config.set_default_namespaces()

    def test_kml(self) -> None:
        """Kml file without contents."""
        k = kml.KML()
        assert not list(k.features())
        assert (
            str(k.to_string())[:51]
            == '<kml:kml xmlns:kml="http://www.opengis.net/kml/2.2" />'[:51]
        )
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_folder(self) -> None:
        """KML file with folders."""
        ns = "{http://www.opengis.net/kml/2.2}"
        k = kml.KML()
        f = kml.Folder(ns, "id", "name", "description")
        nf = kml.Folder(ns, "nested-id", "nested-name", "nested-description")
        f.append(nf)
        k.append(f)
        f2 = kml.Folder(ns, "id2", "name2", "description2")
        k.append(f2)
        assert len(list(k.features())) == 2
        assert len(list(next(iter(k.features())).features())) == 1
        k2 = kml.KML()
        s = k.to_string()
        k2.from_string(s)
        assert s == k2.to_string()

    def test_placemark(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        k = kml.KML(ns=ns)
        p = kml.Placemark(ns, "id", "name", "description")
        # XXX p.geometry = Point(0.0, 0.0, 0.0)
        p2 = kml.Placemark(ns, "id2", "name2", "description2")
        # XXX p2.geometry = LineString([(0, 0, 0), (1, 1, 1)])
        k.append(p)
        k.append(p2)
        assert len(list(k.features())) == 2
        k2 = kml.KML()
        k2.from_string(k.to_string(prettyprint=True))
        assert k.to_string() == k2.to_string()

    def test_document(self) -> None:
        k = kml.KML()
        ns = "{http://www.opengis.net/kml/2.2}"
        d = kml.Document(ns, "docid", "doc name", "doc description")
        f = kml.Folder(ns, "fid", "f name", "f description")
        k.append(d)
        d.append(f)
        nf = kml.Folder(ns, "nested-fid", "nested f name", "nested f description")
        f.append(nf)
        f2 = kml.Folder(ns, "id2", "name2", "description2")
        d.append(f2)
        p = kml.Placemark(ns, "id", "name", "description")
        # XXX p.geometry = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
        p2 = kml.Placemark(ns, "id2", "name2", "description2")
        # p2 does not have a geometry!
        f2.append(p)
        nf.append(p2)
        assert len(list(k.features())) == 1
        assert len(list(next(iter(k.features())).features())) == 2
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_author(self) -> None:
        d = kml.Document()
        d.author = "Christian Ledermann"
        assert "Christian Ledermann" in str(d.to_string())
        a = atom.Author(
            ns="{http://www.w3.org/2005/Atom}",
            name="Nobody",
            uri="http://localhost",
            email="cl@donotreply.com",
        )
        d.author = a
        assert d.author == "Nobody"
        assert "Christian Ledermann" not in str(d.to_string())
        assert "Nobody" in str(d.to_string())
        assert "http://localhost" in str(d.to_string())
        assert "cl@donotreply.com" in str(d.to_string())
        d2 = kml.Document()
        d2.from_string(d.to_string())
        assert d.to_string() == d2.to_string()
        d.author = None

    def test_link(self) -> None:
        d = kml.Document()
        d.link = "http://localhost"
        assert "http://localhost" in str(d.to_string())
        d.link = atom.Link(ns=config.ATOMNS, href="#here")
        assert "#here" in str(d.to_string())
        # pytest.raises(TypeError, d.link, object)
        d2 = kml.Document()
        d2.from_string(d.to_string())
        assert d.to_string() == d2.to_string()
        d.link = None

    def test_address(self) -> None:
        address = "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA"
        d = kml.Document()
        d.address = address
        assert address in str(d.to_string())
        assert "address>" in str(d.to_string())

    def test_phone_number(self) -> None:
        phone = "+1 234 567 8901"
        d = kml.Document()
        d.phone_number = phone
        assert phone in str(d.to_string())
        assert "phoneNumber>" in str(d.to_string())


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

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert len(list(next(iter(k.features())).features())) == 2
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_document_booleans(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document targetId="someTargetId">
          <name>Document.kml</name>
          <visibility>true</visibility>
          <open>1</open>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert next(iter(k.features())).visibility == 1
        assert next(iter(k.features())).isopen == 1
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document targetId="someTargetId">
          <name>Document.kml</name>
          <visibility>0</visibility>
          <open>false</open>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert next(iter(k.features())).visibility == 0
        assert next(iter(k.features())).isopen == 0

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

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert len(list(next(iter(k.features())).features())) == 3
        k2 = kml.KML()
        k2.from_string(k.to_string())
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

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert next(iter(k.features())).name == "Simple placemark"
        k2 = kml.KML()
        k2.from_string(k.to_string())
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

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(k.features())).geometry, Polygon)
        k2 = kml.KML()
        k2.from_string(k.to_string())
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

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(k.features())).geometry, MultiPoint)
        assert len(list(next(iter(k.features())).geometry.geoms)) == 12
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_atom(self) -> None:
        pass

    def test_snippet(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
        <Snippet maxLines="2" >Short Desc</Snippet>
        </Placemark> </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert next(iter(k.features())).snippet["text"] == "Short Desc"
        assert next(iter(k.features())).snippet["maxLines"] == 2
        next(iter(k.features()))._snippet["maxLines"] = 3
        assert next(iter(k.features())).snippet["maxLines"] == 3
        assert 'maxLines="3"' in k.to_string()
        next(iter(k.features())).snippet = {"text": "Annother Snippet"}
        assert "maxLines" not in k.to_string()
        assert "Annother Snippet" in k.to_string()
        next(iter(k.features())).snippet = "Diffrent Snippet"
        assert "maxLines" not in k.to_string()
        assert "Diffrent Snippet" in k.to_string()

    def test_from_wrong_string(self) -> None:
        doc = kml.KML()
        pytest.raises(TypeError, doc.from_string, "<xml></xml>")

    def test_from_string_with_unbound_prefix(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
        <ExtendedData>
          <lc:attachment>image.png</lc:attachment>
        </ExtendedData>
        </Placemark> </kml>"""
        if LXML:
            config.set_etree_implementation(lxml.etree)
            k = kml.KML()
            k.from_string(doc)
            assert len(list(k.features())) == 1
        config.set_etree_implementation(xml.etree.ElementTree)
        k = kml.KML()
        pytest.raises(xml.etree.ElementTree.ParseError, k.from_string, doc)

    def test_address(self) -> None:
        doc = kml.Document()

        doc.from_string(
            """
        <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2" id="pm-id">
            <kml:name>pm-name</kml:name>
            <kml:description>pm-description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:address>1600 Amphitheatre Parkway,...</kml:address>
        </kml:Document>
        """,
        )

        doc2 = kml.Document()
        doc2.from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()

    def test_phone_number(self) -> None:
        doc = kml.Document()

        doc.from_string(
            """
        <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2" id="pm-id">
            <kml:name>pm-name</kml:name>
            <kml:description>pm-description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:phoneNumber>+1 234 567 8901</kml:phoneNumber>
        </kml:Document>
        """,
        )

        doc2 = kml.Document()
        doc2.from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()

    def test_groundoverlay(self) -> None:
        doc = kml.KML()

        doc.from_string(
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

        doc2 = kml.KML()
        doc2.from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()

    def test_linarring_placemark(self) -> None:
        doc = kml.KML()
        doc.from_string(
            """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
          <LinearRing>
            <coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,0.0</coordinates>
          </LinearRing>
        </Placemark> </kml>""",
        )
        doc2 = kml.KML()
        doc2.from_string(doc.to_string())
        assert isinstance(next(iter(doc.features())).geometry, LinearRing)
        assert doc.to_string() == doc2.to_string()


class TestStyle:
    def test_styleurl(self) -> None:
        f = kml.Document()
        f.style_url = "#somestyle"
        assert f.style_url == "#somestyle"
        assert isinstance(f._style_url, styles.StyleUrl)
        s = styles.StyleUrl(config.KMLNS, url="#otherstyle")
        f.style_url = s
        assert isinstance(f._style_url, styles.StyleUrl)
        assert f.style_url == "#otherstyle"
        f2 = kml.Document()
        f2.from_string(f.to_string())
        assert f.to_string() == f2.to_string()

    def test_style(self) -> None:
        lstyle = styles.LineStyle(color="red", width=2.0)
        style = styles.Style(styles=[lstyle])
        f = kml.Document(styles=[style])
        f2 = kml.Document()
        f2.from_string(f.to_string(prettyprint=True))
        assert f.to_string() == f2.to_string()

    def test_polystyle_fill(self) -> None:
        styles.PolyStyle()

    def test_polystyle_outline(self) -> None:
        styles.PolyStyle()


class TestStyleUsage:
    def test_create_document_style(self) -> None:
        style = styles.Style(styles=[styles.PolyStyle(color="7f000000")])

        doc = kml.Document(styles=[style])

        doc2 = kml.Document()
        doc2.append_style(style)

        expected = """
            <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2">
              <kml:visibility>1</kml:visibility>
                <kml:Style>
                  <kml:PolyStyle>
                    <kml:color>7f000000</kml:color>
                    <kml:fill>1</kml:fill>
                    <kml:outline>1</kml:outline>
                  </kml:PolyStyle>
                </kml:Style>
            </kml:Document>
        """

        doc3 = kml.Document()
        doc3.from_string(expected)

        assert doc.to_string() == doc2.to_string()
        assert doc2.to_string() == doc3.to_string()
        assert doc.to_string() == doc3.to_string()

    def test_create_placemark_style(self) -> None:
        style = styles.Style(styles=[styles.PolyStyle(color="7f000000")])

        place = kml.Placemark(styles=[style])

        place2 = kml.Placemark()
        place2.append_style(style)

        expected = """
            <kml:Placemark xmlns:kml="http://www.opengis.net/kml/2.2">
              <kml:visibility>1</kml:visibility>
                <kml:Style>
                  <kml:PolyStyle>
                    <kml:color>7f000000</kml:color>
                    <kml:fill>1</kml:fill>
                    <kml:outline>1</kml:outline>
                  </kml:PolyStyle>
                </kml:Style>
            </kml:Placemark>
        """

        place3 = kml.Placemark()
        place3.from_string(expected)
        assert place.to_string() == place2.to_string()
        assert place2.to_string() == place3.to_string()
        assert place.to_string() == place3.to_string()


class TestStyleFromString:
    def test_styleurl(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>Document.kml</name>
          <open>1</open>
          <styleUrl>#default</styleUrl>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert next(iter(k.features())).style_url == "#default"
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_balloonstyle(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>Document.kml</name>
          <Style id="exampleBalloonStyle">
            <BalloonStyle>
              <!-- a background color for the balloon -->
              <bgColor>ffffffbb</bgColor>
              <!-- styling of the balloon text -->
              <textColor>ff000000</textColor>
              <text><![CDATA[
              <b><font color="#CC0000" size="+3">$[name]</font></b>
              <br/><br/>
              <font face="Courier">$[description]</font>
              <br/><br/>
              Extra text that will appear in the description balloon
              <br/><br/>
              <!-- insert the to/from hyperlinks -->
              $[geDirections]
              ]]></text>
              <!-- kml:displayModeEnum -->
              <displayMode>default</displayMode>
            </BalloonStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(next(iter(k.features())).styles())), styles.Style)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.BalloonStyle)
        assert style.bg_color == "ffffffbb"
        assert style.text_color == "ff000000"
        assert style.display_mode == DisplayMode.default
        assert "$[geDirections]" in style.text
        assert "$[description]" in style.text
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k2.to_string() == k.to_string()

    def test_balloonstyle_old_color(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>Document.kml</name>
          <Style id="exampleBalloonStyle">
            <BalloonStyle>
              <!-- a background color for the balloon -->
              <color>ffffffbb</color>
            </BalloonStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(next(iter(k.features())).styles())), styles.Style)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.BalloonStyle)
        assert style.bg_color == "ffffffbb"
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k2.to_string() == k.to_string()

    def test_labelstyle(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>Document.kml</name>
          <open>1</open>
          <Style id="exampleStyleDocument">
            <LabelStyle>
              <color>ff0000cc</color>
            </LabelStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(next(iter(k.features())).styles())), styles.Style)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.LabelStyle)
        assert style.color == "ff0000cc"
        assert style.color_mode is None
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_iconstyle(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
           <Style id="randomColorIcon">
              <IconStyle>
                 <color>ff00ff00</color>
                 <colorMode>random</colorMode>
                 <scale>1.1</scale>
                 <heading>0</heading>
                 <Icon>
                    <href>http://maps.google.com/icon21.png</href>
                 </Icon>
              </IconStyle>
           </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(next(iter(k.features())).styles())), styles.Style)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.IconStyle)
        assert style.color == "ff00ff00"
        assert style.scale == 1.1
        assert style.color_mode == ColorMode.random
        assert style.heading == 0.0
        assert style.icon_href == "http://maps.google.com/icon21.png"
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_linestyle(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>LineStyle.kml</name>
          <open>1</open>
          <Style id="linestyleExample">
            <LineStyle>
              <color>7f0000ff</color>
              <width>4</width>
            </LineStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(next(iter(k.features())).styles())), styles.Style)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.LineStyle)
        assert style.color == "7f0000ff"
        assert style.width == 4
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_polystyle(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>PolygonStyle.kml</name>
          <open>1</open>
          <Style id="examplePolyStyle">
            <PolyStyle>
              <color>ff0000cc</color>
              <colorMode>random</colorMode>
            </PolyStyle>
          </Style>
        </Document>
        </kml>"""

        # XXX fill and outline
        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(next(iter(k.features())).styles())), styles.Style)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.PolyStyle)
        assert style.color == "ff0000cc"
        assert style.color_mode == ColorMode.random
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_polystyle_boolean_fill(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>PolygonStyle.kml</name>
          <open>1</open>
          <Style id="examplePolyStyle">
            <PolyStyle>
              <fill>false</fill>
            </PolyStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.PolyStyle)
        assert style.fill == 0
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_polystyle_boolean_outline(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>PolygonStyle.kml</name>
          <open>1</open>
          <Style id="examplePolyStyle">
            <PolyStyle>
              <outline>false</outline>
            </PolyStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.PolyStyle)
        assert style.outline == 0
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_polystyle_float_fill(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>PolygonStyle.kml</name>
          <open>1</open>
          <Style id="examplePolyStyle">
            <PolyStyle>
              <fill>0.0</fill>
            </PolyStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.PolyStyle)
        assert style.fill == 0
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_polystyle_float_outline(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>PolygonStyle.kml</name>
          <open>1</open>
          <Style id="examplePolyStyle">
            <PolyStyle>
              <outline>0.0</outline>
            </PolyStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        style = next(iter(next(iter(next(iter(k.features())).styles())).styles()))
        assert isinstance(style, styles.PolyStyle)
        assert style.outline == 0
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_styles(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <!-- Begin Style Definitions -->
          <Style id="myDefaultStyles">
            <IconStyle>
              <color>a1ff00ff</color>
              <scale>1.399999976158142</scale>
              <Icon>
                <href>http://myserver.com/icon.jpg</href>
              </Icon>
            </IconStyle>
            <LabelStyle>
              <color>7fffaaff</color>
              <scale>1.5</scale>
            </LabelStyle>
            <LineStyle>
              <color>ff0000ff</color>
              <width>15</width>
            </LineStyle>
            <PolyStyle>
              <color>7f7faaaa</color>
              <colorMode>random</colorMode>
            </PolyStyle>
          </Style>
          <!-- End Style Definitions -->
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(next(iter(next(iter(k.features())).styles())), styles.Style)
        style = list(next(iter(next(iter(k.features())).styles())).styles())
        assert len(style) == 4
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_stylemapurl(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <StyleMap id="styleMapExample">
            <Pair>
              <key>normal</key>
              <styleUrl>#normalState</styleUrl>
            </Pair>
            <Pair>
              <key>highlight</key>
              <styleUrl>#highlightState</styleUrl>
            </Pair>
          </StyleMap>
          </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(
            next(iter(next(iter(k.features())).styles())),
            styles.StyleMap,
        )
        sm = next(iter(next(iter(k.features())).styles()))
        assert isinstance(sm.normal, styles.StyleUrl)
        assert sm.normal.url == "#normalState"
        assert isinstance(sm.highlight, styles.StyleUrl)
        assert sm.highlight.url == "#highlightState"
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_stylemapstyles(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <StyleMap id="styleMapExample">
            <Pair>
              <key>normal</key>
              <Style id="exampleStyleDocument">
                <LabelStyle>
                  <color>ff0000cc</color>
                </LabelStyle>
              </Style>
            </Pair>
            <Pair>
              <key>highlight</key>
              <Style id="examplePolyStyle">
                <PolyStyle>
                  <color>ff0000cc</color>
                  <colorMode>random</colorMode>
                </PolyStyle>
                <LineStyle>
                  <color>ff0000ff</color>
                  <width>15</width>
                </LineStyle>
              </Style>
            </Pair>
          </StyleMap>
          </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        assert isinstance(
            next(iter(next(iter(k.features())).styles())),
            styles.StyleMap,
        )
        sm = next(iter(next(iter(k.features())).styles()))
        assert isinstance(sm.normal, styles.Style)
        assert len(list(sm.normal.styles())) == 1
        assert isinstance(next(iter(sm.normal.styles())), styles.LabelStyle)
        assert isinstance(sm.highlight, styles.Style)
        assert isinstance(sm.highlight, styles.Style)
        assert len(list(sm.highlight.styles())) == 2
        assert isinstance(next(iter(sm.highlight.styles())), styles.LineStyle)
        assert isinstance(list(sm.highlight.styles())[1], styles.PolyStyle)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_get_style_by_url(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>Document.kml</name>
          <open>1</open>
          <Style id="exampleStyleDocument">
            <LabelStyle>
              <color>ff0000cc</color>
            </LabelStyle>
          </Style>
          <StyleMap id="styleMapExample">
            <Pair>
              <key>normal</key>
              <styleUrl>#normalState</styleUrl>
            </Pair>
            <Pair>
              <key>highlight</key>
              <styleUrl>#highlightState</styleUrl>
            </Pair>
          </StyleMap>
          <Style id="linestyleExample">
            <LineStyle>
              <color>7f0000ff</color>
              <width>4</width>
            </LineStyle>
          </Style>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        assert len(list(k.features())) == 1
        document = next(iter(k.features()))
        style = document.get_style_by_url(
            "http://localhost:8080/somepath#exampleStyleDocument",
        )
        assert isinstance(next(iter(style.styles())), styles.LabelStyle)
        style = document.get_style_by_url("somepath#linestyleExample")
        assert isinstance(next(iter(style.styles())), styles.LineStyle)
        style = document.get_style_by_url("#styleMapExample")
        assert isinstance(style, styles.StyleMap)


def test_nested_multigeometry() -> None:
    doc = """<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark>
          <MultiGeometry>
            <Polygon>
              <outerBoundaryIs>
                <LinearRing>
                  <coordinates>
                    -122.366278,37.818844,0 -122.365248,37.819267,0 -122.365640,37.819875,0 -122.366278,37.818844,0
                  </coordinates>
                </LinearRing>
              </outerBoundaryIs>
            </Polygon>
            <Point>
              <coordinates>-122.365,37.819,0</coordinates>
            </Point>
            <MultiGeometry>
              <LineString>
                <coordinates>
                  -122.365278,37.819000,0 -122.365248,37.819267,0
                </coordinates>
              </LineString>
              <Polygon>
                <outerBoundaryIs>
                  <LinearRing>
                    <coordinates>
                      -122.365248,37.819267,0 -122.365640,37.819875,0 -122.366278,37.818844,0 -122.365248,37.819267,0
                    </coordinates>
                  </LinearRing>
                </outerBoundaryIs>
              </Polygon>
            </MultiGeometry>
          </MultiGeometry>
        </Placemark></Document></kml>
        """

    k = kml.KML()
    k.from_string(doc)
    placemark = next(iter(next(iter(k.features())).features()))

    first_multigeometry = placemark.geometry
    assert len(list(first_multigeometry.geoms)) == 3

    second_multigeometry = next(
        g for g in first_multigeometry.geoms if g.geom_type == "GeometryCollection"
    )
    assert len(list(second_multigeometry.geoms)) == 2


class TestGetGeometry:
    def test_nested_multigeometry(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark>
          <MultiGeometry>
            <Polygon>
              <outerBoundaryIs>
                <LinearRing>
                  <coordinates>
                    -122.366278,37.818844,0 -122.365248,37.819267,0 -122.365640,37.819875,0 -122.366278,37.818844,0
                  </coordinates>
                </LinearRing>
              </outerBoundaryIs>
            </Polygon>
            <Point>
              <coordinates>-122.365,37.819,0</coordinates>
            </Point>
            <MultiGeometry>
              <LineString>
                <coordinates>
                  -122.365278,37.819000,0 -122.365248,37.819267,0
                </coordinates>
              </LineString>
              <Polygon>
                <outerBoundaryIs>
                  <LinearRing>
                    <coordinates>
                      -122.365248,37.819267,0 -122.365640,37.819875,0 -122.366278,37.818844,0 -122.365248,37.819267,0
                    </coordinates>
                  </LinearRing>
                </outerBoundaryIs>
              </Polygon>
            </MultiGeometry>
          </MultiGeometry>
        </Placemark></Document></kml>
        """

        k = kml.KML()
        k.from_string(doc)
        placemark = next(iter(next(iter(k.features())).features()))

        first_multigeometry = placemark.geometry
        assert len(list(first_multigeometry.geoms)) == 3

        second_multigeometry = next(
            g for g in first_multigeometry.geoms if g.geom_type == "GeometryCollection"
        )
        assert len(list(second_multigeometry.geoms)) == 2


class TestBaseFeature:
    def test_address_string(self) -> None:
        f = kml._Feature()
        address = "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA"
        f.address = address
        assert f.address == address

    def test_address_none(self) -> None:
        f = kml._Feature()
        f.address = None
        assert f.address is None

    def test_address_value_error(self) -> None:
        f = kml._Feature()
        with pytest.raises(ValueError):
            f.address = 123

    def test_phone_number_string(self) -> None:
        f = kml._Feature()
        f.phone_number = "+1-234-567-8901"
        assert f.phone_number == "+1-234-567-8901"

    def test_phone_number_none(self) -> None:
        f = kml._Feature()
        f.phone_number = None
        assert f.phone_number is None

    def test_phone_number_value_error(self) -> None:
        f = kml._Feature()
        with pytest.raises(ValueError):
            f.phone_number = 123


class TestBaseOverlay:
    def test_color_string(self) -> None:
        o = kml._Overlay(name="An Overlay")
        o.color = "00010203"
        assert o.color == "00010203"

    def test_color_none(self) -> None:
        o = kml._Overlay(name="An Overlay")
        o.color = "00010203"
        assert o.color == "00010203"
        o.color = None
        assert o.color is None

    def test_color_value_error(self) -> None:
        o = kml._Overlay(name="An Overlay")
        with pytest.raises(ValueError):
            o.color = object()

    def test_draw_order_string(self) -> None:
        o = kml._Overlay(name="An Overlay")
        o.draw_order = "1"
        assert o.draw_order == "1"

    def test_draw_order_int(self) -> None:
        o = kml._Overlay(name="An Overlay")
        o.draw_order = 1
        assert o.draw_order == "1"

    def test_draw_order_none(self) -> None:
        o = kml._Overlay(name="An Overlay")
        o.draw_order = "1"
        assert o.draw_order == "1"
        o.draw_order = None
        assert o.draw_order is None

    def test_draw_order_value_error(self) -> None:
        o = kml._Overlay(name="An Overlay")
        with pytest.raises(ValueError):
            o.draw_order = object()

    def test_icon_raise_exception(self) -> None:
        o = kml._Overlay(name="An Overlay")
        with pytest.raises(ValueError):
            o.icon = 12345


class TestGroundOverlay:
    def setup_method(self) -> None:
        self.g = kml.GroundOverlay()

    def test_altitude_int(self) -> None:
        self.g.altitude = 123
        assert self.g.altitude == "123"

    def test_altitude_float(self) -> None:
        self.g.altitude = 123.4
        assert self.g.altitude == "123.4"

    def test_altitude_string(self) -> None:
        self.g.altitude = "123"
        assert self.g.altitude == "123"

    def test_altitude_value_error(self) -> None:
        with pytest.raises(ValueError):
            self.g.altitude = object()

    def test_altitude_none(self) -> None:
        self.g.altitude = "123"
        assert self.g.altitude == "123"
        self.g.altitude = None
        assert self.g.altitude is None

    def test_altitude_mode_default(self) -> None:
        assert self.g.altitude_mode == "clampToGround"

    def test_altitude_mode_error(self) -> None:
        self.g.altitude_mode = ""
        assert self.g.altitude_mode == "clampToGround"

    def test_altitude_mode_clamp(self) -> None:
        self.g.altitude_mode = "clampToGround"
        assert self.g.altitude_mode == "clampToGround"

    def test_altitude_mode_absolute(self) -> None:
        self.g.altitude_mode = "absolute"
        assert self.g.altitude_mode == "absolute"

    def test_latlonbox_function(self) -> None:
        self.g.lat_lon_box(10, 20, 30, 40, 50)

        assert self.g.north == "10"
        assert self.g.south == "20"
        assert self.g.east == "30"
        assert self.g.west == "40"
        assert self.g.rotation == "50"

    def test_latlonbox_string(self) -> None:
        self.g.north = "10"
        self.g.south = "20"
        self.g.east = "30"
        self.g.west = "40"
        self.g.rotation = "50"

        assert self.g.north == "10"
        assert self.g.south == "20"
        assert self.g.east == "30"
        assert self.g.west == "40"
        assert self.g.rotation == "50"

    def test_latlonbox_int(self) -> None:
        self.g.north = 10
        self.g.south = 20
        self.g.east = 30
        self.g.west = 40
        self.g.rotation = 50

        assert self.g.north == "10"
        assert self.g.south == "20"
        assert self.g.east == "30"
        assert self.g.west == "40"
        assert self.g.rotation == "50"

    def test_latlonbox_float(self) -> None:
        self.g.north = 10.0
        self.g.south = 20.0
        self.g.east = 30.0
        self.g.west = 40.0
        self.g.rotation = 50.0

        assert self.g.north == "10.0"
        assert self.g.south == "20.0"
        assert self.g.east == "30.0"
        assert self.g.west == "40.0"
        assert self.g.rotation == "50.0"

    def test_latlonbox_value_error(self) -> None:
        with pytest.raises(ValueError):
            self.g.north = object()

        with pytest.raises(ValueError):
            self.g.south = object()

        with pytest.raises(ValueError):
            self.g.east = object()

        with pytest.raises(ValueError):
            self.g.west = object()

        with pytest.raises(ValueError):
            self.g.rotation = object()

        assert self.g.north is None
        assert self.g.south is None
        assert self.g.east is None
        assert self.g.west is None
        assert self.g.rotation is None

    def test_latlonbox_empty_string(self) -> None:
        self.g.north = ""
        self.g.south = ""
        self.g.east = ""
        self.g.west = ""
        self.g.rotation = ""

        assert not self.g.north
        assert not self.g.south
        assert not self.g.east
        assert not self.g.west
        assert not self.g.rotation

    def test_latlonbox_none(self) -> None:
        self.g.north = None
        self.g.south = None
        self.g.east = None
        self.g.west = None
        self.g.rotation = None

        assert self.g.north is None
        assert self.g.south is None
        assert self.g.east is None
        assert self.g.west is None
        assert self.g.rotation is None


class TestGroundOverlayString:
    def test_default_to_string(self) -> None:
        g = kml.GroundOverlay()

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "</kml:GroundOverlay>",
        )
        assert g.to_string() == expected.to_string()

    def test_to_string(self) -> None:
        g = kml.GroundOverlay()
        icon = kml.Icon(href="http://example.com")
        g.icon = icon
        g.draw_order = 1
        g.color = "00010203"

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:color>00010203</kml:color>"
            "<kml:drawOrder>1</kml:drawOrder>"
            "<kml:Icon>"
            "<kml:href>http://example.com</kml:href>"
            "</kml:Icon>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_int(self) -> None:
        g = kml.GroundOverlay()
        g.altitude = 123

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:altitude>123</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_float(self) -> None:
        g = kml.GroundOverlay()
        g.altitude = 123.4

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_from_string(self) -> None:
        g = kml.GroundOverlay()
        g.altitude = "123.4"

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_mode_absolute(self) -> None:
        g = kml.GroundOverlay()
        g.altitude = "123.4"
        g.altitude_mode = "absolute"

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>absolute</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_mode_unknown_string(self) -> None:
        g = kml.GroundOverlay()
        g.altitude = "123.4"
        g.altitudeMode = "unknown string"

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_altitude_mode_value(self) -> None:
        g = kml.GroundOverlay()
        g.altitude = "123.4"
        g.altitudeMode = 1234

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:altitude>123.4</kml:altitude>"
            "<kml:altitudeMode>clampToGround</kml:altitudeMode>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_latlonbox_no_rotation(self) -> None:
        g = kml.GroundOverlay()
        g.lat_lon_box(10, 20, 30, 40)

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:LatLonBox>"
            "<kml:north>10</kml:north>"
            "<kml:south>20</kml:south>"
            "<kml:east>30</kml:east>"
            "<kml:west>40</kml:west>"
            "<kml:rotation>0</kml:rotation>"
            "</kml:LatLonBox>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_latlonbox_rotation(self) -> None:
        g = kml.GroundOverlay()
        g.lat_lon_box(10, 20, 30, 40, 50)

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:LatLonBox>"
            "<kml:north>10</kml:north>"
            "<kml:south>20</kml:south>"
            "<kml:east>30</kml:east>"
            "<kml:west>40</kml:west>"
            "<kml:rotation>50</kml:rotation>"
            "</kml:LatLonBox>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()

    def test_latlonbox_nswer(self) -> None:
        g = kml.GroundOverlay()
        g.north = 10
        g.south = 20
        g.east = 30
        g.west = 40
        g.rotation = 50

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:visibility>1</kml:visibility>"
            "<kml:LatLonBox>"
            "<kml:north>10</kml:north>"
            "<kml:south>20</kml:south>"
            "<kml:east>30</kml:east>"
            "<kml:west>40</kml:west>"
            "<kml:rotation>50</kml:rotation>"
            "</kml:LatLonBox>"
            "</kml:GroundOverlay>",
        )

        assert g.to_string() == expected.to_string()


class TestPhotoOverlay:
    def setup_method(self) -> None:
        self.p = kml.PhotoOverlay()
        self.p.camera = kml.Camera()

    def test_camera_altitude_int(self) -> None:
        self.p.camera.altitude = 123
        assert self.p.camera.altitude == 123

    def test_camera_altitude_float(self) -> None:
        self.p.camera.altitude = 123.4
        assert self.p.camera.altitude == 123.4

    def test_camera_altitude_string(self) -> None:
        self.p.camera.altitude = 123
        assert self.p.camera.altitude == 123

    def test_camera_altitude_value_error(self) -> None:
        with pytest.raises(ValueError):
            self.p.camera.altitude = object()

    def test_camera_altitude_none(self) -> None:
        self.p.camera.altitude = 123
        assert self.p.camera.altitude == 123
        self.p.camera.altitude = None
        assert self.p.camera.altitude is None

    def test_camera_altitude_mode_default(self) -> None:
        assert self.p.camera.altitude_mode == AltitudeMode("relativeToGround")

    def test_camera_altitude_mode_clamp(self) -> None:
        self.p.camera.altitude_mode = AltitudeMode("clampToGround")
        assert self.p.camera.altitude_mode == AltitudeMode("clampToGround")

    def test_camera_altitude_mode_absolute(self) -> None:
        self.p.camera.altitude_mode = "absolute"
        assert self.p.camera.altitude_mode == "absolute"

    def test_camera_initialization(self) -> None:
        self.p.camera = kml.Camera(
            longitude=10,
            latitude=20,
            altitude=30,
            heading=40,
            tilt=50,
            roll=60,
        )
        assert self.p.camera.longitude == 10
        assert self.p.camera.latitude == 20
        assert self.p.camera.altitude == 30
        assert self.p.camera.heading == 40
        assert self.p.camera.tilt == 50
        assert self.p.camera.roll == 60
        assert self.p.camera.altitude_mode == AltitudeMode("relativeToGround")
