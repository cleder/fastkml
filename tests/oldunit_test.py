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

from pygeoif.geometry import MultiPoint
from pygeoif.geometry import Polygon

from fastkml import atom
from fastkml import base
from fastkml import config
from fastkml import features
from fastkml import kml
from fastkml import styles
from fastkml.enums import ColorMode
from fastkml.enums import DisplayMode


class TestBaseClasses:
    """
    BaseClasses  must raise a NotImplementedError on etree_element.
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
        bo.target_id = "target"
        assert bo.target_id == "target"
        bo.ns = ""
        bo.id = None
        assert bo.id is None
        assert not bo.ns


class TestBuildKml:
    """Build a simple KML File."""

    def setup_method(self) -> None:
        """Always test with the same parser."""
        config.set_etree_implementation(xml.etree.ElementTree)
        config.set_default_namespaces()

    def test_kml(self) -> None:
        """Kml file without contents."""
        k = kml.KML(ns="")
        assert k.features == []
        assert (
            str(k.to_string())[:51]
            == '<kml xmlns="http://www.opengis.net/kml/2.2" />'[:51]
        )
        k2 = kml.KML.class_from_string(k.to_string(), ns="")
        assert k.to_string() == k2.to_string()

    def test_folder(self) -> None:
        """KML file with folders."""
        ns = "{http://www.opengis.net/kml/2.2}"
        k = kml.KML(ns=ns)
        f = kml.Folder(ns=ns, id="id", name="name", description="description")
        nf = kml.Folder(
            ns=ns,
            id="nested-id",
            name="nested-name",
            description="nested-description",
        )
        f.append(nf)
        k.append(f)
        f2 = kml.Folder(ns, id="id2", name="name2", description="description2")
        k.append(f2)
        assert len(k.features) == 2
        assert len(k.features[0].features) == 1
        s = k.to_string()
        k2 = kml.KML.class_from_string(s, ns=ns)
        assert s == k2.to_string()

    def test_placemark(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        k = kml.KML(ns=ns)
        p = kml.Placemark(ns, id="id", name="name", description="description")
        # XXX p.geometry = Point(0.0, 0.0, 0.0)
        p2 = kml.Placemark(ns, id="id2", name="name2", description="description2")
        # XXX p2.geometry = LineString([(0, 0, 0), (1, 1, 1)])
        k.append(p)
        k.append(p2)
        assert len(k.features) == 2
        k2 = kml.KML.class_from_string(k.to_string(prettyprint=True), ns=ns)
        assert k.to_string() == k2.to_string()

    def test_document(self) -> None:
        ns = "{http://www.opengis.net/kml/2.2}"
        k = kml.KML(ns=ns)
        d = kml.Document(ns, id="docid", name="doc name", description="doc description")
        f = kml.Folder(ns, id="fid", name="f name", description="f description")
        k.append(d)
        d.append(f)
        nf = kml.Folder(
            ns,
            id="nested-fid",
            name="nested f name",
            description="nested f description",
        )
        f.append(nf)
        f2 = kml.Folder(ns, id="id2", name="name2", description="description2")
        d.append(f2)
        p = kml.Placemark(ns, id="id", name="name", description="description")
        # XXX p.geometry = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
        p2 = kml.Placemark(ns, id="id2", name="name2", description="description2")
        # p2 does not have a geometry!
        f2.append(p)
        nf.append(p2)
        assert len(k.features) == 1
        assert len(k.features[0].features) == 2
        k2 = kml.KML.class_from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_author(self) -> None:
        d = kml.Document()
        d.atom_author = atom.Author(
            ns="{http://www.w3.org/2005/Atom}",
            name="Christian Ledermann",
        )
        assert "Christian Ledermann" in str(d.to_string())
        a = atom.Author(
            ns="{http://www.w3.org/2005/Atom}",
            name="Nobody",
            uri="http://localhost",
            email="cl@donotreply.com",
        )
        d.atom_author = a
        assert "Christian Ledermann" not in str(d.to_string())
        assert "Nobody" in str(d.to_string())
        assert "http://localhost" in str(d.to_string())
        assert "cl@donotreply.com" in str(d.to_string())
        d2 = kml.Document.class_from_string(d.to_string())
        assert d.to_string() == d2.to_string()

    def test_link(self) -> None:
        d = kml.Document()
        d.atom_link = atom.Link(ns=config.ATOMNS, href="http://localhost")
        assert "http://localhost" in str(d.to_string())
        d.atom_link = atom.Link(ns=config.ATOMNS, href="#here")
        assert "#here" in str(d.to_string())
        d2 = kml.Document.class_from_string(d.to_string())
        assert d.to_string() == d2.to_string()

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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert len(k.features[0].features) == 2
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert len(k.features[0].features) == 3
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert k.features[0].name == "Simple placemark"
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].geometry, Polygon)
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].geometry, MultiPoint)
        assert len(list(k.features[0].geometry.geoms)) == 12
        k2 = kml.KML.class_from_string(k.to_string())
        assert k.to_string() == k2.to_string()

    def test_atom(self) -> None:
        pass

    def test_snippet(self) -> None:
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
        <Snippet maxLines="2" >Short Desc</Snippet>
        </Placemark> </kml>"""

        k = kml.KML.class_from_string(doc)
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
        doc = kml.Document.class_from_string(
            """
        <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2" id="pm-id">
            <kml:name>pm-name</kml:name>
            <kml:description>pm-description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:address>1600 Amphitheatre Parkway,...</kml:address>
        </kml:Document>
        """,
        )

        doc2 = kml.Document.class_from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()

    def test_phone_number(self) -> None:
        doc = kml.Document.class_from_string(
            """
        <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2" id="pm-id">
            <kml:name>pm-name</kml:name>
            <kml:description>pm-description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:phoneNumber>+1 234 567 8901</kml:phoneNumber>
        </kml:Document>
        """,
        )

        doc2 = kml.Document.class_from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()

    def test_groundoverlay(self) -> None:
        doc = kml.KML.class_from_string(
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

        doc2 = kml.KML.class_from_string(doc.to_string())
        assert doc.to_string() == doc2.to_string()


class TestStyle:
    def test_styleurl(self) -> None:
        f = kml.Document()
        s = styles.StyleUrl(config.KMLNS, url="#otherstyle")
        f.style_url = s
        f2 = kml.Document.class_from_string(f.to_string())
        assert f.to_string() == f2.to_string()
        assert isinstance(f2.style_url, styles.StyleUrl)
        assert f2.style_url.url == "#otherstyle"

    def test_style(self) -> None:
        lstyle = styles.LineStyle(color="red", width=2.0)
        style = styles.Style(styles=[lstyle])
        f = kml.Document(styles=[style])
        f2 = kml.Document.class_from_string(f.to_string(prettyprint=True))
        assert f.to_string() == f2.to_string()

    def test_polystyle_fill(self) -> None:
        styles.PolyStyle()

    def test_polystyle_outline(self) -> None:
        styles.PolyStyle()


class TestStyleUsage:
    def test_create_document_style(self) -> None:
        style = styles.Style(
            styles=[
                styles.PolyStyle(
                    color="7f000000",
                    fill=True,
                    outline=True,
                ),
            ],
        )

        doc = kml.Document(styles=[style])

        doc2 = kml.Document()
        doc2.styles.append(style)

        expected = """
            <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2">
              <kml:visibility/>
                <kml:Style>
                  <kml:PolyStyle>
                    <kml:color>7f000000</kml:color>
                    <kml:fill>1</kml:fill>
                    <kml:outline>1</kml:outline>
                  </kml:PolyStyle>
                </kml:Style>
            </kml:Document>
        """

        doc3 = kml.Document.class_from_string(expected)

        assert doc.to_string() == doc2.to_string()
        assert doc2.to_string() == doc3.to_string()
        assert doc.to_string() == doc3.to_string()

    def test_create_placemark_style(self) -> None:
        style = styles.Style(
            styles=[
                styles.PolyStyle(
                    color="7f000000",
                    fill=True,
                    outline=True,
                ),
            ],
        )

        place = kml.Placemark(styles=[style])

        place2 = kml.Placemark()
        place2.styles.append(style)

        expected = """
            <kml:Placemark xmlns:kml="http://www.opengis.net/kml/2.2">
                <kml:Style>
                  <kml:PolyStyle>
                    <kml:color>7f000000</kml:color>
                    <kml:fill>1</kml:fill>
                    <kml:outline>1</kml:outline>
                  </kml:PolyStyle>
                </kml:Style>
            </kml:Placemark>
        """

        place3 = kml.Placemark.class_from_string(expected)
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert k.features[0].style_url.url == "#default"
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        features = k.features
        assert len(features) == 1
        style = features[0].styles[0]
        assert isinstance(style, styles.Style)
        style_1 = style.styles[0]
        assert isinstance(style_1, styles.BalloonStyle)
        assert style_1.bg_color == "ffffffbb"
        assert style_1.text_color == "ff000000"
        assert style_1.display_mode == DisplayMode.default
        assert style_1.text
        assert "$[geDirections]" in style_1.text
        assert "$[description]" in style_1.text
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].styles[0], styles.Style)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.BalloonStyle)
        assert style.bg_color is None
        assert not style
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].styles[0], styles.Style)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.LabelStyle)
        assert style.color == "ff0000cc"
        assert style.color_mode is None
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].styles[0], styles.Style)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.IconStyle)
        assert style.color == "ff00ff00"
        assert style.scale == 1.1
        assert style.color_mode == ColorMode.random
        assert style.heading == 0.0
        assert style.icon.href == "http://maps.google.com/icon21.png"
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].styles[0], styles.Style)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.LineStyle)
        assert style.color == "7f0000ff"
        assert style.width == 4
        k2 = kml.KML.class_from_string(k.to_string())
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
        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].styles[0], styles.Style)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.PolyStyle)
        assert style.color == "ff0000cc"
        assert style.color_mode == ColorMode.random
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc, strict=False)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.PolyStyle)
        assert style.fill == 0
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc, strict=False)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.PolyStyle)
        assert style.outline == 0
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc, strict=False)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.PolyStyle)
        assert style.fill == 0
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc, strict=False)
        style = k.features[0].styles[0].styles[0]
        assert isinstance(style, styles.PolyStyle)
        assert style.outline == 0
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(k.features[0].styles[0], styles.Style)
        style = k.features[0].styles[0].styles
        assert len(style) == 4
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        features = k.features
        assert len(features) == 1
        feature_styles = features[0].styles
        assert isinstance(
            feature_styles[0],
            styles.StyleMap,
        )
        sm = feature_styles[0]

        assert isinstance(sm.normal, styles.StyleUrl)
        assert sm.normal.url == "#normalState"
        assert isinstance(sm.highlight, styles.StyleUrl)
        assert sm.highlight.url == "#highlightState"
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        assert isinstance(
            k.features[0].styles[0],
            styles.StyleMap,
        )
        sm = k.features[0].styles[0]
        assert isinstance(sm.normal, styles.Style)
        assert len(sm.normal.styles) == 1
        assert isinstance(sm.normal.styles[0], styles.LabelStyle)
        assert isinstance(sm.highlight, styles.Style)
        assert isinstance(sm.highlight, styles.Style)
        assert len(sm.highlight.styles) == 2
        assert isinstance(sm.highlight.styles[0], styles.LineStyle)
        assert isinstance(sm.highlight.styles[1], styles.PolyStyle)
        k2 = kml.KML.class_from_string(k.to_string())
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

        k = kml.KML.class_from_string(doc)
        assert len(k.features) == 1
        document = k.features[0]
        style = document.get_style_by_url(
            "http://localhost:8080/somepath#exampleStyleDocument",
        )
        assert isinstance(style.styles[0], styles.LabelStyle)
        style = document.get_style_by_url("somepath#linestyleExample")
        assert isinstance(style.styles[0], styles.LineStyle)
        style = document.get_style_by_url("#styleMapExample")
        assert isinstance(style, styles.StyleMap)


def test_nested_multigeometry() -> None:
    doc = """<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark>
          <MultiGeometry>
            <Polygon>
              <outerBoundaryIs>
                <LinearRing>
                  <coordinates>
                    -122.366278,37.818844,0 -122.365248,37.819267,0
                    -122.365640,37.819875,0 -122.366278,37.818844,0
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
                      -122.365248,37.819267,0 -122.365640,37.819875,0
                      -122.366278,37.818844,0 -122.365248,37.819267,0
                    </coordinates>
                  </LinearRing>
                </outerBoundaryIs>
              </Polygon>
            </MultiGeometry>
          </MultiGeometry>
        </Placemark></Document></kml>
        """

    k = kml.KML.class_from_string(doc)
    placemark = k.features[0].features[0]

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
                    -122.366278,37.818844,0 -122.365248,37.819267,0
                    -122.365640,37.819875,0 -122.366278,37.818844,0
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
                      -122.365248,37.819267,0 -122.365640,37.819875,0
                      -122.366278,37.818844,0 -122.365248,37.819267,0
                    </coordinates>
                  </LinearRing>
                </outerBoundaryIs>
              </Polygon>
            </MultiGeometry>
          </MultiGeometry>
        </Placemark></Document></kml>
        """

        k = kml.KML.class_from_string(doc)
        placemark = k.features[0].features[0]

        first_multigeometry = placemark.geometry
        assert len(list(first_multigeometry.geoms)) == 3

        second_multigeometry = next(
            g for g in first_multigeometry.geoms if g.geom_type == "GeometryCollection"
        )
        assert len(list(second_multigeometry.geoms)) == 2
