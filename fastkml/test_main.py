# -*- coding: utf-8 -*-
# Copyright (C) 2012  Christian Ledermann
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

try:
    import unittest2 as unittest  # Needed in Python 2.6
except:
    import unittest

from fastkml import kml
from fastkml import styles
from fastkml import base
from fastkml import atom
from fastkml import config
from fastkml import gx  # NOQA

import datetime
from dateutil.tz import tzutc, tzoffset

from fastkml.config import etree

from fastkml.geometry import Point, LineString, Polygon
from fastkml.geometry import MultiPoint, MultiLineString, MultiPolygon
from fastkml.geometry import LinearRing, GeometryCollection
from fastkml.geometry import Geometry


class BaseClassesTestCase(unittest.TestCase):
    """ BaseClasses  must raise a NotImplementedError on etree_element
    and a TypeError on from_element """

    def test_base_object(self):
        bo = base._BaseObject(id='id0')
        self.assertEqual(bo.id, 'id0')
        self.assertEqual(bo.ns, config.NS)
        self.assertEqual(bo.targetId, None)
        self.assertEqual(bo.__name__, None)
        bo.targetId = 'target'
        self.assertEqual(bo.targetId, 'target')
        bo.ns = ''
        bo.id = None
        self.assertEqual(bo.id, None)
        self.assertEqual(bo.ns, '')
        self.assertRaises(NotImplementedError, bo.etree_element)
        element = etree.Element(config.NS + 'Base')
        self.assertRaises(TypeError, bo.from_element)
        self.assertRaises(TypeError, bo.from_element, element)
        bo.__name__ = 'NotABaseObject'
        self.assertRaises(TypeError, bo.from_element, element)
        # Note that we can coax baseclasses not to throw errors
        bo.__name__ = 'Base'
        bo.ns = config.NS
        bo.from_element(element)
        self.assertEqual(bo.id, None)
        self.assertEqual(bo.ns, config.NS)
        self.assertFalse(bo.etree_element(), None)
        self.assertTrue(len(bo.to_string()) > 1)

    def test_feature(self):
        f = kml._Feature(name='A Feature')
        self.assertRaises(NotImplementedError, f.etree_element)
        self.assertEqual(f.name, 'A Feature')
        self.assertEqual(f.visibility, 1)
        self.assertEqual(f.isopen, 0)
        self.assertEqual(f._atom_author, None)
        self.assertEqual(f._atom_link, None)
        self.assertEqual(f.address, None)
        # self.assertEqual(f.phoneNumber, None)
        self.assertEqual(f._snippet, None)
        self.assertEqual(f.description, None)
        self.assertEqual(f._styleUrl, None)
        self.assertEqual(f._styles, [])
        self.assertEqual(f._time_span, None)
        self.assertEqual(f._time_stamp, None)
        # self.assertEqual(f.region, None)
        # self.assertEqual(f.extended_data, None)

        f.__name__ = 'Feature'
        f.styleUrl = '#default'
        self.assertTrue('Feature>' in str(f.to_string()))
        self.assertTrue('#default' in str(f.to_string()))

    def test_container(self):
        f = kml._Container(name='A Container')
        # apparently you can add documents to containes
        # d = kml.Document()
        # self.assertRaises(TypeError, f.append, d)
        p = kml.Placemark()
        f.append(p)
        self.assertRaises(NotImplementedError, f.etree_element)

    def test_overlay(self):
        o = kml._Overlay(name='An Overlay')
        self.assertEqual(o._color, None)
        self.assertEqual(o._drawOrder, None)
        self.assertEqual(o._icon, None)
        self.assertRaises(NotImplementedError, o.etree_element)

    def test_atom_link(self):
        ns = '{http://www.opengis.net/kml/2.2}'
        l = atom.Link(ns=ns)
        self.assertEqual(l.ns, ns)

    def test_atom_person(self):
        ns = '{http://www.opengis.net/kml/2.2}'
        p = atom._Person(ns=ns)
        self.assertEqual(p.ns, ns)


class BuildKmlTestCase(unittest.TestCase):
    """ Build a simple KML File """

    def test_kml(self):
        """ kml file without contents """
        k = kml.KML()
        self.assertEqual(len(list(k.features())), 0)
        if config.LXML:
            self.assertEqual(
                str(k.to_string())[:43],
                '<kml xmlns="http://www.opengis.net/kml/2.2"/>' [:43])
        else:
            if hasattr(etree, 'register_namespace'):
                self.assertEqual(str(k.to_string())[:51], '<kml:kml xmlns:kml="http://www.opengis.net/kml/2.2" />'[:51])
            else:
                self.assertEqual(str(k.to_string())[:51], '<ns0:kml xmlns:ns0="http://www.opengis.net/kml/2.2" />'[:51])

        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_folder(self):
        """ KML file with folders """
        ns = '{http://www.opengis.net/kml/2.2}'
        k = kml.KML()
        f = kml.Folder(ns, 'id', 'name', 'description')
        nf = kml.Folder(ns, 'nested-id', 'nested-name', 'nested-description')
        f.append(nf)
        k.append(f)
        f2 = kml.Folder(ns, 'id2', 'name2', 'description2')
        k.append(f2)
        self.assertEqual(len(list(k.features())), 2)
        self.assertEqual(len(list(list(k.features())[0].features())), 1)
        k2 = kml.KML()
        s = k.to_string()
        k2.from_string(s)
        self.assertEqual(s, k2.to_string())

    def test_placemark(self):
        ns = '{http://www.opengis.net/kml/2.2}'
        k = kml.KML(ns=ns)
        p = kml.Placemark(ns, 'id', 'name', 'description')
        p.geometry = Point(0.0, 0.0, 0.0)
        p2 = kml.Placemark(ns, 'id2', 'name2', 'description2')
        p2.geometry = LineString([(0, 0, 0), (1, 1, 1)])
        k.append(p)
        k.append(p2)
        self.assertEqual(len(list(k.features())), 2)
        k2 = kml.KML()
        k2.from_string(k.to_string(prettyprint=True))
        self.assertEqual(k.to_string(), k2.to_string())

    def test_schema(self):
        ns = '{http://www.opengis.net/kml/2.2}'
        self.assertRaises(ValueError, kml.Schema, ns)
        s = kml.Schema(ns, 'some_id')
        self.assertEqual(len(list(s.simple_fields)), 0)
        s.append('int', 'Integer', 'An Integer')
        self.assertEqual(list(s.simple_fields)[0]['type'], 'int')
        self.assertEqual(list(s.simple_fields)[0]['name'], 'Integer')
        self.assertEqual(list(s.simple_fields)[0]['displayName'], 'An Integer')
        s.simple_fields = None
        self.assertEqual(len(list(s.simple_fields)), 0)
        self.assertRaises(
            TypeError, s.append, ('none', 'Integer', 'An Integer'))
        self.assertRaises(
            TypeError, s.simple_fields, [('none', 'Integer', 'An Integer')])
        self.assertRaises(
            TypeError, s.simple_fields, ('int', 'Integer', 'An Integer'))
        fields = {
            'type': 'int',
            'name': 'Integer',
            'displayName': 'An Integer'
        }
        s.simple_fields = fields
        self.assertEqual(list(s.simple_fields)[0]['type'], 'int')
        self.assertEqual(list(s.simple_fields)[0]['name'], 'Integer')
        self.assertEqual(list(s.simple_fields)[0]['displayName'], 'An Integer')
        s.simple_fields = [['float', 'Float'], fields]
        self.assertEqual(list(s.simple_fields)[0]['type'], 'float')
        self.assertEqual(list(s.simple_fields)[0]['name'], 'Float')
        self.assertEqual(list(s.simple_fields)[0]['displayName'], None)
        self.assertEqual(list(s.simple_fields)[1]['type'], 'int')
        self.assertEqual(list(s.simple_fields)[1]['name'], 'Integer')
        self.assertEqual(list(s.simple_fields)[1]['displayName'], 'An Integer')

    def test_schema_data(self):
        ns = '{http://www.opengis.net/kml/2.2}'
        self.assertRaises(ValueError, kml.SchemaData, ns)
        self.assertRaises(ValueError, kml.SchemaData, ns, '')
        sd = kml.SchemaData(ns, '#default')
        sd.append_data('text', 'Some Text')
        self.assertEqual(len(sd.data), 1)
        sd.append_data(value=1, name='Integer')
        self.assertEqual(len(sd.data), 2)
        self.assertEqual(sd.data[0], {'value': 'Some Text', 'name': 'text'})
        self.assertEqual(sd.data[1], {'value': 1, 'name': 'Integer'})
        data = (('text', 'Some new Text'), {'value': 2, 'name': 'Integer'})
        sd.data = data
        self.assertEqual(len(sd.data), 2)
        self.assertEqual(
            sd.data[0], {'value': 'Some new Text',
                         'name': 'text'})
        self.assertEqual(sd.data[1], {'value': 2, 'name': 'Integer'})

    def test_untyped_extended_data(self):
        ns = '{http://www.opengis.net/kml/2.2}'
        k = kml.KML(ns=ns)

        p = kml.Placemark(ns, 'id', 'name', 'description')
        p.geometry = Point(0.0, 0.0, 0.0)
        p.extended_data = kml.UntypedExtendedData(elements=[
            kml.UntypedExtendedDataElement(
                name='info',
                value='so much to see'), kml.UntypedExtendedDataElement(
                    name='weather',
                    display_name='Weather',
                    value='blue skies')
        ])

        self.assertEqual(len(p.extended_data.elements), 2)
        k.append(p)

        k2 = kml.KML()
        k2.from_string(k.to_string(prettyprint=True))
        k.to_string()

        extended_data = list(k2.features())[0].extended_data
        self.assertTrue(extended_data is not None)
        self.assertTrue(len(extended_data.elements), 2)
        self.assertEqual(extended_data.elements[0].name, 'info')
        self.assertEqual(extended_data.elements[0].value, 'so much to see')
        self.assertEqual(extended_data.elements[0].display_name, None)
        self.assertEqual(extended_data.elements[1].name, 'weather')
        self.assertEqual(extended_data.elements[1].value, 'blue skies')
        self.assertEqual(extended_data.elements[1].display_name, 'Weather')

    def test_untyped_extended_data_nested(self):
        ns = '{http://www.opengis.net/kml/2.2}'
        k = kml.KML(ns=ns)

        d = kml.Document(ns, 'docid', 'doc name', 'doc description')
        d.extended_data = kml.UntypedExtendedData(elements=[
            kml.UntypedExtendedDataElement(name='type',
                                           value='Document')
        ])

        f = kml.Folder(ns, 'fid', 'f name', 'f description')
        f.extended_data = kml.UntypedExtendedData(elements=[
            kml.UntypedExtendedDataElement(name='type',
                                           value='Folder')
        ])

        k.append(d)
        d.append(f)

        k2 = kml.KML()
        k2.from_string(k.to_string())

        document_data = list(k2.features())[0].extended_data
        folder_data = list(list(k2.features())[0].features())[0].extended_data

        self.assertEqual(document_data.elements[0].name, 'type')
        self.assertEqual(document_data.elements[0].value, 'Document')

        self.assertEqual(folder_data.elements[0].name, 'type')
        self.assertEqual(folder_data.elements[0].value, 'Folder')

    def test_document(self):
        k = kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        d = kml.Document(ns, 'docid', 'doc name', 'doc description')
        f = kml.Folder(ns, 'fid', 'f name', 'f description')
        k.append(d)
        d.append(f)
        nf = kml.Folder(
            ns, 'nested-fid', 'nested f name', 'nested f description')
        f.append(nf)
        f2 = kml.Folder(ns, 'id2', 'name2', 'description2')
        d.append(f2)
        p = kml.Placemark(ns, 'id', 'name', 'description')
        p.geometry = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
        p2 = kml.Placemark(ns, 'id2', 'name2', 'description2')
        # p2 does not have a geometry!
        f2.append(p)
        nf.append(p2)
        self.assertEqual(len(list(k.features())), 1)
        self.assertEqual(len(list((list(k.features())[0].features()))), 2)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_author(self):
        d = kml.Document()
        d.author = 'Christian Ledermann'
        self.assertTrue('Christian Ledermann' in str(d.to_string()))
        a = atom.Author(
            name='Nobody',
            uri='http://localhost',
            email='cl@donotreply.com')
        d.author = a
        self.assertEqual(d.author, 'Nobody')
        self.assertFalse('Christian Ledermann' in str(d.to_string()))
        self.assertTrue('Nobody' in str(d.to_string()))
        self.assertTrue('http://localhost' in str(d.to_string()))
        self.assertTrue('cl@donotreply.com' in str(d.to_string()))
        d2 = kml.Document()
        d2.from_string(d.to_string())
        self.assertEqual(d.to_string(), d2.to_string())
        d.author = None

    def test_link(self):
        d = kml.Document()
        d.link = 'http://localhost'
        self.assertTrue('http://localhost' in str(d.to_string()))
        l = atom.Link(href='#here')
        d.link = l
        self.assertTrue('#here' in str(d.to_string()))
        self.assertRaises(TypeError, d.link, object)
        d2 = kml.Document()
        d2.from_string(d.to_string())
        self.assertEqual(d.to_string(), d2.to_string())
        d.link = None

    def test_address(self):
        address = '1600 Amphitheatre Parkway, Mountain View, CA 94043, USA'
        d = kml.Document()
        d.address = address
        self.assertTrue(address in str(d.to_string()))
        self.assertTrue('address>' in str(d.to_string()))

    def test_phone_number(self):
        phone = '+1 234 567 8901'
        d = kml.Document()
        d.phoneNumber = phone
        self.assertTrue(phone in str(d.to_string()))
        self.assertTrue('phoneNumber>' in str(d.to_string()))


class KmlFromStringTestCase(unittest.TestCase):

    def test_document(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertEqual(len(list(list(k.features())[0].features())), 2)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_document_booleans(self):
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document targetId="someTargetId">
          <name>Document.kml</name>
          <visibility>true</visibility>
          <open>1</open>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        self.assertEqual(list(k.features())[0].visibility, 1)
        self.assertEqual(list(k.features())[0].isopen, 1)
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document targetId="someTargetId">
          <name>Document.kml</name>
          <visibility>0</visibility>
          <open>false</open>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        self.assertEqual(list(k.features())[0].visibility, 0)
        self.assertEqual(list(k.features())[0].isopen, 0)

    def test_folders(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertEqual(len(list(list(k.features())[0].features())), 3)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_placemark(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertEqual(list(k.features())[0].name, "Simple placemark")
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_extended_data(self):
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
          <Placemark>
            <name>Simple placemark</name>
            <description></description>
            <Point>
              <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
            </Point>
            <ExtendedData>
              <Data name="holeNumber">
                <displayName><![CDATA[
                    <b>This is hole </b>
                ]]></displayName>
                <value>1</value>
              </Data>
              <Data name="holePar">
                <displayName><![CDATA[
                  <i>The par for this hole is </i>
                ]]></displayName>
                <value>4</value>
              </Data>
              <SchemaData schemaUrl="#TrailHeadTypeId">
                <SimpleData name="TrailHeadName">Mount Everest</SimpleData>
                <SimpleData name="TrailLength">347.45</SimpleData>
                <SimpleData name="ElevationGain">10000</SimpleData>
              </SchemaData>
            </ExtendedData>
          </Placemark>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)

        extended_data = list(k.features())[0].extended_data

        self.assertEqual(extended_data.elements[0].name, 'holeNumber')
        self.assertEqual(extended_data.elements[0].value, '1')
        self.assertTrue(
            '<b>This is hole </b>' in extended_data.elements[0].display_name)

        self.assertEqual(extended_data.elements[1].name, 'holePar')
        self.assertEqual(extended_data.elements[1].value, '4')
        self.assertTrue(
            '<i>The par for this hole is </i>' in
            extended_data.elements[1].display_name)
        sd = extended_data.elements[2]
        self.assertEqual(sd.data[0]['name'], 'TrailHeadName')
        self.assertEqual(sd.data[1]['value'], '347.45')

    def test_polygon(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(isinstance(list(k.features())[0].geometry, Polygon))
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_multipoints(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(isinstance(list(k.features())[0].geometry, MultiPoint))
        self.assertEqual(len(list(k.features())[0].geometry.geoms), 12)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_multilinestrings(self):
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
          <name>Dnipro (Dnieper)</name>
          <MultiGeometry>
          <LineString><coordinates>33.54,46.831,0 33.606,46.869,0 33.662,46.957,0 33.739,47.05,0 33.859,47.149,0 33.976,47.307,0 33.998,47.411,0 34.155,47.49,0 34.448,47.542,0 34.712,47.553,0 34.946,47.521,0 35.088,47.528,0 35.138,47.573,0 35.149,47.657,0 35.106,47.842,0 </coordinates></LineString>
          <LineString><coordinates>33.194,49.094,0 32.884,49.225,0 32.603,49.302,0 31.886,49.555,0 </coordinates></LineString>
          <LineString><coordinates>31.44,50,0 31.48,49.933,0 31.486,49.871,0 31.467,49.754,0 </coordinates></LineString>
          <LineString><coordinates>30.508,51.217,0 30.478,50.904,0 30.479,50.749,0 30.515,50.597,0 </coordinates></LineString>
          </MultiGeometry>
        </Placemark> </kml>"""

        k = kml.KML()
        k.from_string(doc)
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(list(k.features())[0].geometry, MultiLineString))
        self.assertEqual(len(list(k.features())[0].geometry.geoms), 4)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_multipolygon(self):
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
          <name>Italy</name>
            <MultiGeometry><Polygon><outerBoundaryIs><LinearRing><coordinates>12.621,35.492,0 12.611,35.489,0 12.603,35.491,0 12.598,35.494,0 12.594,35.494,0 12.556,35.508,0 12.536,35.513,0 12.526,35.517,0 12.534,35.522,0 12.556,35.521,0 12.567,35.519,0 12.613,35.515,0 12.621,35.513,0 12.624,35.512,0 12.622,35.51,0 12.621,35.508,0 12.624,35.502,0 12.621,35.492,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>12.873,35.852,0 12.857,35.852,0 12.851,35.856,0 12.846,35.863,0 12.847,35.868,0 12.854,35.871,0 12.86,35.872,0 12.867,35.872,0 12.874,35.866,0 12.877,35.856,0 12.873,35.852,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>11.981,36.827,0 11.988,36.824,0 11.994,36.825,0 12,36.836,0 12.038,36.806,0 12.052,36.79,0 12.054,36.767,0 12.031,36.741,0 11.997,36.745,0 11.962,36.765,0 11.938,36.789,0 11.934,36.795,0 11.926,36.812,0 11.923,36.828,0 11.935,36.836,0 11.939,36.837,0 11.947,36.841,0 11.952,36.843,0 11.958,36.84,0 11.968,36.831,0 11.972,36.829,0 11.981,36.827,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>12.322,37.94,0 12.337,37.933,0 12.355,37.927,0 12.369,37.925,0 12.358,37.914,0 12.343,37.913,0 12.327,37.918,0 12.315,37.925,0 12.3,37.919,0 12.288,37.921,0 12.279,37.929,0 12.274,37.939,0 12.288,37.938,0 12.298,37.941,0 12.306,37.945,0 12.315,37.946,0 12.322,37.94,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>12.078,37.96,0 12.079,37.95,0 12.065,37.951,0 12.048,37.961,0 12.037,37.974,0 12.03,37.984,0 12.036,37.991,0 12.054,37.992,0 12.065,37.986,0 12.072,37.968,0 12.078,37.96,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>15.643,38.262,0 15.635,38.261,0 15.625,38.261,0 15.584,38.24,0 15.57,38.227,0 15.564,38.214,0 15.56,38.2,0 15.576,38.2,0 15.527,38.137,0 15.501,38.085,0 15.393,37.976,0 15.303,37.864,0 15.284,37.833,0 15.267,37.812,0 15.242,37.795,0 15.214,37.761,0 15.207,37.747,0 15.209,37.737,0 15.219,37.718,0 15.221,37.706,0 15.217,37.696,0 15.203,37.685,0 15.2,37.675,0 15.197,37.655,0 15.185,37.626,0 15.179,37.604,0 15.164,37.567,0 15.117,37.522,0 15.097,37.494,0 15.092,37.477,0 15.09,37.459,0 15.093,37.36,0 15.097,37.343,0 15.104,37.33,0 15.111,37.322,0 15.181,37.291,0 15.218,37.285,0 15.237,37.275,0 15.253,37.257,0 15.262,37.234,0 15.245,37.246,0 15.236,37.242,0 15.229,37.23,0 15.221,37.22,0 15.222,37.237,0 15.216,37.244,0 15.206,37.244,0 15.193,37.24,0 15.2,37.227,0 15.184,37.207,0 15.195,37.176,0 15.217,37.155,0 15.234,37.165,0 15.248,37.158,0 15.248,37.152,0 15.23,37.149,0 15.232,37.135,0 15.247,37.118,0 15.265,37.11,0 15.289,37.108,0 15.304,37.101,0 15.309,37.086,0 15.303,37.062,0 15.289,37.069,0 15.283,37.061,0 15.284,37.048,0 15.292,37.042,0 15.313,37.044,0 15.322,37.04,0 15.33,37.027,0 15.333,37.011,0 15.325,37.008,0 15.315,37.012,0 15.309,37.018,0 15.304,37.016,0 15.269,37,0 15.275,36.993,0 15.267,36.989,0 15.264,36.987,0 15.269,36.98,0 15.269,36.973,0 15.245,36.972,0 15.227,36.965,0 15.212,36.956,0 15.197,36.952,0 15.175,36.944,0 15.159,36.924,0 15.108,36.82,0 15.107,36.808,0 15.095,36.799,0 15.099,36.779,0 15.118,36.747,0 15.135,36.687,0 15.135,36.675,0 15.115,36.66,0 15.094,36.655,0 15.074,36.659,0 15.056,36.671,0 15.041,36.687,0 15.034,36.694,0 15.021,36.699,0 15.008,36.703,0 14.998,36.702,0 14.994,36.696,0 14.983,36.689,0 14.958,36.698,0 14.919,36.72,0 14.883,36.73,0 14.847,36.726,0 14.781,36.699,0 14.777,36.707,0 14.774,36.71,0 14.761,36.706,0 14.745,36.719,0 14.685,36.726,0 14.672,36.744,0 14.659,36.754,0 14.601,36.772,0 14.583,36.781,0 14.566,36.778,0 14.488,36.793,0 14.476,36.805,0 14.395,36.945,0 14.37,36.973,0 14.279,37.044,0 14.209,37.081,0 14.127,37.112,0 14.089,37.117,0 13.977,37.11,0 13.968,37.108,0 13.949,37.099,0 13.939,37.096,0 13.895,37.101,0 13.833,37.139,0 13.795,37.152,0 13.752,37.159,0 13.716,37.171,0 13.684,37.189,0 13.599,37.256,0 13.57,37.273,0 13.535,37.282,0 13.489,37.288,0 13.453,37.299,0 13.422,37.314,0 13.373,37.346,0 13.33,37.366,0 13.312,37.381,0 13.303,37.386,0 13.29,37.389,0 13.279,37.393,0 13.254,37.432,0 13.248,37.436,0 13.226,37.446,0 13.215,37.458,0 13.207,37.464,0 13.195,37.466,0 13.19,37.469,0 13.18,37.484,0 13.175,37.487,0 13.052,37.5,0 13.037,37.495,0 13.027,37.493,0 13.017,37.497,0 13.011,37.507,0 13.005,37.527,0 13.001,37.535,0 12.975,37.557,0 12.943,37.568,0 12.863,37.576,0 12.781,37.574,0 12.698,37.563,0 12.66,37.565,0 12.637,37.582,0 12.595,37.638,0 12.578,37.652,0 12.564,37.658,0 12.524,37.658,0 12.507,37.665,0 12.49,37.682,0 12.475,37.703,0 12.466,37.72,0 12.461,37.734,0 12.46,37.748,0 12.457,37.76,0 12.449,37.771,0 12.437,37.783,0 12.428,37.797,0 12.428,37.809,0 12.445,37.816,0 12.447,37.812,0 12.461,37.819,0 12.466,37.823,0 12.464,37.825,0 12.471,37.853,0 12.473,37.854,0 12.478,37.872,0 12.479,37.881,0 12.477,37.886,0 12.468,37.897,0 12.466,37.906,0 12.465,37.913,0 12.465,37.914,0 12.468,37.916,0 12.491,37.954,0 12.497,37.98,0 12.503,37.997,0 12.505,38.011,0 12.493,38.021,0 12.524,38.031,0 12.55,38.055,0 12.577,38.072,0 12.609,38.062,0 12.639,38.079,0 12.652,38.091,0 12.657,38.107,0 12.663,38.116,0 12.677,38.116,0 12.692,38.112,0 12.705,38.111,0 12.726,38.126,0 12.725,38.15,0 12.72,38.175,0 12.732,38.193,0 12.738,38.181,0 12.75,38.182,0 12.761,38.181,0 12.767,38.162,0 12.791,38.117,0 12.819,38.078,0 12.829,38.07,0 12.858,38.058,0 12.869,38.051,0 12.87,38.042,0 12.902,38.028,0 12.945,38.033,0 13.028,38.062,0 13.062,38.083,0 13.07,38.091,0 13.072,38.095,0 13.07,38.101,0 13.069,38.114,0 13.067,38.123,0 13.057,38.133,0 13.055,38.142,0 13.09,38.166,0 13.084,38.174,0 13.09,38.183,0 13.102,38.19,0 13.113,38.193,0 13.123,38.191,0 13.158,38.179,0 13.18,38.176,0 13.208,38.176,0 13.231,38.184,0 13.239,38.207,0 13.255,38.202,0 13.267,38.205,0 13.278,38.21,0 13.297,38.214,0 13.311,38.219,0 13.319,38.22,0 13.324,38.218,0 13.326,38.211,0 13.327,38.205,0 13.329,38.2,0 13.367,38.179,0 13.372,38.173,0 13.374,38.14,0 13.377,38.131,0 13.392,38.103,0 13.514,38.11,0 13.542,38.094,0 13.54,38.077,0 13.542,38.067,0 13.548,38.056,0 13.558,38.049,0 13.588,38.039,0 13.623,38.015,0 13.652,38.001,0 13.698,37.993,0 13.712,37.988,0 13.708,37.985,0 13.708,37.984,0 13.706,37.98,0 13.727,37.981,0 13.791,37.973,0 13.813,37.978,0 13.858,37.996,0 13.899,38.004,0 13.913,38.012,0 13.925,38.022,0 13.939,38.029,0 14.008,38.038,0 14.021,38.049,0 14.063,38.03,0 14.084,38.024,0 14.107,38.021,0 14.122,38.022,0 14.152,38.029,0 14.274,38.015,0 14.332,38.018,0 14.385,38.029,0 14.433,38.049,0 14.465,38.037,0 14.512,38.044,0 14.635,38.081,0 14.668,38.099,0 14.696,38.121,0 14.734,38.157,0 14.745,38.161,0 14.778,38.159,0 14.799,38.16,0 14.875,38.175,0 14.889,38.182,0 14.898,38.186,0 14.908,38.187,0 14.936,38.186,0 14.945,38.182,0 14.963,38.163,0 14.97,38.159,0 14.982,38.158,0 15.008,38.152,0 15.04,38.153,0 15.049,38.152,0 15.054,38.148,0 15.064,38.135,0 15.069,38.131,0 15.088,38.128,0 15.106,38.133,0 15.123,38.141,0 15.178,38.156,0 15.204,38.183,0 15.241,38.241,0 15.238,38.249,0 15.237,38.251,0 15.237,38.253,0 15.241,38.261,0 15.238,38.265,0 15.244,38.265,0 15.247,38.254,0 15.241,38.23,0 15.246,38.217,0 15.258,38.21,0 15.275,38.207,0 15.292,38.207,0 15.322,38.211,0 15.4,38.232,0 15.423,38.244,0 15.434,38.253,0 15.473,38.268,0 15.513,38.297,0 15.529,38.302,0 15.56,38.3,0 15.616,38.28,0 15.652,38.275,0 15.649,38.266,0 15.643,38.262,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>14.999,38.371,0 14.987,38.364,0 14.964,38.381,0 14.949,38.396,0 14.946,38.412,0 14.96,38.433,0 14.967,38.433,0 14.967,38.418,0 14.983,38.412,0 14.994,38.403,0 15.002,38.391,0 15.008,38.378,0 14.999,38.371,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>14.967,38.453,0 14.949,38.451,0 14.935,38.458,0 14.922,38.469,0 14.908,38.474,0 14.9,38.481,0 14.901,38.498,0 14.91,38.515,0 14.925,38.522,0 14.958,38.522,0 14.967,38.516,0 14.96,38.502,0 14.966,38.497,0 14.975,38.49,0 14.98,38.487,0 14.98,38.481,0 14.953,38.481,0 14.958,38.469,0 14.962,38.465,0 14.967,38.461,0 14.967,38.453,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>14.361,38.539,0 14.346,38.535,0 14.343,38.547,0 14.357,38.551,0 14.361,38.539,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>14.864,38.549,0 14.862,38.539,0 14.824,38.552,0 14.794,38.571,0 14.815,38.584,0 14.852,38.585,0 14.867,38.581,0 14.877,38.569,0 14.873,38.565,0 14.869,38.56,0 14.864,38.549,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>14.585,38.557,0 14.574,38.557,0 14.552,38.562,0 14.544,38.575,0 14.543,38.587,0 14.546,38.588,0 14.564,38.585,0 14.576,38.577,0 14.58,38.566,0 14.585,38.561,0 14.585,38.557,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>13.177,38.693,0 13.165,38.691,0 13.153,38.695,0 13.153,38.702,0 13.158,38.71,0 13.169,38.717,0 13.186,38.718,0 13.196,38.711,0 13.197,38.708,0 13.177,38.693,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>15.225,38.777,0 15.217,38.773,0 15.206,38.775,0 15.187,38.789,0 15.187,38.793,0 15.194,38.798,0 15.204,38.802,0 15.209,38.806,0 15.212,38.81,0 15.219,38.812,0 15.228,38.81,0 15.235,38.808,0 15.239,38.804,0 15.237,38.796,0 15.232,38.789,0 15.23,38.783,0 15.225,38.777,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>8.361,39.118,0 8.386,39.105,0 8.418,39.106,0 8.445,39.102,0 8.457,39.073,0 8.459,39.068,0 8.464,39.065,0 8.47,39.065,0 8.477,39.07,0 8.478,39.07,0 8.48,39.072,0 8.484,39.07,0 8.465,39.056,0 8.46,39.05,0 8.464,39.042,0 8.455,39.028,0 8.447,38.994,0 8.438,38.967,0 8.433,38.963,0 8.422,38.96,0 8.41,38.962,0 8.407,38.967,0 8.406,38.974,0 8.402,38.981,0 8.365,39.029,0 8.35,39.062,0 8.354,39.083,0 8.354,39.091,0 8.347,39.091,0 8.347,39.097,0 8.361,39.118,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>8.306,39.104,0 8.291,39.099,0 8.27,39.1,0 8.255,39.107,0 8.258,39.118,0 8.258,39.124,0 8.233,39.144,0 8.225,39.157,0 8.231,39.173,0 8.246,39.181,0 8.291,39.188,0 8.306,39.193,0 8.307,39.161,0 8.313,39.12,0 8.306,39.104,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>13.959,40.712,0 13.945,40.701,0 13.935,40.705,0 13.92,40.704,0 13.904,40.7,0 13.891,40.694,0 13.882,40.699,0 13.86,40.707,0 13.85,40.715,0 13.857,40.735,0 13.862,40.744,0 13.871,40.749,0 13.868,40.752,0 13.863,40.762,0 13.884,40.762,0 13.947,40.745,0 13.966,40.735,0 13.963,40.729,0 13.963,40.723,0 13.966,40.715,0 13.959,40.712,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>13.427,40.791,0 13.415,40.786,0 13.419,40.796,0 13.424,40.8,0 13.432,40.801,0 13.427,40.791,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>8.333,41.105,0 8.343,41.098,0 8.345,41.086,0 8.342,41.074,0 8.333,41.064,0 8.275,41.057,0 8.252,41.043,0 8.252,41.016,0 8.247,40.993,0 8.21,40.996,0 8.218,41.005,0 8.222,41.014,0 8.224,41.024,0 8.224,41.033,0 8.229,41.042,0 8.242,41.052,0 8.261,41.064,0 8.276,41.07,0 8.278,41.081,0 8.276,41.095,0 8.278,41.105,0 8.285,41.107,0 8.303,41.105,0 8.306,41.109,0 8.309,41.114,0 8.314,41.118,0 8.327,41.126,0 8.326,41.118,0 8.328,41.112,0 8.333,41.105,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>9.471,41.19,0 9.474,41.184,0 9.475,41.179,0 9.47,41.172,0 9.464,41.173,0 9.456,41.181,0 9.449,41.186,0 9.442,41.183,0 9.437,41.186,0 9.448,41.205,0 9.443,41.211,0 9.446,41.22,0 9.454,41.234,0 9.46,41.242,0 9.468,41.241,0 9.475,41.236,0 9.478,41.228,0 9.48,41.224,0 9.479,41.217,0 9.471,41.19,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>9.239,41.249,0 9.247,41.248,0 9.258,41.249,0 9.269,41.236,0 9.268,41.202,0 9.279,41.195,0 9.275,41.199,0 9.274,41.205,0 9.275,41.212,0 9.279,41.221,0 9.286,41.221,0 9.29,41.209,0 9.289,41.205,0 9.286,41.201,0 9.286,41.195,0 9.3,41.196,0 9.306,41.198,0 9.313,41.201,0 9.317,41.196,0 9.334,41.187,0 9.336,41.211,0 9.353,41.207,0 9.389,41.181,0 9.389,41.187,0 9.397,41.184,0 9.405,41.181,0 9.413,41.181,0 9.423,41.181,0 9.423,41.174,0 9.417,41.171,0 9.415,41.168,0 9.413,41.164,0 9.409,41.16,0 9.421,41.156,0 9.427,41.149,0 9.433,41.14,0 9.443,41.133,0 9.438,41.125,0 9.437,41.115,0 9.443,41.092,0 9.455,41.112,0 9.461,41.12,0 9.471,41.126,0 9.467,41.13,0 9.466,41.134,0 9.463,41.137,0 9.457,41.14,0 9.47,41.146,0 9.482,41.145,0 9.495,41.142,0 9.509,41.14,0 9.514,41.143,0 9.519,41.148,0 9.524,41.15,0 9.533,41.14,0 9.525,41.133,0 9.535,41.128,0 9.541,41.123,0 9.547,41.121,0 9.553,41.126,0 9.56,41.126,0 9.562,41.122,0 9.562,41.121,0 9.564,41.121,0 9.567,41.119,0 9.566,41.107,0 9.563,41.097,0 9.557,41.088,0 9.546,41.077,0 9.544,41.082,0 9.541,41.087,0 9.54,41.092,0 9.522,41.031,0 9.512,41.016,0 9.533,41.016,0 9.525,41.03,0 9.544,41.037,0 9.555,41.034,0 9.558,41.025,0 9.553,41.009,0 9.558,41.009,0 9.559,41.011,0 9.559,41.013,0 9.56,41.016,0 9.566,41.011,0 9.569,41.009,0 9.574,41.009,0 9.589,41.02,0 9.616,41.019,0 9.645,41.011,0 9.663,41.002,0 9.652,40.991,0 9.637,40.992,0 9.62,40.999,0 9.605,41.002,0 9.588,40.996,0 9.583,40.98,0 9.579,40.962,0 9.567,40.948,0 9.572,40.935,0 9.558,40.931,0 9.512,40.934,0 9.512,40.929,0 9.513,40.928,0 9.505,40.927,0 9.512,40.915,0 9.521,40.915,0 9.53,40.919,0 9.54,40.92,0 9.55,40.917,0 9.568,40.908,0 9.574,40.906,0 9.593,40.91,0 9.608,40.918,0 9.623,40.924,0 9.643,40.92,0 9.638,40.911,0 9.632,40.905,0 9.624,40.9,0 9.615,40.899,0 9.615,40.893,0 9.651,40.879,0 9.656,40.876,0 9.658,40.864,0 9.664,40.858,0 9.672,40.859,0 9.684,40.865,0 9.69,40.856,0 9.7,40.85,0 9.712,40.847,0 9.725,40.845,0 9.691,40.836,0 9.682,40.829,0 9.69,40.817,0 9.69,40.811,0 9.675,40.814,0 9.662,40.809,0 9.658,40.8,0 9.669,40.79,0 9.67,40.801,0 9.676,40.788,0 9.705,40.759,0 9.711,40.745,0 9.715,40.727,0 9.745,40.68,0 9.749,40.667,0 9.754,40.605,0 9.757,40.595,0 9.762,40.587,0 9.769,40.584,0 9.782,40.582,0 9.786,40.576,0 9.787,40.567,0 9.793,40.557,0 9.821,40.536,0 9.827,40.529,0 9.827,40.519,0 9.816,40.502,0 9.813,40.492,0 9.809,40.471,0 9.801,40.455,0 9.779,40.427,0 9.762,40.39,0 9.75,40.377,0 9.728,40.372,0 9.713,40.366,0 9.701,40.353,0 9.684,40.324,0 9.671,40.312,0 9.646,40.296,0 9.635,40.282,0 9.627,40.263,0 9.625,40.248,0 9.629,40.205,0 9.632,40.196,0 9.655,40.144,0 9.666,40.131,0 9.68,40.126,0 9.688,40.12,0 9.711,40.096,0 9.733,40.084,0 9.731,40.068,0 9.694,39.993,0 9.688,39.961,0 9.697,39.934,0 9.703,39.937,0 9.71,39.94,0 9.716,39.94,0 9.718,39.934,0 9.715,39.924,0 9.709,39.922,0 9.702,39.922,0 9.697,39.919,0 9.69,39.906,0 9.685,39.894,0 9.684,39.882,0 9.69,39.871,0 9.684,39.871,0 9.684,39.865,0 9.688,39.863,0 9.693,39.86,0 9.697,39.858,0 9.697,39.852,0 9.685,39.84,0 9.676,39.819,0 9.671,39.793,0 9.669,39.769,0 9.67,39.756,0 9.676,39.732,0 9.677,39.718,0 9.675,39.708,0 9.665,39.691,0 9.663,39.677,0 9.661,39.67,0 9.656,39.663,0 9.652,39.652,0 9.65,39.639,0 9.656,39.594,0 9.654,39.567,0 9.629,39.502,0 9.645,39.484,0 9.64,39.452,0 9.615,39.399,0 9.603,39.355,0 9.601,39.341,0 9.604,39.326,0 9.612,39.316,0 9.635,39.303,0 9.635,39.297,0 9.608,39.289,0 9.582,39.266,0 9.568,39.238,0 9.574,39.214,0 9.566,39.205,0 9.569,39.199,0 9.577,39.194,0 9.581,39.187,0 9.578,39.179,0 9.569,39.159,0 9.567,39.149,0 9.558,39.139,0 9.54,39.134,0 9.523,39.125,0 9.519,39.104,0 9.511,39.108,0 9.508,39.111,0 9.508,39.116,0 9.512,39.124,0 9.497,39.133,0 9.481,39.135,0 9.466,39.132,0 9.451,39.124,0 9.443,39.124,0 9.439,39.133,0 9.429,39.138,0 9.409,39.146,0 9.384,39.169,0 9.378,39.173,0 9.368,39.177,0 9.346,39.196,0 9.337,39.201,0 9.327,39.203,0 9.313,39.208,0 9.3,39.214,0 9.293,39.221,0 9.286,39.214,0 9.272,39.22,0 9.253,39.225,0 9.217,39.228,0 9.198,39.221,0 9.182,39.207,0 9.17,39.193,0 9.167,39.187,0 9.137,39.194,0 9.114,39.211,0 9.073,39.248,0 9.064,39.243,0 9.056,39.247,0 9.048,39.256,0 9.039,39.262,0 9.025,39.265,0 9.015,39.264,0 9.013,39.26,0 9.026,39.256,0 9.026,39.248,0 9.022,39.24,0 9.027,39.236,0 9.036,39.232,0 9.038,39.227,0 9.039,39.228,0 9.051,39.225,0 9.075,39.23,0 9.08,39.224,0 9.08,39.216,0 9.08,39.212,0 9.039,39.179,0 9.027,39.165,0 9.019,39.146,0 9.017,39.124,0 9.019,39.104,0 9.025,39.086,0 9.033,39.07,0 9.038,39.063,0 9.044,39.058,0 9.046,39.051,0 9.03,39.03,0 9.019,38.995,0 9.026,38.995,0 9.016,38.989,0 9.013,38.99,0 9.005,38.995,0 8.997,38.983,0 8.895,38.902,0 8.889,38.9,0 8.878,38.899,0 8.873,38.896,0 8.862,38.882,0 8.854,38.878,0 8.842,38.88,0 8.828,38.889,0 8.806,38.906,0 8.806,38.885,0 8.791,38.904,0 8.767,38.92,0 8.74,38.93,0 8.717,38.932,0 8.695,38.925,0 8.669,38.91,0 8.652,38.891,0 8.656,38.871,0 8.641,38.864,0 8.635,38.871,0 8.643,38.89,0 8.634,38.895,0 8.616,38.896,0 8.6,38.899,0 8.6,38.906,0 8.616,38.923,0 8.616,38.947,0 8.604,38.965,0 8.581,38.96,0 8.573,39.013,0 8.56,39.057,0 8.553,39.057,0 8.545,39.051,0 8.521,39.061,0 8.505,39.063,0 8.51,39.068,0 8.519,39.083,0 8.505,39.091,0 8.483,39.08,0 8.483,39.084,0 8.478,39.09,0 8.474,39.107,0 8.466,39.119,0 8.455,39.125,0 8.443,39.118,0 8.439,39.128,0 8.439,39.153,0 8.436,39.166,0 8.429,39.173,0 8.419,39.177,0 8.413,39.175,0 8.416,39.166,0 8.41,39.169,0 8.406,39.174,0 8.403,39.181,0 8.402,39.19,0 8.399,39.201,0 8.393,39.204,0 8.386,39.204,0 8.381,39.207,0 8.373,39.222,0 8.372,39.23,0 8.377,39.238,0 8.427,39.283,0 8.433,39.302,0 8.416,39.323,0 8.418,39.339,0 8.383,39.359,0 8.375,39.379,0 8.379,39.388,0 8.396,39.404,0 8.402,39.412,0 8.406,39.427,0 8.404,39.436,0 8.39,39.462,0 8.387,39.465,0 8.387,39.47,0 8.395,39.481,0 8.422,39.508,0 8.436,39.525,0 8.452,39.558,0 8.464,39.577,0 8.457,39.584,0 8.465,39.598,0 8.463,39.617,0 8.45,39.659,0 8.447,39.704,0 8.443,39.714,0 8.443,39.721,0 8.447,39.731,0 8.445,39.757,0 8.447,39.762,0 8.46,39.76,0 8.469,39.755,0 8.5,39.716,0 8.518,39.702,0 8.539,39.696,0 8.566,39.701,0 8.515,39.713,0 8.505,39.721,0 8.507,39.738,0 8.521,39.755,0 8.536,39.771,0 8.546,39.783,0 8.539,39.783,0 8.536,39.776,0 8.531,39.77,0 8.525,39.766,0 8.519,39.762,0 8.53,39.772,0 8.541,39.789,0 8.549,39.807,0 8.553,39.821,0 8.556,39.852,0 8.554,39.864,0 8.546,39.878,0 8.524,39.899,0 8.495,39.912,0 8.464,39.914,0 8.436,39.899,0 8.443,39.893,0 8.446,39.898,0 8.45,39.899,0 8.456,39.898,0 8.464,39.899,0 8.452,39.893,0 8.445,39.883,0 8.436,39.858,0 8.429,39.865,0 8.438,39.877,0 8.432,39.885,0 8.419,39.892,0 8.404,39.903,0 8.401,39.903,0 8.399,39.905,0 8.395,39.912,0 8.394,39.92,0 8.397,39.927,0 8.4,39.933,0 8.402,39.94,0 8.394,39.977,0 8.395,39.988,0 8.407,40.01,0 8.408,40.022,0 8.395,40.036,0 8.381,40.03,0 8.378,40.033,0 8.385,40.042,0 8.402,40.05,0 8.405,40.049,0 8.435,40.051,0 8.453,40.056,0 8.46,40.057,0 8.469,40.062,0 8.48,40.074,0 8.488,40.089,0 8.491,40.104,0 8.486,40.118,0 8.468,40.144,0 8.464,40.163,0 8.46,40.216,0 8.477,40.262,0 8.477,40.292,0 8.463,40.314,0 8.442,40.331,0 8.416,40.345,0 8.409,40.338,0 8.387,40.352,0 8.384,40.372,0 8.395,40.424,0 8.391,40.442,0 8.38,40.468,0 8.366,40.492,0 8.35,40.502,0 8.332,40.51,0 8.324,40.531,0 8.32,40.555,0 8.313,40.578,0 8.292,40.595,0 8.268,40.594,0 8.217,40.57,0 8.196,40.578,0 8.206,40.598,0 8.217,40.612,0 8.194,40.617,0 8.177,40.606,0 8.167,40.586,0 8.162,40.564,0 8.154,40.578,0 8.148,40.593,0 8.141,40.619,0 8.141,40.625,0 8.158,40.632,0 8.174,40.641,0 8.186,40.656,0 8.189,40.68,0 8.192,40.68,0 8.196,40.685,0 8.198,40.691,0 8.193,40.694,0 8.18,40.695,0 8.174,40.697,0 8.168,40.701,0 8.154,40.719,0 8.146,40.726,0 8.134,40.729,0 8.21,40.865,0 8.216,40.881,0 8.217,40.899,0 8.21,40.914,0 8.193,40.92,0 8.179,40.928,0 8.183,40.945,0 8.194,40.963,0 8.203,40.975,0 8.21,40.975,0 8.213,40.963,0 8.221,40.962,0 8.229,40.962,0 8.237,40.955,0 8.236,40.946,0 8.232,40.934,0 8.23,40.921,0 8.234,40.91,0 8.278,40.865,0 8.311,40.85,0 8.422,40.839,0 8.478,40.826,0 8.501,40.824,0 8.521,40.827,0 8.599,40.853,0 8.619,40.866,0 8.635,40.881,0 8.641,40.896,0 8.71,40.92,0 8.734,40.921,0 8.752,40.919,0 8.765,40.914,0 8.823,40.947,0 8.84,40.961,0 8.876,41.008,0 8.889,41.016,0 8.887,41.02,0 8.887,41.021,0 8.886,41.022,0 8.882,41.023,0 8.914,41.032,0 8.923,41.037,0 8.93,41.043,0 8.941,41.061,0 8.947,41.064,0 8.959,41.07,0 8.976,41.082,0 8.991,41.097,0 9.006,41.122,0 9.025,41.129,0 9.094,41.135,0 9.108,41.139,0 9.136,41.16,0 9.142,41.153,0 9.158,41.169,0 9.164,41.184,0 9.163,41.225,0 9.172,41.243,0 9.191,41.251,0 9.213,41.256,0 9.231,41.262,0 9.233,41.253,0 9.239,41.249,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>9.435,41.217,0 9.395,41.211,0 9.377,41.213,0 9.373,41.222,0 9.373,41.23,0 9.378,41.234,0 9.385,41.237,0 9.392,41.241,0 9.396,41.248,0 9.398,41.256,0 9.402,41.258,0 9.408,41.258,0 9.414,41.262,0 9.422,41.261,0 9.427,41.254,0 9.431,41.246,0 9.43,41.238,0 9.429,41.229,0 9.431,41.225,0 9.434,41.221,0 9.435,41.217,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>10.316,42.341,0 10.313,42.324,0 10.294,42.328,0 10.297,42.345,0 10.306,42.352,0 10.316,42.341,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>10.922,42.334,0 10.909,42.325,0 10.874,42.36,0 10.862,42.366,0 10.871,42.376,0 10.877,42.387,0 10.884,42.392,0 10.896,42.386,0 10.907,42.378,0 10.919,42.356,0 10.931,42.346,0 10.926,42.339,0 10.922,42.334,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>10.095,42.577,0 10.086,42.572,0 10.072,42.573,0 10.059,42.576,0 10.05,42.582,0 10.053,42.589,0 10.063,42.592,0 10.073,42.6,0 10.08,42.614,0 10.084,42.615,0 10.088,42.604,0 10.092,42.596,0 10.096,42.591,0 10.098,42.588,0 10.098,42.584,0 10.095,42.577,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>10.431,42.816,0 10.437,42.804,0 10.431,42.787,0 10.421,42.776,0 10.407,42.769,0 10.389,42.763,0 10.408,42.757,0 10.426,42.741,0 10.431,42.722,0 10.416,42.709,0 10.411,42.718,0 10.404,42.719,0 10.394,42.718,0 10.382,42.722,0 10.378,42.728,0 10.368,42.746,0 10.365,42.75,0 10.352,42.755,0 10.338,42.765,0 10.326,42.765,0 10.314,42.743,0 10.305,42.76,0 10.266,42.744,0 10.246,42.757,0 10.241,42.742,0 10.236,42.736,0 10.23,42.735,0 10.148,42.737,0 10.125,42.743,0 10.107,42.757,0 10.102,42.784,0 10.112,42.801,0 10.134,42.812,0 10.159,42.817,0 10.18,42.819,0 10.19,42.817,0 10.213,42.808,0 10.225,42.804,0 10.243,42.803,0 10.266,42.804,0 10.266,42.809,0 10.265,42.81,0 10.263,42.81,0 10.26,42.812,0 10.273,42.819,0 10.273,42.826,0 10.273,42.827,0 10.29,42.825,0 10.327,42.826,0 10.323,42.811,0 10.333,42.806,0 10.348,42.806,0 10.355,42.808,0 10.359,42.817,0 10.366,42.823,0 10.375,42.827,0 10.382,42.832,0 10.393,42.858,0 10.401,42.869,0 10.413,42.873,0 10.422,42.871,0 10.432,42.864,0 10.439,42.855,0 10.444,42.845,0 10.437,42.838,0 10.432,42.828,0 10.431,42.816,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>9.844,43.06,0 9.848,43.058,0 9.854,43.059,0 9.843,43.035,0 9.828,43.019,0 9.81,43.017,0 9.793,43.037,0 9.812,43.071,0 9.827,43.081,0 9.841,43.065,0 9.842,43.063,0 9.844,43.06,0 </coordinates></LinearRing></outerBoundaryIs></Polygon><Polygon><outerBoundaryIs><LinearRing><coordinates>12.122,46.972,0 12.128,46.949,0 12.135,46.937,0 12.142,46.928,0 12.142,46.919,0 12.127,46.909,0 12.137,46.906,0 12.161,46.903,0 12.172,46.899,0 12.184,46.891,0 12.189,46.885,0 12.195,46.88,0 12.209,46.877,0 12.251,46.876,0 12.267,46.868,0 12.276,46.846,0 12.276,46.834,0 12.273,46.827,0 12.27,46.82,0 12.267,46.808,0 12.267,46.795,0 12.269,46.789,0 12.275,46.785,0 12.284,46.78,0 12.305,46.774,0 12.326,46.772,0 12.343,46.765,0 12.351,46.743,0 12.37,46.711,0 12.405,46.69,0 12.446,46.679,0 12.5,46.672,0 12.531,46.658,0 12.547,46.652,0 12.562,46.651,0 12.62,46.656,0 12.67,46.653,0 12.679,46.65,0 12.697,46.641,0 12.707,46.638,0 12.716,46.638,0 12.732,46.642,0 12.74,46.643,0 12.774,46.635,0 12.83,46.61,0 13.065,46.598,0 13.146,46.585,0 13.21,46.558,0 13.231,46.552,0 13.271,46.551,0 13.373,46.566,0 13.417,46.56,0 13.478,46.564,0 13.485,46.562,0 13.499,46.551,0 13.507,46.547,0 13.549,46.546,0 13.67,46.519,0 13.685,46.518,0 13.701,46.52,0 13.701,46.512,0 13.699,46.505,0 13.695,46.499,0 13.69,46.493,0 13.688,46.468,0 13.677,46.452,0 13.659,46.445,0 13.634,46.446,0 13.6,46.443,0 13.576,46.427,0 13.554,46.406,0 13.53,46.388,0 13.484,46.371,0 13.46,46.359,0 13.447,46.355,0 13.434,46.354,0 13.423,46.345,0 13.41,46.324,0 13.391,46.302,0 13.365,46.29,0 13.373,46.28,0 13.379,46.268,0 13.385,46.243,0 13.385,46.243,0 13.385,46.243,0 13.398,46.231,0 13.402,46.217,0 13.41,46.208,0 13.437,46.211,0 13.423,46.229,0 13.438,46.225,0 13.468,46.223,0 13.482,46.218,0 13.51,46.214,0 13.529,46.205,0 13.559,46.184,0 13.584,46.181,0 13.614,46.184,0 13.637,46.18,0 13.645,46.162,0 13.616,46.125,0 13.505,46.066,0 13.482,46.045,0 13.49,46.039,0 13.493,46.032,0 13.49,46.026,0 13.482,46.018,0 13.477,46.016,0 13.462,46.006,0 13.475,45.996,0 13.479,45.993,0 13.48,45.992,0 13.481,45.991,0 13.482,45.99,0 13.482,45.989,0 13.509,45.967,0 13.539,45.969,0 13.572,45.98,0 13.606,45.985,0 13.623,45.966,0 13.608,45.927,0 13.569,45.865,0 13.566,45.83,0 13.581,45.809,0 13.609,45.799,0 13.644,45.796,0 13.66,45.792,0 13.709,45.765,0 13.779,45.743,0 13.858,45.649,0 13.869,45.641,0 13.884,45.635,0 13.893,45.635,0 13.895,45.632,0 13.887,45.619,0 13.848,45.585,0 13.801,45.581,0 13.761,45.596,0 13.712,45.593,0 13.719,45.6,0 13.731,45.613,0 13.757,45.613,0 13.787,45.611,0 13.809,45.614,0 13.796,45.617,0 13.787,45.624,0 13.778,45.635,0 13.74,45.649,0 13.758,45.655,0 13.754,45.672,0 13.74,45.691,0 13.727,45.703,0 13.648,45.762,0 13.63,45.772,0 13.575,45.789,0 13.552,45.792,0 13.535,45.782,0 13.525,45.76,0 13.529,45.74,0 13.555,45.737,0 13.519,45.725,0 13.514,45.721,0 13.508,45.714,0 13.481,45.71,0 13.47,45.707,0 13.452,45.694,0 13.429,45.681,0 13.402,45.675,0 13.377,45.683,0 13.392,45.686,0 13.41,45.691,0 13.425,45.698,0 13.432,45.707,0 13.423,45.724,0 13.382,45.73,0 13.37,45.744,0 13.352,45.74,0 13.255,45.756,0 13.246,45.759,0 13.222,45.776,0 13.216,45.779,0 13.206,45.778,0 13.17,45.768,0 13.158,45.754,0 13.15,45.751,0 13.14,45.755,0 13.132,45.769,0 13.12,45.772,0 13.111,45.767,0 13.109,45.758,0 13.112,45.749,0 13.124,45.744,0 13.124,45.737,0 13.101,45.736,0 13.081,45.727,0 13.07,45.713,0 13.076,45.697,0 13.092,45.689,0 13.112,45.691,0 13.15,45.703,0 13.139,45.689,0 13.104,45.669,0 13.096,45.652,0 13.086,45.642,0 13.061,45.636,0 12.982,45.635,0 12.944,45.628,0 12.781,45.553,0 12.612,45.496,0 12.513,45.47,0 12.497,45.46,0 12.488,45.456,0 12.452,45.45,0 12.424,45.438,0 12.411,45.436,0 12.419,45.451,0 12.43,45.464,0 12.436,45.475,0 12.431,45.484,0 12.441,45.483,0 12.448,45.484,0 12.452,45.489,0 12.452,45.498,0 12.459,45.498,0 12.463,45.489,0 12.468,45.485,0 12.472,45.486,0 12.479,45.491,0 12.466,45.504,0 12.477,45.503,0 12.488,45.504,0 12.498,45.506,0 12.5,45.504,0 12.501,45.506,0 12.504,45.503,0 12.507,45.499,0 12.507,45.498,0 12.504,45.498,0 12.493,45.498,0 12.493,45.491,0 12.516,45.492,0 12.521,45.505,0 12.522,45.519,0 12.531,45.525,0 12.549,45.527,0 12.563,45.531,0 12.574,45.54,0 12.582,45.553,0 12.57,45.549,0 12.545,45.536,0 12.538,45.536,0 12.519,45.55,0 12.511,45.559,0 12.507,45.573,0 12.486,45.565,0 12.459,45.548,0 12.443,45.53,0 12.452,45.518,0 12.452,45.512,0 12.435,45.512,0 12.418,45.523,0 12.411,45.518,0 12.404,45.518,0 12.397,45.539,0 12.385,45.523,0 12.391,45.514,0 12.425,45.504,0 12.425,45.498,0 12.412,45.493,0 12.394,45.491,0 12.381,45.494,0 12.384,45.504,0 12.351,45.505,0 12.31,45.489,0 12.273,45.463,0 12.253,45.436,0 12.253,45.43,0 12.259,45.43,0 12.251,45.42,0 12.247,45.411,0 12.249,45.402,0 12.259,45.395,0 12.25,45.385,0 12.248,45.378,0 12.249,45.371,0 12.246,45.361,0 12.238,45.358,0 12.229,45.357,0 12.224,45.354,0 12.233,45.34,0 12.221,45.327,0 12.217,45.316,0 12.209,45.309,0 12.188,45.306,0 12.175,45.31,0 12.164,45.316,0 12.155,45.313,0 12.15,45.292,0 12.16,45.283,0 12.169,45.262,0 12.181,45.258,0 12.192,45.263,0 12.2,45.274,0 12.203,45.288,0 12.198,45.299,0 12.218,45.294,0 12.222,45.283,0 12.221,45.269,0 12.225,45.251,0 12.214,45.248,0 12.212,45.243,0 12.216,45.237,0 12.225,45.23,0 12.222,45.216,0 12.231,45.204,0 12.248,45.197,0 12.267,45.196,0 12.264,45.2,0 12.263,45.201,0 12.259,45.203,0 12.274,45.211,0 12.296,45.226,0 12.308,45.23,0 12.299,45.215,0 12.305,45.201,0 12.316,45.186,0 12.322,45.172,0 12.322,45.139,0 12.329,45.101,0 12.319,45.103,0 12.308,45.108,0 12.309,45.114,0 12.308,45.124,0 12.308,45.128,0 12.298,45.106,0 12.297,45.088,0 12.307,45.078,0 12.329,45.08,0 12.326,45.083,0 12.324,45.086,0 12.322,45.093,0 12.341,45.081,0 12.354,45.067,0 12.364,45.052,0 12.377,45.039,0 12.377,45.032,0 12.369,45.031,0 12.365,45.029,0 12.361,45.027,0 12.356,45.024,0 12.369,45.011,0 12.384,45.026,0 12.387,45.039,0 12.381,45.051,0 12.369,45.065,0 12.384,45.056,0 12.402,45.05,0 12.414,45.043,0 12.411,45.032,0 12.427,45.02,0 12.435,45.015,0 12.445,45.011,0 12.465,44.992,0 12.487,44.976,0 12.5,44.983,0 12.497,44.984,0 12.49,44.983,0 12.487,44.983,0 12.487,44.991,0 12.503,44.991,0 12.517,44.987,0 12.528,44.98,0 12.535,44.97,0 12.534,44.961,0 12.524,44.95,0 12.528,44.943,0 12.519,44.934,0 12.516,44.928,0 12.513,44.922,0 12.507,44.922,0 12.5,44.921,0 12.495,44.91,0 12.493,44.878,0 12.488,44.862,0 12.475,44.845,0 12.445,44.82,0 12.444,44.825,0 12.439,44.835,0 12.433,44.846,0 12.425,44.854,0 12.44,44.877,0 12.444,44.89,0 12.439,44.901,0 12.427,44.905,0 12.416,44.9,0 12.407,44.891,0 12.404,44.884,0 12.393,44.868,0 12.392,44.859,0 12.417,44.851,0 12.416,44.843,0 12.409,44.836,0 12.397,44.833,0 12.397,44.826,0 12.404,44.825,0 12.417,44.821,0 12.425,44.82,0 12.417,44.803,0 12.398,44.794,0 12.376,44.792,0 12.358,44.804,0 12.347,44.815,0 12.322,44.833,0 12.304,44.843,0 12.293,44.843,0 12.267,44.826,0 12.267,44.82,0 12.281,44.82,0 12.254,44.751,0 12.247,44.711,0 12.253,44.668,0 12.266,44.636,0 12.276,44.62,0 12.284,44.614,0 12.286,44.602,0 12.281,44.532,0 12.284,44.487,0 12.315,44.387,0 12.319,44.361,0 12.322,44.353,0 12.326,44.348,0 12.34,44.334,0 12.343,44.329,0 12.345,44.308,0 12.351,44.288,0 12.369,44.25,0 12.391,44.222,0 12.418,44.195,0 12.459,44.166,0 12.479,44.139,0 12.511,44.114,0 12.548,44.093,0 12.575,44.085,0 12.632,44.03,0 12.662,44.008,0 12.692,43.99,0 12.711,43.983,0 12.757,43.972,0 12.804,43.967,0 12.823,43.958,0 12.863,43.935,0 12.929,43.916,0 12.939,43.904,0 12.948,43.897,0 13.254,43.703,0 13.371,43.65,0 13.39,43.644,0 13.4,43.635,0 13.447,43.623,0 13.474,43.612,0 13.484,43.616,0 13.491,43.623,0 13.497,43.627,0 13.5,43.628,0 13.502,43.63,0 13.505,43.633,0 13.511,43.633,0 13.517,43.631,0 13.52,43.627,0 13.522,43.622,0 13.525,43.62,0 13.544,43.613,0 13.558,43.596,0 13.57,43.58,0 13.579,43.573,0 13.599,43.569,0 13.616,43.56,0 13.625,43.547,0 13.618,43.531,0 13.761,43.264,0 13.777,43.243,0 13.781,43.236,0 13.787,43.2,0 13.791,43.192,0 13.803,43.178,0 13.835,43.127,0 13.849,43.092,0 13.866,43.007,0 13.945,42.798,0 13.981,42.73,0 14.002,42.698,0 14.064,42.625,0 14.069,42.609,0 14.076,42.599,0 14.221,42.47,0 14.285,42.428,0 14.357,42.393,0 14.388,42.373,0 14.43,42.321,0 14.561,42.225,0 14.596,42.208,0 14.654,42.191,0 14.694,42.185,0 14.71,42.175,0 14.718,42.16,0 14.723,42.119,0 14.73,42.099,0 14.741,42.084,0 14.758,42.079,0 14.781,42.075,0 14.8,42.066,0 14.836,42.044,0 14.871,42.032,0 14.953,42.021,0 14.994,42.01,0 15.008,42.001,0 15.035,41.974,0 15.046,41.969,0 15.064,41.964,0 15.105,41.942,0 15.124,41.934,0 15.166,41.927,0 15.282,41.928,0 15.401,41.908,0 15.447,41.907,0 15.612,41.928,0 15.775,41.921,0 16.028,41.944,0 16.112,41.928,0 16.112,41.926,0 16.141,41.92,0 16.161,41.892,0 16.18,41.893,0 16.177,41.877,0 16.184,41.858,0 16.193,41.821,0 16.194,41.808,0 16.193,41.791,0 16.185,41.779,0 16.167,41.763,0 16.146,41.749,0 16.128,41.742,0 16.108,41.737,0 16.09,41.726,0 16.064,41.701,0 16.028,41.68,0 15.926,41.64,0 15.901,41.614,0 15.892,41.577,0 15.897,41.536,0 15.912,41.503,0 15.934,41.479,0 15.962,41.459,0 16.022,41.428,0 16.086,41.412,0 16.101,41.403,0 16.115,41.393,0 16.302,41.328,0 16.461,41.262,0 16.521,41.25,0 16.539,41.239,0 16.555,41.227,0 16.594,41.207,0 16.831,41.146,0 16.852,41.133,0 16.859,41.133,0 16.859,41.14,0 16.865,41.14,0 16.886,41.124,0 17.058,41.082,0 17.204,41.021,0 17.277,40.98,0 17.311,40.955,0 17.348,40.912,0 17.362,40.906,0 17.378,40.902,0 17.414,40.881,0 17.476,40.83,0 17.493,40.824,0 17.513,40.82,0 17.549,40.802,0 17.635,40.785,0 17.646,40.78,0 17.749,40.747,0 17.844,40.694,0 17.922,40.683,0 17.956,40.67,0 17.956,40.647,0 17.967,40.647,0 17.993,40.653,0 18.008,40.65,0 18.012,40.644,0 18.012,40.635,0 18.016,40.625,0 18.04,40.608,0 18.044,40.602,0 18.038,40.557,0 18.12,40.504,0 18.212,40.464,0 18.232,40.461,0 18.239,40.457,0 18.259,40.43,0 18.271,40.421,0 18.304,40.4,0 18.33,40.366,0 18.344,40.351,0 18.362,40.345,0 18.371,40.338,0 18.438,40.268,0 18.501,40.152,0 18.505,40.146,0 18.51,40.142,0 18.517,40.139,0 18.512,40.127,0 18.514,40.12,0 18.518,40.114,0 18.517,40.104,0 18.509,40.094,0 18.492,40.084,0 18.484,40.055,0 18.471,40.043,0 18.435,40.022,0 18.412,39.979,0 18.408,39.968,0 18.405,39.947,0 18.395,39.925,0 18.393,39.916,0 18.4,39.89,0 18.401,39.878,0 18.387,39.825,0 18.39,39.817,0 18.384,39.814,0 18.374,39.8,0 18.369,39.796,0 18.347,39.798,0 18.339,39.8,0 18.331,39.803,0 18.283,39.833,0 18.266,39.837,0 18.225,39.837,0 18.212,39.839,0 18.187,39.852,0 18.162,39.86,0 18.131,39.883,0 18.095,39.903,0 18.082,39.906,0 18.072,39.911,0 18.008,39.986,0 17.996,39.995,0 17.996,40.002,0 18.012,40.003,0 18.021,40.01,0 18.023,40.021,0 18.016,40.036,0 18.006,40.045,0 17.979,40.051,0 17.968,40.057,0 18.003,40.074,0 18.012,40.096,0 17.998,40.12,0 17.968,40.146,0 17.941,40.163,0 17.927,40.176,0 17.92,40.191,0 17.92,40.21,0 17.917,40.227,0 17.912,40.24,0 17.9,40.249,0 17.913,40.249,0 17.913,40.255,0 17.864,40.285,0 17.848,40.29,0 17.513,40.303,0 17.494,40.307,0 17.441,40.331,0 17.431,40.331,0 17.41,40.33,0 17.4,40.331,0 17.393,40.335,0 17.375,40.348,0 17.369,40.351,0 17.352,40.355,0 17.297,40.379,0 17.241,40.395,0 17.213,40.406,0 17.201,40.42,0 17.224,40.428,0 17.244,40.441,0 17.248,40.457,0 17.228,40.474,0 17.248,40.48,0 17.296,40.473,0 17.317,40.482,0 17.324,40.498,0 17.305,40.499,0 17.262,40.488,0 17.264,40.491,0 17.269,40.496,0 17.248,40.503,0 17.23,40.497,0 17.211,40.487,0 17.191,40.482,0 17.182,40.485,0 17.177,40.493,0 17.172,40.502,0 17.167,40.509,0 17.157,40.512,0 17.134,40.512,0 17.125,40.515,0 17.05,40.519,0 16.977,40.492,0 16.913,40.445,0 16.783,40.301,0 16.762,40.269,0 16.738,40.211,0 16.731,40.2,0 16.716,40.193,0 16.68,40.146,0 16.625,40.108,0 16.605,40.084,0 16.597,40.046,0 16.6,40.034,0 16.614,39.996,0 16.632,39.966,0 16.622,39.953,0 16.606,39.943,0 16.59,39.92,0 16.543,39.885,0 16.509,39.837,0 16.492,39.805,0 16.49,39.775,0 16.503,39.747,0 16.529,39.721,0 16.529,39.714,0 16.516,39.689,0 16.546,39.661,0 16.592,39.636,0 16.625,39.625,0 16.75,39.62,0 16.783,39.611,0 16.799,39.603,0 16.817,39.591,0 16.831,39.576,0 16.838,39.56,0 16.847,39.552,0 16.906,39.529,0 16.954,39.499,0 16.971,39.495,0 16.996,39.492,0 17.012,39.486,0 17.024,39.475,0 17.036,39.461,0 17.058,39.441,0 17.089,39.422,0 17.125,39.409,0 17.159,39.406,0 17.123,39.338,0 17.115,39.283,0 17.115,39.269,0 17.118,39.256,0 17.125,39.244,0 17.143,39.222,0 17.146,39.21,0 17.141,39.179,0 17.123,39.121,0 17.125,39.091,0 17.148,39.054,0 17.152,39.046,0 17.159,39.04,0 17.193,39.031,0 17.207,39.029,0 17.187,39.019,0 17.177,39.012,0 17.173,39.005,0 17.172,38.966,0 17.173,38.96,0 17.139,38.936,0 17.136,38.932,0 17.128,38.929,0 17.119,38.919,0 17.105,38.899,0 17.096,38.919,0 17.071,38.923,0 17.043,38.916,0 17.023,38.906,0 16.997,38.929,0 16.982,38.937,0 16.958,38.94,0 16.936,38.938,0 16.839,38.918,0 16.728,38.879,0 16.688,38.856,0 16.68,38.847,0 16.671,38.84,0 16.611,38.816,0 16.586,38.798,0 16.575,38.785,0 16.564,38.756,0 16.551,38.741,0 16.539,38.723,0 16.535,38.7,0 16.547,38.693,0 16.55,38.69,0 16.549,38.672,0 16.559,38.596,0 16.578,38.528,0 16.578,38.503,0 16.57,38.429,0 16.562,38.416,0 16.523,38.387,0 16.509,38.371,0 16.498,38.369,0 16.468,38.348,0 16.436,38.34,0 16.34,38.301,0 16.307,38.277,0 16.17,38.143,0 16.152,38.111,0 16.126,38.005,0 16.112,37.973,0 16.102,37.96,0 16.091,37.949,0 16.078,37.94,0 16.064,37.932,0 16.016,37.924,0 16.002,37.919,0 15.943,37.933,0 15.762,37.925,0 15.736,37.931,0 15.709,37.941,0 15.685,37.953,0 15.666,37.967,0 15.646,37.988,0 15.636,38.009,0 15.639,38.027,0 15.659,38.042,0 15.633,38.074,0 15.625,38.092,0 15.628,38.107,0 15.642,38.126,0 15.648,38.143,0 15.647,38.162,0 15.639,38.186,0 15.633,38.22,0 15.651,38.241,0 15.685,38.253,0 15.787,38.278,0 15.796,38.285,0 15.799,38.291,0 15.813,38.3,0 15.817,38.306,0 15.83,38.351,0 15.905,38.474,0 15.918,38.517,0 15.916,38.55,0 15.901,38.578,0 15.871,38.604,0 15.864,38.608,0 15.851,38.613,0 15.845,38.618,0 15.836,38.628,0 15.834,38.634,0 15.836,38.639,0 15.837,38.649,0 15.845,38.66,0 15.864,38.668,0 15.905,38.679,0 15.969,38.712,0 16.003,38.725,0 16.049,38.728,0 16.121,38.721,0 16.137,38.724,0 16.153,38.731,0 16.18,38.748,0 16.201,38.776,0 16.216,38.814,0 16.222,38.856,0 16.221,38.899,0 16.215,38.919,0 16.205,38.934,0 16.19,38.943,0 16.169,38.947,0 16.155,38.955,0 16.14,38.974,0 16.084,39.075,0 16.043,39.31,0 16.032,39.345,0 15.955,39.489,0 15.934,39.513,0 15.905,39.536,0 15.877,39.551,0 15.868,39.564,0 15.865,39.588,0 15.851,39.615,0 15.837,39.652,0 15.816,39.679,0 15.807,39.695,0 15.789,39.796,0 15.789,39.79,0 15.784,39.81,0 15.779,39.82,0 15.772,39.824,0 15.77,39.83,0 15.783,39.868,0 15.775,39.891,0 15.742,39.929,0 15.735,39.943,0 15.729,39.964,0 15.714,39.981,0 15.679,40.009,0 15.652,40.043,0 15.631,40.057,0 15.625,40.065,0 15.625,40.078,0 15.611,40.073,0 15.536,40.078,0 15.51,40.07,0 15.493,40.059,0 15.46,40.029,0 15.425,40.004,0 15.405,39.999,0 15.377,40.002,0 15.354,40.012,0 15.315,40.034,0 15.303,40.036,0 15.294,40.032,0 15.284,40.03,0 15.273,40.028,0 15.262,40.029,0 15.262,40.036,0 15.28,40.047,0 15.264,40.074,0 15.234,40.1,0 15.21,40.112,0 15.191,40.119,0 15.128,40.169,0 15.113,40.175,0 15.096,40.173,0 15.066,40.166,0 15.048,40.169,0 15.035,40.175,0 15.015,40.194,0 14.974,40.223,0 14.967,40.224,0 14.959,40.231,0 14.923,40.238,0 14.912,40.241,0 14.907,40.258,0 14.932,40.285,0 14.94,40.307,0 14.933,40.324,0 14.933,40.334,0 14.943,40.338,0 14.954,40.34,0 14.965,40.345,0 14.973,40.352,0 14.98,40.359,0 14.99,40.394,0 14.976,40.431,0 14.889,40.573,0 14.862,40.607,0 14.836,40.632,0 14.81,40.653,0 14.783,40.67,0 14.753,40.676,0 14.72,40.667,0 14.691,40.649,0 14.679,40.646,0 14.626,40.649,0 14.614,40.646,0 14.572,40.617,0 14.545,40.613,0 14.517,40.62,0 14.487,40.632,0 14.472,40.624,0 14.423,40.615,0 14.402,40.602,0 14.356,40.583,0 14.343,40.57,0 14.331,40.584,0 14.329,40.605,0 14.338,40.624,0 14.36,40.632,0 14.38,40.634,0 14.388,40.637,0 14.395,40.65,0 14.403,40.657,0 14.471,40.699,0 14.48,40.711,0 14.475,40.729,0 14.461,40.744,0 14.443,40.755,0 14.426,40.762,0 14.415,40.765,0 14.399,40.767,0 14.391,40.77,0 14.385,40.774,0 14.372,40.787,0 14.367,40.79,0 14.349,40.797,0 14.313,40.828,0 14.295,40.839,0 14.276,40.84,0 14.249,40.837,0 14.224,40.831,0 14.213,40.821,0 14.204,40.801,0 14.182,40.8,0 14.112,40.829,0 14.096,40.834,0 14.083,40.831,0 14.077,40.822,0 14.078,40.81,0 14.082,40.797,0 14.083,40.783,0 14.075,40.788,0 14.041,40.798,0 14.053,40.837,0 14.044,40.875,0 13.966,40.996,0 13.931,41.014,0 13.918,41.023,0 13.915,41.033,0 13.913,41.054,0 13.911,41.064,0 13.885,41.104,0 13.786,41.203,0 13.722,41.252,0 13.709,41.256,0 13.679,41.25,0 13.664,41.25,0 13.657,41.259,0 13.595,41.253,0 13.564,41.238,0 13.576,41.208,0 13.544,41.206,0 13.535,41.208,0 13.526,41.215,0 13.52,41.225,0 13.515,41.229,0 13.508,41.221,0 13.5,41.221,0 13.481,41.239,0 13.325,41.295,0 13.286,41.295,0 13.205,41.284,0 13.187,41.278,0 13.152,41.26,0 13.115,41.251,0 13.091,41.226,0 13.069,41.221,0 13.045,41.227,0 13.037,41.24,0 13.034,41.257,0 13.024,41.273,0 13.013,41.286,0 12.993,41.315,0 12.98,41.331,0 12.924,41.379,0 12.894,41.399,0 12.863,41.413,0 12.842,41.418,0 12.764,41.421,0 12.749,41.423,0 12.679,41.458,0 12.655,41.465,0 12.643,41.458,0 12.636,41.447,0 12.62,41.459,0 12.546,41.544,0 12.449,41.63,0 12.343,41.702,0 12.328,41.711,0 12.301,41.717,0 12.286,41.727,0 12.277,41.729,0 12.247,41.733,0 12.24,41.736,0 12.224,41.75,0 12.216,41.768,0 12.212,41.787,0 12.212,41.808,0 12.207,41.827,0 12.195,41.847,0 12.171,41.879,0 12.148,41.903,0 12.05,41.96,0 12.039,41.965,0 12.03,41.973,0 12.027,41.986,0 12.021,41.993,0 11.993,41.996,0 11.983,42,0 11.97,42.011,0 11.953,42.022,0 11.935,42.031,0 11.917,42.038,0 11.84,42.036,0 11.828,42.034,0 11.823,42.047,0 11.81,42.066,0 11.794,42.084,0 11.78,42.092,0 11.772,42.106,0 11.751,42.128,0 11.746,42.136,0 11.744,42.152,0 11.737,42.169,0 11.683,42.252,0 11.659,42.279,0 11.54,42.349,0 11.49,42.359,0 11.421,42.386,0 11.397,42.393,0 11.397,42.4,0 11.387,42.404,0 11.377,42.407,0 11.366,42.408,0 11.355,42.407,0 11.363,42.4,0 11.334,42.4,0 11.26,42.421,0 11.246,42.422,0 11.228,42.422,0 11.212,42.419,0 11.205,42.411,0 11.201,42.395,0 11.187,42.379,0 11.185,42.366,0 11.175,42.369,0 11.165,42.369,0 11.158,42.368,0 11.157,42.366,0 11.148,42.371,0 11.135,42.384,0 11.107,42.391,0 11.095,42.402,0 11.087,42.418,0 11.081,42.435,0 11.1,42.443,0 11.123,42.446,0 11.167,42.448,0 11.175,42.458,0 11.184,42.48,0 11.19,42.504,0 11.188,42.521,0 11.167,42.546,0 11.159,42.564,0 11.149,42.563,0 11.138,42.559,0 11.129,42.558,0 11.117,42.572,0 11.108,42.591,0 11.098,42.607,0 11.081,42.612,0 11.078,42.632,0 11.054,42.647,0 11.006,42.668,0 11.001,42.68,0 10.996,42.696,0 10.99,42.71,0 10.982,42.716,0 10.973,42.72,0 10.944,42.743,0 10.891,42.764,0 10.732,42.804,0 10.756,42.819,0 10.766,42.835,0 10.767,42.854,0 10.766,42.877,0 10.769,42.884,0 10.775,42.888,0 10.778,42.894,0 10.774,42.908,0 10.764,42.918,0 10.751,42.925,0 10.682,42.949,0 10.633,42.958,0 10.584,42.959,0 10.54,42.949,0 10.544,42.939,0 10.547,42.935,0 10.519,42.925,0 10.5,42.94,0 10.478,42.99,0 10.503,43.005,0 10.518,43.024,0 10.54,43.079,0 10.536,43.091,0 10.536,43.112,0 10.54,43.134,0 10.547,43.147,0 10.539,43.164,0 10.535,43.185,0 10.533,43.226,0 10.529,43.246,0 10.517,43.267,0 10.438,43.388,0 10.374,43.453,0 10.36,43.465,0 10.327,43.477,0 10.318,43.492,0 10.295,43.568,0 10.265,43.809,0 10.252,43.846,0 10.211,43.92,0 10.181,43.955,0 10.137,43.978,0 10.106,44.016,0 10.091,44.025,0 10.073,44.029,0 10.036,44.048,0 10.015,44.052,0 9.999,44.058,0 9.989,44.06,0 9.985,44.055,0 9.981,44.05,0 9.973,44.045,0 9.963,44.044,0 9.954,44.048,0 9.938,44.06,0 9.905,44.08,0 9.888,44.093,0 9.877,44.088,0 9.845,44.108,0 9.827,44.107,0 9.834,44.1,0 9.829,44.098,0 9.825,44.095,0 9.82,44.093,0 9.825,44.085,0 9.831,44.079,0 9.839,44.075,0 9.848,44.072,0 9.848,44.066,0 9.842,44.063,0 9.839,44.06,0 9.834,44.052,0 9.847,44.046,0 9.843,44.041,0 9.833,44.042,0 9.827,44.055,0 9.82,44.063,0 9.772,44.079,0 9.722,44.113,0 9.71,44.118,0 9.683,44.136,0 9.673,44.141,0 9.644,44.142,0 9.632,44.144,0 9.622,44.148,0 9.587,44.178,0 9.581,44.179,0 9.573,44.191,0 9.557,44.2,0 9.512,44.215,0 9.5,44.222,0 9.49,44.231,0 9.485,44.244,0 9.473,44.24,0 9.454,44.237,0 9.437,44.239,0 9.43,44.247,0 9.423,44.257,0 9.375,44.272,0 9.368,44.294,0 9.263,44.336,0 9.231,44.353,0 9.222,44.344,0 9.214,44.333,0 9.21,44.321,0 9.211,44.305,0 9.166,44.318,0 9.147,44.328,0 9.149,44.34,0 9.131,44.363,0 9.103,44.374,0 9.002,44.387,0 8.953,44.4,0 8.924,44.411,0 8.915,44.409,0 8.869,44.409,0 8.846,44.413,0 8.838,44.417,0 8.828,44.428,0 8.763,44.432,0 8.738,44.429,0 8.725,44.424,0 8.696,44.406,0 8.686,44.398,0 8.679,44.394,0 8.671,44.394,0 8.663,44.395,0 8.656,44.394,0 8.594,44.363,0 8.577,44.36,0 8.565,44.357,0 8.541,44.34,0 8.467,44.304,0 8.445,44.284,0 8.45,44.264,0 8.44,44.253,0 8.437,44.247,0 8.436,44.24,0 8.433,44.238,0 8.418,44.23,0 8.412,44.227,0 8.407,44.215,0 8.409,44.204,0 8.409,44.193,0 8.395,44.182,0 8.37,44.173,0 8.314,44.16,0 8.285,44.148,0 8.27,44.138,0 8.257,44.128,0 8.234,44.103,0 8.231,44.096,0 8.232,44.08,0 8.231,44.072,0 8.224,44.057,0 8.217,44.045,0 8.17,44.006,0 8.153,43.983,0 8.168,43.962,0 8.168,43.956,0 8.145,43.952,0 8.116,43.927,0 8.09,43.92,0 8.082,43.915,0 8.076,43.909,0 8.073,43.904,0 8.068,43.896,0 8.056,43.892,0 8.032,43.887,0 7.96,43.853,0 7.786,43.822,0 7.737,43.798,0 7.695,43.791,0 7.573,43.791,0 7.545,43.784,0 7.532,43.784,0 7.524,43.789,0 7.513,43.792,0 7.503,43.792,0 7.483,43.84,0 7.478,43.866,0 7.493,43.886,0 7.537,43.921,0 7.557,43.944,0 7.609,43.976,0 7.631,43.994,0 7.639,44.005,0 7.647,44.027,0 7.653,44.04,0 7.664,44.049,0 7.679,44.057,0 7.69,44.067,0 7.692,44.085,0 7.676,44.109,0 7.654,44.125,0 7.642,44.144,0 7.656,44.176,0 7.625,44.18,0 7.584,44.161,0 7.555,44.159,0 7.381,44.123,0 7.341,44.124,0 7.331,44.125,0 7.322,44.132,0 7.316,44.14,0 7.309,44.147,0 7.296,44.151,0 7.27,44.154,0 7.251,44.16,0 7.145,44.207,0 7.105,44.218,0 7.046,44.24,0 7.033,44.243,0 7.02,44.242,0 7.008,44.239,0 6.996,44.238,0 6.983,44.242,0 6.973,44.249,0 6.969,44.258,0 6.966,44.268,0 6.959,44.277,0 6.95,44.285,0 6.93,44.295,0 6.921,44.302,0 6.916,44.31,0 6.904,44.33,0 6.896,44.34,0 6.874,44.358,0 6.87,44.363,0 6.866,44.372,0 6.866,44.377,0 6.869,44.383,0 6.877,44.414,0 6.884,44.423,0 6.918,44.436,0 6.892,44.452,0 6.861,44.475,0 6.839,44.503,0 6.836,44.534,0 6.846,44.547,0 6.897,44.575,0 6.932,44.618,0 6.946,44.625,0 6.934,44.647,0 6.941,44.667,0 6.96,44.683,0 6.983,44.692,0 7.001,44.692,0 7.037,44.685,0 7.055,44.685,0 7.049,44.698,0 7.019,44.739,0 7.015,44.747,0 7.01,44.772,0 6.998,44.794,0 6.999,44.795,0 7.004,44.811,0 7.006,44.812,0 7.006,44.816,0 7.007,44.819,0 7.007,44.822,0 7.005,44.828,0 7.001,44.833,0 6.983,44.847,0 6.933,44.862,0 6.915,44.863,0 6.866,44.856,0 6.847,44.859,0 6.778,44.888,0 6.745,44.908,0 6.728,44.929,0 6.73,44.985,0 6.723,45.013,0 6.697,45.027,0 6.662,45.029,0 6.652,45.036,0 6.64,45.05,0 6.637,45.059,0 6.638,45.067,0 6.637,45.074,0 6.62,45.084,0 6.603,45.103,0 6.615,45.115,0 6.633,45.126,0 6.667,45.14,0 6.676,45.141,0 6.694,45.14,0 6.702,45.141,0 6.711,45.145,0 6.729,45.155,0 6.736,45.157,0 6.771,45.153,0 6.808,45.139,0 6.844,45.13,0 6.877,45.141,0 6.879,45.147,0 6.873,45.152,0 6.868,45.157,0 6.873,45.166,0 6.881,45.168,0 6.905,45.169,0 6.914,45.17,0 6.928,45.18,0 6.946,45.201,0 6.959,45.21,0 6.994,45.221,0 7.03,45.228,0 7.038,45.226,0 7.05,45.215,0 7.055,45.214,0 7.062,45.219,0 7.081,45.243,0 7.108,45.259,0 7.108,45.275,0 7.098,45.295,0 7.093,45.324,0 7.098,45.33,0 7.13,45.357,0 7.151,45.383,0 7.16,45.398,0 7.161,45.411,0 7.153,45.415,0 7.11,45.428,0 7.097,45.435,0 7.089,45.447,0 7.082,45.459,0 7.072,45.47,0 7.028,45.493,0 6.983,45.511,0 6.975,45.526,0 6.97,45.567,0 6.966,45.574,0 6.955,45.586,0 6.953,45.594,0 6.956,45.603,0 6.967,45.62,0 6.969,45.626,0 6.963,45.641,0 6.951,45.647,0 6.919,45.653,0 6.905,45.66,0 6.883,45.676,0 6.869,45.679,0 6.843,45.683,0 6.816,45.697,0 6.796,45.718,0 6.785,45.76,0 6.782,45.777,0 6.783,45.795,0 6.788,45.812,0 6.801,45.826,0 6.816,45.833,0 6.846,45.836,0 6.846,45.838,0 6.849,45.842,0 6.853,45.847,0 6.858,45.849,0 6.862,45.849,0 6.87,45.845,0 6.873,45.845,0 6.88,45.846,0 6.905,45.845,0 6.926,45.85,0 6.949,45.858,0 6.969,45.87,0 6.983,45.886,0 6.989,45.899,0 6.997,45.911,0 7.008,45.921,0 7.022,45.925,0 7.067,45.89,0 7.09,45.881,0 7.121,45.876,0 7.154,45.877,0 7.184,45.88,0 7.245,45.898,0 7.274,45.91,0 7.287,45.913,0 7.362,45.908,0 7.394,45.916,0 7.453,45.946,0 7.483,45.955,0 7.504,45.957,0 7.515,45.967,0 7.524,45.978,0 7.541,45.984,0 7.643,45.966,0 7.659,45.96,0 7.674,45.95,0 7.693,45.931,0 7.694,45.929,0 7.706,45.926,0 7.715,45.927,0 7.722,45.93,0 7.732,45.93,0 7.78,45.918,0 7.808,45.918,0 7.825,45.915,0 7.831,45.914,0 7.844,45.919,0 7.846,45.923,0 7.845,45.928,0 7.848,45.938,0 7.872,45.969,0 7.898,45.982,0 7.969,45.993,0 7.979,45.995,0 7.986,45.999,0 7.998,46.011,0 7.999,46.013,0 8.009,46.028,0 8.011,46.03,0 8.016,46.058,0 8.016,46.069,0 8.018,46.081,0 8.025,46.091,0 8.035,46.097,0 8.056,46.098,0 8.067,46.101,0 8.111,46.127,0 8.132,46.159,0 8.13,46.196,0 8.1,46.236,0 8.077,46.25,0 8.073,46.254,0 8.077,46.262,0 8.087,46.272,0 8.107,46.286,0 8.128,46.292,0 8.172,46.299,0 8.193,46.309,0 8.242,46.354,0 8.27,46.364,0 8.282,46.37,0 8.291,46.378,0 8.297,46.388,0 8.297,46.398,0 8.29,46.401,0 8.287,46.405,0 8.295,46.418,0 8.316,46.434,0 8.343,46.444,0 8.399,46.452,0 8.428,46.449,0 8.442,46.435,0 8.446,46.412,0 8.446,46.382,0 8.443,46.353,0 8.427,46.302,0 8.423,46.276,0 8.427,46.251,0 8.438,46.235,0 8.457,46.225,0 8.483,46.218,0 8.51,46.208,0 8.539,46.188,0 8.602,46.123,0 8.612,46.119,0 8.631,46.115,0 8.677,46.096,0 8.695,46.095,0 8.702,46.098,0 8.718,46.108,0 8.724,46.11,0 8.732,46.107,0 8.739,46.098,0 8.747,46.094,0 8.763,46.093,0 8.794,46.093,0 8.809,46.09,0 8.834,46.066,0 8.82,46.043,0 8.791,46.019,0 8.773,45.991,0 8.77,45.986,0 8.768,45.983,0 8.785,45.982,0 8.8,45.979,0 8.858,45.957,0 8.864,45.953,0 8.871,45.947,0 8.881,45.931,0 8.898,45.91,0 8.907,45.896,0 8.912,45.883,0 8.914,45.866,0 8.91,45.854,0 8.904,45.842,0 8.9,45.826,0 8.94,45.835,0 8.972,45.825,0 9.002,45.821,0 9.034,45.848,0 9.059,45.882,0 9.063,45.899,0 9.052,45.916,0 9.042,45.92,0 9.021,45.923,0 9.011,45.927,0 9.002,45.936,0 8.993,45.954,0 8.983,45.962,0 8.981,45.964,0 8.98,45.967,0 8.981,45.969,0 8.983,45.972,0 9.016,45.993,0 8.998,46.028,0 9.002,46.039,0 9.028,46.053,0 9.05,46.058,0 9.059,46.062,0 9.067,46.071,0 9.07,46.083,0 9.068,46.106,0 9.072,46.119,0 9.091,46.138,0 9.163,46.172,0 9.171,46.183,0 9.176,46.194,0 9.181,46.204,0 9.192,46.21,0 9.204,46.214,0 9.216,46.221,0 9.225,46.231,0 9.24,46.267,0 9.269,46.309,0 9.275,46.331,0 9.274,46.344,0 9.26,46.38,0 9.26,46.394,0 9.263,46.407,0 9.261,46.417,0 9.248,46.423,0 9.238,46.437,0 9.246,46.461,0 9.263,46.485,0 9.282,46.497,0 9.331,46.502,0 9.351,46.498,0 9.352,46.485,0 9.377,46.469,0 9.385,46.466,0 9.395,46.469,0 9.4,46.475,0 9.404,46.483,0 9.411,46.489,0 9.427,46.497,0 9.435,46.498,0 9.438,46.492,0 9.444,46.396,0 9.442,46.381,0 9.444,46.375,0 9.452,46.37,0 9.474,46.362,0 9.483,46.357,0 9.503,46.321,0 9.515,46.309,0 9.536,46.299,0 9.56,46.293,0 9.674,46.292,0 9.693,46.297,0 9.708,46.312,0 9.709,46.32,0 9.707,46.331,0 9.709,46.342,0 9.72,46.351,0 9.731,46.351,0 9.755,46.341,0 9.768,46.339,0 9.789,46.343,0 9.855,46.367,0 9.899,46.372,0 9.918,46.371,0 9.939,46.367,0 9.964,46.356,0 9.971,46.34,0 9.971,46.32,0 9.978,46.298,0 9.992,46.284,0 10.032,46.26,0 10.042,46.243,0 10.043,46.22,0 10.076,46.22,0 10.118,46.231,0 10.146,46.243,0 10.159,46.262,0 10.146,46.28,0 10.105,46.309,0 10.096,46.321,0 10.092,46.329,0 10.092,46.338,0 10.097,46.352,0 10.105,46.361,0 10.126,46.374,0 10.133,46.381,0 10.141,46.403,0 10.133,46.414,0 10.116,46.419,0 10.071,46.425,0 10.042,46.433,0 10.026,46.446,0 10.044,46.467,0 10.035,46.471,0 10.03,46.477,0 10.028,46.484,0 10.027,46.493,0 10.031,46.504,0 10.031,46.526,0 10.033,46.533,0 10.041,46.542,0 10.063,46.557,0 10.071,46.564,0 10.083,46.597,0 10.088,46.604,0 10.097,46.608,0 10.192,46.627,0 10.218,46.627,0 10.234,46.618,0 10.236,46.607,0 10.23,46.586,0 10.235,46.575,0 10.276,46.566,0 10.284,46.561,0 10.289,46.556,0 10.295,46.551,0 10.307,46.547,0 10.319,46.546,0 10.354,46.548,0 10.426,46.535,0 10.444,46.538,0 10.458,46.554,0 10.466,46.578,0 10.467,46.604,0 10.459,46.624,0 10.438,46.636,0 10.396,46.639,0 10.378,46.653,0 10.369,46.672,0 10.374,46.682,0 10.385,46.689,0 10.394,46.701,0 10.397,46.715,0 10.396,46.726,0 10.4,46.736,0 10.417,46.743,0 10.429,46.756,0 10.426,46.769,0 10.419,46.784,0 10.417,46.799,0 10.439,46.817,0 10.445,46.823,0 10.449,46.832,0 10.454,46.864,0 10.486,46.846,0 10.528,46.843,0 10.629,46.862,0 10.647,46.864,0 10.662,46.861,0 10.739,46.83,0 10.749,46.819,0 10.744,46.813,0 10.722,46.8,0 10.717,46.795,0 10.723,46.786,0 10.734,46.786,0 10.755,46.791,0 10.766,46.788,0 10.795,46.777,0 10.805,46.777,0 10.824,46.78,0 10.834,46.78,0 10.843,46.777,0 10.86,46.767,0 10.87,46.764,0 10.88,46.765,0 10.914,46.772,0 10.931,46.774,0 10.966,46.772,0 10.983,46.768,0 10.997,46.769,0 11.011,46.779,0 11.033,46.806,0 11.037,46.808,0 11.049,46.812,0 11.053,46.815,0 11.055,46.82,0 11.053,46.83,0 11.054,46.834,0 11.073,46.865,0 11.084,46.9,0 11.092,46.912,0 11.157,46.957,0 11.174,46.964,0 11.244,46.979,0 11.314,46.987,0 11.349,46.982,0 11.381,46.972,0 11.411,46.97,0 11.445,46.993,0 11.445,46.993,0 11.453,47.001,0 11.462,47.006,0 11.472,47.007,0 11.489,47.004,0 11.496,47.002,0 11.502,46.998,0 11.507,46.993,0 11.515,46.989,0 11.524,46.988,0 11.534,46.99,0 11.543,46.993,0 11.543,46.993,0 11.544,46.993,0 11.544,46.993,0 11.573,46.999,0 11.596,47,0 11.648,46.993,0 11.648,46.993,0 11.65,46.993,0 11.657,46.993,0 11.665,46.993,0 11.684,46.992,0 11.716,46.975,0 11.735,46.971,0 11.746,46.972,0 11.766,46.983,0 11.777,46.988,0 11.823,46.993,0 11.857,47.012,0 11.9,47.028,0 11.944,47.038,0 12.015,47.04,0 12.116,47.077,0 12.181,47.085,0 12.204,47.08,0 12.204,47.053,0 12.182,47.034,0 12.122,47.011,0 12.111,46.993,0 12.118,46.983,0 12.122,46.972,0 </coordinates></LinearRing></outerBoundaryIs><innerBoundaryIs><LinearRing><coordinates>12.4,43.903,0 12.429,43.892,0 12.461,43.895,0 12.479,43.917,0 12.478,43.92,0 12.478,43.923,0 12.48,43.926,0 12.483,43.929,0 12.49,43.939,0 12.492,43.956,0 12.489,43.973,0 12.482,43.983,0 12.453,43.979,0 12.421,43.967,0 12.396,43.948,0 12.386,43.925,0 12.4,43.903,0 </coordinates></LinearRing></innerBoundaryIs><innerBoundaryIs><LinearRing><coordinates>12.444,41.902,0 12.449,41.9,0 12.455,41.9,0 12.458,41.902,0 12.455,41.908,0 12.447,41.907,0 12.444,41.902,0 </coordinates></LinearRing></innerBoundaryIs></Polygon></MultiGeometry>
        </Placemark> </kml>"""

        k = kml.KML()
        k.from_string(doc)
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(list(k.features())[0].geometry, MultiPolygon))
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_atom(self):
        pass

    def test_schema(self):
        doc = """<Schema name="TrailHeadType" id="TrailHeadTypeId">
            <SimpleField type="string" name="TrailHeadName">
              <displayName><![CDATA[<b>Trail Head Name</b>]]></displayName>
            </SimpleField>
            <SimpleField type="double" name="TrailLength">
              <displayName><![CDATA[<i>The length in miles</i>]]></displayName>
            </SimpleField>
            <SimpleField type="int" name="ElevationGain">
              <displayName><![CDATA[<i>change in altitude</i>]]></displayName>
            </SimpleField>
          </Schema> """

        s = kml.Schema(ns='', id='default')
        s.from_string(doc)
        self.assertEqual(len(list(s.simple_fields)), 3)
        self.assertEqual(list(s.simple_fields)[0]['type'], 'string')
        self.assertEqual(list(s.simple_fields)[1]['type'], 'double')
        self.assertEqual(list(s.simple_fields)[2]['type'], 'int')
        self.assertEqual(list(s.simple_fields)[0]['name'], 'TrailHeadName')
        self.assertEqual(list(s.simple_fields)[1]['name'], 'TrailLength')
        self.assertEqual(list(s.simple_fields)[2]['name'], 'ElevationGain')
        self.assertEqual(list(s.simple_fields)[0][
            'displayName'
        ], '<b>Trail Head Name</b>')
        self.assertEqual(list(s.simple_fields)[1][
            'displayName'
        ], '<i>The length in miles</i>')
        self.assertEqual(list(s.simple_fields)[2][
            'displayName'
        ], '<i>change in altitude</i>')
        s1 = kml.Schema(ns='', id='default')
        s1.from_string(s.to_string())
        self.assertEqual(len(list(s1.simple_fields)), 3)
        self.assertEqual(list(s1.simple_fields)[0]['type'], 'string')
        self.assertEqual(list(s1.simple_fields)[1]['name'], 'TrailLength')
        self.assertEqual(list(s1.simple_fields)[2][
            'displayName'
        ], '<i>change in altitude</i>')
        self.assertEqual(s.to_string(), s1.to_string())
        doc1 = """<kml xmlns="http://www.opengis.net/kml/2.2">
            <Document>
            %s
        </Document>
        </kml>""" % doc
        k = kml.KML()
        k.from_string(doc1)
        d = list(k.features())[0]
        s2 = list(d.schemata())[0]
        s.ns = config.NS
        self.assertEqual(s.to_string(), s2.to_string())
        k1 = kml.KML()
        k1.from_string(k.to_string())
        self.assertTrue('Schema' in k1.to_string())
        self.assertTrue('SimpleField' in k1.to_string())
        self.assertEqual(k1.to_string(), k.to_string())

    def test_schema_data(self):
        doc = """<SchemaData schemaUrl="#TrailHeadTypeId">
          <SimpleData name="TrailHeadName">Pi in the sky</SimpleData>
          <SimpleData name="TrailLength">3.14159</SimpleData>
          <SimpleData name="ElevationGain">10</SimpleData>
        </SchemaData>"""

        sd = kml.SchemaData(ns='', schema_url='#default')
        sd.from_string(doc)
        self.assertEqual(sd.schema_url, '#TrailHeadTypeId')
        self.assertEqual(
            sd.data[0], {'name': 'TrailHeadName',
                         'value': 'Pi in the sky'})
        self.assertEqual(
            sd.data[1], {'name': 'TrailLength',
                         'value': '3.14159'})
        self.assertEqual(sd.data[2], {'name': 'ElevationGain', 'value': '10'})
        sd1 = kml.SchemaData(ns='', schema_url='#default')
        sd1.from_string(sd.to_string())
        self.assertEqual(sd1.schema_url, '#TrailHeadTypeId')
        self.assertEqual(sd.to_string(), sd1.to_string())

    def test_snippet(self):
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
        <Snippet maxLines="2" >Short Desc</Snippet>
        </Placemark> </kml>"""

        k = kml.KML()
        k.from_string(doc)
        self.assertEqual(list(k.features())[0].snippet['text'], 'Short Desc')
        self.assertEqual(list(k.features())[0].snippet['maxLines'], 2)
        list(k.features())[0]._snippet['maxLines'] = 3
        self.assertEqual(list(k.features())[0].snippet['maxLines'], 3)
        self.assertTrue('maxLines="3"' in k.to_string())
        list(k.features())[0].snippet = {'text': 'Annother Snippet'}
        self.assertFalse('maxLines' in k.to_string())
        self.assertTrue('Annother Snippet' in k.to_string())
        list(k.features())[0].snippet = 'Diffrent Snippet'
        self.assertFalse('maxLines' in k.to_string())
        self.assertTrue('Diffrent Snippet' in k.to_string())

    def test_from_wrong_string(self):
        doc = kml.KML()
        self.assertRaises(TypeError, doc.from_string, '<xml></xml>')

    def test_address(self):
        doc = kml.Document()

        doc.from_string("""
        <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2" id="pm-id">
            <kml:name>pm-name</kml:name>
            <kml:description>pm-description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:address>1600 Amphitheatre Parkway, Mountain View, CA 94043, USA</kml:address>
        </kml:Document>
        """)

        doc2 = kml.Document()
        doc2.from_string(doc.to_string())
        self.assertEqual(doc.to_string(), doc2.to_string())

    def test_phone_number(self):
        doc = kml.Document()

        doc.from_string("""
        <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2" id="pm-id">
            <kml:name>pm-name</kml:name>
            <kml:description>pm-description</kml:description>
            <kml:visibility>1</kml:visibility>
            <kml:phoneNumber>+1 234 567 8901</kml:phoneNumber>
        </kml:Document>
        """)

        doc2 = kml.Document()
        doc2.from_string(doc.to_string())
        self.assertEqual(doc.to_string(), doc2.to_string())

    def test_groundoverlay(self):
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
                    <href>http://developers.google.com/kml/documentation/images/etna.jpg</href>
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
            """)

        doc2 = kml.KML()
        doc2.from_string(doc.to_string())
        self.assertEqual(doc.to_string(), doc2.to_string())

    def test_linarring_placemark(self):
        doc = kml.KML()
        doc.from_string( """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Placemark>
          <LinearRing>
            <coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,0.0</coordinates>
          </LinearRing>
        </Placemark> </kml>""")
        doc2 = kml.KML()
        doc2.from_string(doc.to_string())
        self.assertTrue(
            isinstance(list(doc.features())[0].geometry, LinearRing))
        self.assertEqual(doc.to_string(), doc2.to_string())


class StyleTestCase(unittest.TestCase):

    def test_styleurl(self):
        f = kml.Document()
        f.styleUrl = '#somestyle'
        self.assertEqual(f.styleUrl, '#somestyle')
        self.assertTrue(isinstance(f._styleUrl, styles.StyleUrl))
        s = styles.StyleUrl(config.NS, url='#otherstyle')
        f.styleUrl = s
        self.assertTrue(isinstance(f._styleUrl, styles.StyleUrl))
        self.assertEqual(f.styleUrl, '#otherstyle')
        f2 = kml.Document()
        f2.from_string(f.to_string())
        self.assertEqual(f.to_string(), f2.to_string())

    def test_style(self):
        lstyle = styles.LineStyle(color='red', width=2.0)
        style = styles.Style(styles=[lstyle])
        f = kml.Document(styles=[style])
        f2 = kml.Document()
        f2.from_string(f.to_string(prettyprint=True))
        self.assertEqual(f.to_string(), f2.to_string())

    def test_polystyle_fill(self):
        style = styles.PolyStyle()

    def test_polystyle_outline(self):
        style = styles.PolyStyle()


class StyleUsageTestCase(unittest.TestCase):

    def test_create_document_style(self):
        style = styles.Style(styles=[styles.PolyStyle(color='7f000000')])

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

        self.assertEqual(doc.to_string(), doc2.to_string())
        self.assertEqual(doc2.to_string(), doc3.to_string())
        self.assertEqual(doc.to_string(), doc3.to_string())

    def test_create_placemark_style(self):
        style = styles.Style(styles=[styles.PolyStyle(color='7f000000')])

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
        self.assertEqual(place.to_string(), place2.to_string())
        self.assertEqual(place2.to_string(), place3.to_string())
        self.assertEqual(place.to_string(), place3.to_string())


class StyleFromStringTestCase(unittest.TestCase):

    def test_styleurl(self):
        doc = """<kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
          <name>Document.kml</name>
          <open>1</open>
          <styleUrl>#default</styleUrl>
        </Document>
        </kml>"""

        k = kml.KML()
        k.from_string(doc)
        self.assertEqual(len(list(k.features())), 1)
        self.assertEqual(list(k.features())[0].styleUrl, '#default')
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_balloonstyle(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(list(list(k.features())[0].styles())[0], styles.Style))
        style = list(list(list(k.features())[0].styles())[0].styles())[0]
        self.assertTrue(isinstance(style, styles.BalloonStyle))
        self.assertEqual(style.bgColor, 'ffffffbb')
        self.assertEqual(style.textColor, 'ff000000')
        self.assertEqual(style.displayMode, 'default')
        self.assertTrue('$[geDirections]' in style.text)
        self.assertTrue('$[description]' in style.text)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k2.to_string(), k.to_string())

    def test_balloonstyle_old_color(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(list(list(k.features())[0].styles())[0], styles.Style))
        style = list(list(list(k.features())[0].styles())[0].styles())[0]
        self.assertTrue(isinstance(style, styles.BalloonStyle))
        self.assertEqual(style.bgColor, 'ffffffbb')
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k2.to_string(), k.to_string())



    def test_labelstyle(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(list(list(k.features())[0].styles())[0], styles.Style))
        style = list(list(list(k.features())[0].styles())[0].styles())[0]
        self.assertTrue(isinstance(style, styles.LabelStyle))
        self.assertEqual(style.color, 'ff0000cc')
        self.assertEqual(style.colorMode, None)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_iconstyle(self):
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
        self.assertEqual(len(list((k.features()))), 1)
        self.assertTrue(
            isinstance(list(list(k.features())[0].styles())[0], styles.Style))
        style = list(list(list(k.features())[0].styles())[0].styles())[0]
        self.assertTrue(isinstance(style, styles.IconStyle))
        self.assertEqual(style.color, 'ff00ff00')
        self.assertEqual(style.scale, 1.1)
        self.assertEqual(style.colorMode, 'random')
        self.assertEqual(style.heading, 0.0)
        self.assertEqual(style.icon_href, 'http://maps.google.com/icon21.png')
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_linestyle(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(list(list(k.features())[0].styles())[0], styles.Style))
        style = list(list(list(k.features())[0].styles())[0].styles())[0]
        self.assertTrue(isinstance(style, styles.LineStyle))
        self.assertEqual(style.color, '7f0000ff')
        self.assertEqual(style.width, 4)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_polystyle(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(list(list(k.features())[0].styles())[0], styles.Style))
        style = list(list(list(k.features())[0].styles())[0].styles())[0]
        self.assertTrue(isinstance(style, styles.PolyStyle))
        self.assertEqual(style.color, 'ff0000cc')
        self.assertEqual(style.colorMode, 'random')
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_polystyle_float_fill(self):
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
        style = list(list(list(k.features())[0].styles())[0].styles())[0]
        self.assertTrue(isinstance(style, styles.PolyStyle))
        self.assertEqual(style.fill, 0)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_polystyle_float_outline(self):
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
        style = list(list(list(k.features())[0].styles())[0].styles())[0]
        self.assertTrue(isinstance(style, styles.PolyStyle))
        self.assertEqual(style.outline, 0)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_styles(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(list(list(k.features())[0].styles())[0], styles.Style))
        style = list(list(list(k.features())[0].styles())[0].styles())
        self.assertEqual(len(style), 4)
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_stylemapurl(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(
                list(list(k.features())[0].styles())[0], styles.StyleMap))
        sm = list(list(list(k.features())[0].styles()))[0]
        self.assertTrue(isinstance(sm.normal, styles.StyleUrl))
        self.assertEqual(sm.normal.url, '#normalState')
        self.assertTrue(isinstance(sm.highlight, styles.StyleUrl))
        self.assertEqual(sm.highlight.url, '#highlightState')
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_stylemapstyles(self):
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
        self.assertEqual(len(list(k.features())), 1)
        self.assertTrue(
            isinstance(
                list(list(k.features())[0].styles())[0], styles.StyleMap))
        sm = list(list(list(k.features())[0].styles()))[0]
        self.assertTrue(isinstance(sm.normal, styles.Style))
        self.assertEqual(len(list(sm.normal.styles())), 1)
        self.assertTrue(
            isinstance(list(sm.normal.styles())[0], styles.LabelStyle))
        self.assertTrue(isinstance(sm.highlight, styles.Style))
        self.assertTrue(isinstance(sm.highlight, styles.Style))
        self.assertEqual(len(list(sm.highlight.styles())), 2)
        self.assertTrue(
            isinstance(list(sm.highlight.styles())[0], styles.LineStyle))
        self.assertTrue(
            isinstance(list(sm.highlight.styles())[1], styles.PolyStyle))
        k2 = kml.KML()
        k2.from_string(k.to_string())
        self.assertEqual(k.to_string(), k2.to_string())

    def test_get_style_by_url(self):
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
        self.assertEqual(len(list(k.features())), 1)
        document = list(k.features())[0]
        style = document.get_style_by_url(
            'http://localhost:8080/somepath#exampleStyleDocument')
        self.assertTrue(isinstance(list(style.styles())[0], styles.LabelStyle))
        style = document.get_style_by_url('somepath#linestyleExample')
        self.assertTrue(isinstance(list(style.styles())[0], styles.LineStyle))
        style = document.get_style_by_url('#styleMapExample')
        self.assertTrue(isinstance(style, styles.StyleMap))


class DateTimeTestCase(unittest.TestCase):

    def test_timestamp(self):
        now = datetime.datetime.now()
        ts = kml.TimeStamp(timestamp=now)
        self.assertEqual(ts.timestamp, [now, 'dateTime'])
        self.assertTrue('TimeStamp>' in str(ts.to_string()))
        self.assertTrue('when>' in str(ts.to_string()))
        self.assertTrue(now.isoformat() in str(ts.to_string()))
        y2k = datetime.date(2000, 1, 1)
        ts = kml.TimeStamp(timestamp=y2k)
        self.assertEqual(ts.timestamp, [y2k, 'date'])
        self.assertTrue('2000-01-01' in str(ts.to_string()))

    def test_timestamp_resolution(self):
        now = datetime.datetime.now()
        ts = kml.TimeStamp(timestamp=now)
        self.assertTrue(now.isoformat() in str(ts.to_string()))
        ts.timestamp[1] = 'date'
        self.assertTrue(now.date().isoformat() in str(ts.to_string()))
        self.assertFalse(now.isoformat() in str(ts.to_string()))
        year = str(now.year)
        ym = now.strftime('%Y-%m')
        ts.timestamp[1] = 'gYearMonth'
        self.assertTrue(ym in str(ts.to_string()))
        self.assertFalse(now.date().isoformat() in str(ts.to_string()))
        ts.timestamp[1] = 'gYear'
        self.assertTrue(year in str(ts.to_string()))
        self.assertFalse(ym in str(ts.to_string()))
        ts.timestamp = None
        self.assertRaises(TypeError, ts.to_string)

    def test_timespan(self):
        now = datetime.datetime.now()
        y2k = datetime.datetime(2000, 1, 1)
        ts = kml.TimeSpan(end=now, begin=y2k)
        self.assertEqual(ts.end, [now, 'dateTime'])
        self.assertEqual(ts.begin, [y2k, 'dateTime'])
        self.assertTrue('TimeSpan>' in str(ts.to_string()))
        self.assertTrue('begin>' in str(ts.to_string()))
        self.assertTrue('end>' in str(ts.to_string()))
        self.assertTrue(now.isoformat() in str(ts.to_string()))
        self.assertTrue(y2k.isoformat() in str(ts.to_string()))
        ts.end = None
        self.assertFalse(now.isoformat() in str(ts.to_string()))
        self.assertTrue(y2k.isoformat() in str(ts.to_string()))
        ts.begin = None
        self.assertRaises(ValueError, ts.to_string)

    def test_feature_timestamp(self):
        now = datetime.datetime.now()
        f = kml.Document()
        f.timeStamp = now
        self.assertEqual(f.timeStamp, now)
        self.assertTrue(now.isoformat() in str(f.to_string()))
        self.assertTrue('TimeStamp>' in str(f.to_string()))
        self.assertTrue('when>' in str(f.to_string()))
        f.timeStamp = now.date()
        self.assertTrue(now.date().isoformat() in str(f.to_string()))
        self.assertFalse(now.isoformat() in str(f.to_string()))
        f.timeStamp = None
        self.assertFalse('TimeStamp>' in str(f.to_string()))

    def test_feature_timespan(self):
        now = datetime.datetime.now()
        y2k = datetime.date(2000, 1, 1)
        f = kml.Document()
        f.begin = y2k
        f.end = now
        self.assertEqual(f.begin, y2k)
        self.assertEqual(f.end, now)
        self.assertTrue(now.isoformat() in str(f.to_string()))
        self.assertTrue('2000-01-01' in str(f.to_string()))
        self.assertTrue('TimeSpan>' in str(f.to_string()))
        self.assertTrue('begin>' in str(f.to_string()))
        self.assertTrue('end>' in str(f.to_string()))
        f.end = None
        self.assertFalse(now.isoformat() in str(f.to_string()))
        self.assertTrue('2000-01-01' in str(f.to_string()))
        self.assertTrue('TimeSpan>' in str(f.to_string()))
        self.assertTrue('begin>' in str(f.to_string()))
        self.assertFalse('end>' in str(f.to_string()))
        f.begin = None
        self.assertFalse('TimeSpan>' in str(f.to_string()))

    def test_feature_timespan_stamp(self):
        now = datetime.datetime.now()
        y2k = datetime.date(2000, 1, 1)
        f = kml.Document()
        f.begin = y2k
        f.end = now
        self.assertTrue(now.isoformat() in str(f.to_string()))
        self.assertTrue('2000-01-01' in str(f.to_string()))
        self.assertTrue('TimeSpan>' in str(f.to_string()))
        self.assertTrue('begin>' in str(f.to_string()))
        self.assertTrue('end>' in str(f.to_string()))
        self.assertFalse('TimeStamp>' in str(f.to_string()))
        self.assertFalse('when>' in str(f.to_string()))
        # when we set a timestamp an existing timespan will be deleted
        f.timeStamp = now
        self.assertTrue(now.isoformat() in str(f.to_string()))
        self.assertTrue('TimeStamp>' in str(f.to_string()))
        self.assertTrue('when>' in str(f.to_string()))
        self.assertFalse('2000-01-01' in str(f.to_string()))
        self.assertFalse('TimeSpan>' in str(f.to_string()))
        self.assertFalse('begin>' in str(f.to_string()))
        self.assertFalse('end>' in str(f.to_string()))
        # when we set a timespan an existing timestamp will be deleted
        f.end = y2k
        self.assertFalse(now.isoformat() in str(f.to_string()))
        self.assertTrue('2000-01-01' in str(f.to_string()))
        self.assertTrue('TimeSpan>' in str(f.to_string()))
        self.assertFalse('begin>' in str(f.to_string()))
        self.assertTrue('end>' in str(f.to_string()))
        self.assertFalse('TimeStamp>' in str(f.to_string()))
        self.assertFalse('when>' in str(f.to_string()))
        # We manipulate our Feature so it has timespan and stamp
        ts = kml.TimeStamp(timestamp=now)
        f._time_stamp = ts
        # this raises an exception as only either timespan or timestamp
        # are allowed not both
        self.assertRaises(ValueError, f.to_string)

    def test_read_timestamp(self):
        ts = kml.TimeStamp(ns='')
        doc = """
        <TimeStamp>
          <when>1997</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        self.assertEqual(ts.timestamp[1], 'gYear')
        self.assertEqual(ts.timestamp[0], datetime.datetime(1997, 1, 1, 0, 0))
        doc = """
        <TimeStamp>
          <when>1997-07</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        self.assertEqual(ts.timestamp[1], 'gYearMonth')
        self.assertEqual(ts.timestamp[0], datetime.datetime(1997, 7, 1, 0, 0))
        doc = """
        <TimeStamp>
          <when>199808</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        self.assertEqual(ts.timestamp[1], 'gYearMonth')
        self.assertEqual(ts.timestamp[0], datetime.datetime(1998, 8, 1, 0, 0))
        doc = """
        <TimeStamp>
          <when>1997-07-16</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        self.assertEqual(ts.timestamp[1], 'date')
        self.assertEqual(ts.timestamp[0], datetime.datetime(1997, 7, 16, 0, 0))
        # dateTime (YYYY-MM-DDThh:mm:ssZ)
        # Here, T is the separator between the calendar and the hourly notation
        # of time, and Z indicates UTC. (Seconds are required.)
        doc = """
        <TimeStamp>
          <when>1997-07-16T07:30:15Z</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        self.assertEqual(ts.timestamp[1], 'dateTime')
        self.assertEqual(ts.timestamp[0], datetime.datetime(
            1997, 7, 16, 7, 30, 15,
            tzinfo=tzutc()))
        doc = """
        <TimeStamp>
          <when>1997-07-16T10:30:15+03:00</when>
        </TimeStamp>
        """

        ts.from_string(doc)
        self.assertEqual(ts.timestamp[1], 'dateTime')
        self.assertEqual(ts.timestamp[0], datetime.datetime(
            1997, 7, 16, 10, 30, 15,
            tzinfo=tzoffset(None, 10800)))

    def test_read_timespan(self):
        ts = kml.TimeSpan(ns='')
        doc = """
        <TimeSpan>
            <begin>1876-08-01</begin>
            <end>1997-07-16T07:30:15Z</end>
        </TimeSpan>
        """

        ts.from_string(doc)
        self.assertEqual(ts.begin[1], 'date')
        self.assertEqual(ts.begin[0], datetime.datetime(1876, 8, 1, 0, 0))
        self.assertEqual(ts.end[1], 'dateTime')
        self.assertEqual(ts.end[0], datetime.datetime(
            1997, 7, 16, 7, 30, 15,
            tzinfo=tzutc()))

    def test_featurefromstring(self):
        d = kml.Document(ns='')
        doc = """<Document>
          <name>Document.kml</name>
          <open>1</open>
          <TimeStamp>
            <when>1997-07-16T10:30:15+03:00</when>
          </TimeStamp>
          <TimeSpan>
            <begin>1876-08-01</begin>
            <end>1997-07-16T07:30:15Z</end>
          </TimeSpan>
        </Document>"""

        d.from_string(doc)


class AtomTestCase(unittest.TestCase):

    def test_author(self):
        a = atom.Author(name="Christian Ledermann")
        self.assertEqual(a.name, "Christian Ledermann")
        a.uri = 'http://iwlearn.net'
        a.email = 'christian@gmail.com'
        self.assertTrue("Christian Ledermann" in str(a.to_string()))
        self.assertTrue('http://iwlearn.net' in str(a.to_string()))
        self.assertTrue('christian@gmail.com' in str(a.to_string()))
        self.assertTrue('name>' in str(a.to_string()))
        self.assertTrue('uri>' in str(a.to_string()))
        self.assertTrue('email>' in str(a.to_string()))
        # print (a.to_string())
        a.email = 'christian'
        self.assertFalse('email>' in str(a.to_string()))
        a2 = atom.Author()
        a2.from_string(a.to_string())
        self.assertEqual(a.to_string(), a2.to_string())

    def test_link(self):
        l = atom.Link(href="http://localhost/", rel="alternate")
        self.assertEqual(l.href, "http://localhost/")
        self.assertEqual(l.rel, "alternate")
        l.title = "Title"
        l.type = "text/html"
        l.hreflang = 'en'
        l.length = "4096"
        self.assertTrue('href="http://localhost/"' in str(l.to_string()))
        self.assertTrue('rel="alternate"' in str(l.to_string()))
        self.assertTrue('title="Title"' in str(l.to_string()))
        self.assertTrue('hreflang="en"' in str(l.to_string()))
        self.assertTrue('type="text/html"' in str(l.to_string()))
        self.assertTrue('length="4096"' in str(l.to_string()))
        self.assertTrue('link' in str(l.to_string()))
        self.assertTrue('="http://www.w3.org/2005/Atom"' in str(l.to_string()))
        l2 = atom.Link()
        l2.from_string(l.to_string())
        self.assertEqual(l.to_string(), l2.to_string())
        l.href = None
        self.assertRaises(ValueError, l.to_string)


class SetGeometryTestCase(unittest.TestCase):

    def test_altitude_mode(self):
        geom = Geometry()
        geom.geometry = Point(0, 1)
        self.assertEqual(geom.altitude_mode, None)
        self.assertFalse('altitudeMode' in str(geom.to_string()))
        geom.altitude_mode = 'unknown'
        self.assertRaises(AssertionError, geom.to_string)
        geom.altitude_mode = 'clampToSeaFloor'
        self.assertRaises(AssertionError, geom.to_string)
        geom.altitude_mode = 'relativeToSeaFloor'
        self.assertRaises(AssertionError, geom.to_string)
        geom.altitude_mode = 'clampToGround'
        self.assertFalse('altitudeMode' in str(geom.to_string()))
        geom.altitude_mode = 'relativeToGround'
        self.assertTrue(
            'altitudeMode>relativeToGround</' in str(geom.to_string()))
        geom.altitude_mode = 'absolute'
        self.assertTrue('altitudeMode>absolute</' in str(geom.to_string()))

    def test_extrude(self):
        geom = Geometry()
        self.assertEqual(geom.extrude, False)
        geom.geometry = Point(0, 1)
        geom.extrude = False
        self.assertFalse('extrude' in str(geom.to_string()))
        geom.extrude = True
        geom.altitude_mode = 'clampToGround'
        self.assertFalse('extrude' in str(geom.to_string()))
        geom.altitude_mode = 'relativeToGround'
        self.assertTrue('extrude>1</' in str(geom.to_string()))
        geom.altitude_mode = 'absolute'
        self.assertTrue('extrude>1</' in str(geom.to_string()))

    def test_tesselate(self):
        geom = Geometry()
        self.assertEqual(geom.tessellate, False)
        geom.geometry = LineString([(0, 0), (1, 1)])
        self.assertFalse('tessellate' in str(geom.to_string()))
        geom.altitude_mode = 'clampToGround'
        self.assertFalse('tessellate' in str(geom.to_string()))
        geom.altitude_mode = 'relativeToGround'
        self.assertFalse('tessellate' in str(geom.to_string()))
        geom.altitude_mode = 'absolute'
        self.assertFalse('tessellate' in str(geom.to_string()))
        geom.tessellate = True
        geom.altitude_mode = None
        self.assertFalse('tessellate' in str(geom.to_string()))
        geom.altitude_mode = 'relativeToGround'
        self.assertFalse('tessellate' in str(geom.to_string()))
        geom.altitude_mode = 'absolute'
        self.assertFalse('tessellate' in str(geom.to_string()))
        geom.altitude_mode = 'clampToGround'
        self.assertTrue('tessellate>1</' in str(geom.to_string()))
        # for geometries != LineString tesselate is ignored
        geom.geometry = Point(0, 1)
        self.assertFalse('tessellate' in str(geom.to_string()))
        geom.geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])
        self.assertFalse('tessellate' in str(geom.to_string()))

    def test_point(self):
        p = Point(0, 1)
        g = Geometry(geometry=p)
        self.assertEqual(g.geometry, p)
        g = Geometry(geometry=p.__geo_interface__)
        self.assertEqual(g.geometry.__geo_interface__, p.__geo_interface__)
        self.assertTrue('Point' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,1.000000</' in str(g.to_string()))

    def test_linestring(self):
        l = LineString([(0, 0), (1, 1)])
        g = Geometry(geometry=l)
        self.assertEqual(g.geometry, l)
        self.assertTrue('LineString' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,0.000000 1.000000,1.000000</' in
            str(g.to_string()))
        g2 = Geometry()
        g2.from_string(g.to_string())
        self.assertEqual(g.to_string(), g2.to_string())

    def test_linearring(self):
        l = LinearRing([(0, 0), (1, 0), (1, 1), (0, 0)])
        g = Geometry(geometry=l)
        self.assertEqual(g.geometry, l)
        self.assertTrue('LinearRing' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000 0.000000,0.000000</'
            in str(g.to_string()))

    def test_polygon(self):
        # without holes
        l = Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])
        g = Geometry(geometry=l)
        self.assertEqual(g.geometry, l)
        self.assertTrue('Polygon' in str(g.to_string()))
        self.assertTrue('outerBoundaryIs' in str(g.to_string()))
        self.assertFalse('innerBoundaryIs' in str(g.to_string()))
        self.assertTrue('LinearRing' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000 0.000000,0.000000</'
            in str(g.to_string()))
        # with holes
        p = Polygon(
            [(-1, -1), (2, -1), (2, 2), (-1, -1)], [[(0, 0), (1, 0), (1, 1),
                                                     (0, 0)]], )
        g = Geometry(geometry=p)
        self.assertEqual(g.geometry, p)
        self.assertTrue('Polygon' in str(g.to_string()))
        self.assertTrue('outerBoundaryIs' in str(g.to_string()))
        self.assertTrue('innerBoundaryIs' in str(g.to_string()))
        self.assertTrue('LinearRing' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000 0.000000,0.000000</'
            in str(g.to_string()))
        self.assertTrue(
            'coordinates>-1.000000,-1.000000 2.000000,-1.000000 2.000000,2.000000 -1.000000,-1.000000</'
            in str(g.to_string()))

    def test_multipoint(self):
        p0 = Point(0, 1)
        p1 = Point(1, 1)
        g = Geometry(geometry=MultiPoint([p0, p1]))
        self.assertTrue('MultiGeometry' in str(g.to_string()))
        self.assertTrue('Point' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,1.000000</' in str(g.to_string()))
        self.assertTrue(
            'coordinates>1.000000,1.000000</' in str(g.to_string()))

    def test_multilinestring(self):
        l0 = LineString([(0, 0), (1, 0)])
        l1 = LineString([(0, 1), (1, 1)])
        g = Geometry(geometry=MultiLineString([l0, l1]))
        self.assertTrue('MultiGeometry' in str(g.to_string()))
        self.assertTrue('LineString' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,0.000000 1.000000,0.000000</' in
            str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,1.000000 1.000000,1.000000</' in
            str(g.to_string()))

    def test_multipolygon(self):
        # with holes
        p0 = Polygon(
            [(-1, -1), (2, -1), (2, 2), (-1, -1)], [[(0, 0), (1, 0), (1, 1),
                                                     (0, 0)]])
        # without holes
        p1 = Polygon([(3, 0), (4, 0), (4, 1), (3, 0)])
        g = Geometry(geometry=MultiPolygon([p0, p1]))
        self.assertTrue('MultiGeometry' in str(g.to_string()))
        self.assertTrue('Polygon' in str(g.to_string()))
        self.assertTrue('outerBoundaryIs' in str(g.to_string()))
        self.assertTrue('innerBoundaryIs' in str(g.to_string()))
        self.assertTrue('LinearRing' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000 0.000000,0.000000</'
            in str(g.to_string()))
        self.assertTrue(
            'coordinates>-1.000000,-1.000000 2.000000,-1.000000 2.000000,2.000000 -1.000000,-1.000000</'
            in str(g.to_string()))
        self.assertTrue(
            'coordinates>3.000000,0.000000 4.000000,0.000000 4.000000,1.000000 3.000000,0.000000</'
            in str(g.to_string()))

    def test_geometrycollection(self):
        po = Polygon([(3, 0), (4, 0), (4, 1), (3, 0)])
        lr = LinearRing([(0, -1), (1, -1), (1, 1), (0, -1)])
        ls = LineString([(0, 0), (1, 1)])
        p = Point(0, 1)
        # geo_if = {'type': 'GeometryCollection', 'geometries': [
        #     po.__geo_interface__, p.__geo_interface__,
        #     ls.__geo_interface__, lr.__geo_interface__]}
        g = Geometry(geometry=GeometryCollection([po, p, ls, lr]))
        # g1 = Geometry(geometry=as_shape(geo_if))
        # self.assertEqual(g1.__geo_interface__, g.__geo_interface__)
        self.assertTrue('MultiGeometry' in str(g.to_string()))
        self.assertTrue('Polygon' in str(g.to_string()))
        self.assertTrue('outerBoundaryIs' in str(g.to_string()))
        self.assertFalse('innerBoundaryIs' in str(g.to_string()))
        self.assertTrue('LinearRing' in str(g.to_string()))
        self.assertTrue(
            'coordinates>3.000000,0.000000 4.000000,0.000000 4.000000,1.000000 3.000000,0.000000</'
            in str(g.to_string()))
        self.assertTrue('LineString' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,0.000000 1.000000,1.000000</' in
            str(g.to_string()))
        self.assertTrue('Point' in str(g.to_string()))
        self.assertTrue(
            'coordinates>0.000000,1.000000</' in str(g.to_string()))


class GetGeometryTestCase(unittest.TestCase):

    def test_altitude_mode(self):
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:altitudeMode>clampToGround</kml:altitudeMode>
        </kml:Point>"""

        g = Geometry()
        self.assertEqual(g.altitude_mode, None)
        g.from_string(doc)
        self.assertEqual(g.altitude_mode, 'clampToGround')

    def test_extrude(self):
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:extrude>1</kml:extrude>
        </kml:Point>"""

        g = Geometry()
        self.assertEqual(g.extrude, False)
        g.from_string(doc)
        self.assertEqual(g.extrude, True)

    def test_tesselate(self):
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
          <kml:tessellate>1</kml:tessellate>
        </kml:Point>"""

        g = Geometry()
        self.assertEqual(g.tessellate, False)
        g.from_string(doc)
        self.assertEqual(g.tessellate, True)

    def test_point(self):
        doc = """<kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,1.000000</kml:coordinates>
        </kml:Point>"""

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(
            g.geometry.__geo_interface__,
            {'type': 'Point',
             'coordinates': (0.0, 1.0)})

    def test_linestring(self):
        doc = """<kml:LineString xmlns:kml="http://www.opengis.net/kml/2.2">
            <kml:coordinates>0.000000,0.000000 1.000000,1.000000</kml:coordinates>
        </kml:LineString>"""

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(
            g.geometry.__geo_interface__,
            {'type': 'LineString',
             'coordinates': ((0.0, 0.0), (1.0, 1.0))})

    def test_linearring(self):
        doc = """<kml:LinearRing xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000 0.000000,0.000000</kml:coordinates>
        </kml:LinearRing>
        """

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(
            g.geometry.__geo_interface__, {
                'type': 'LinearRing',
                'coordinates': ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0))
            })

    def test_polygon(self):
        doc = """<kml:Polygon xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:outerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000 0.000000,0.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:outerBoundaryIs>
        </kml:Polygon>
        """

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(
            g.geometry.__geo_interface__, {
                'type': 'Polygon',
                'coordinates': ((
                    (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)
                ), )
            })
        doc = """<kml:Polygon xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:outerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>-1.000000,-1.000000 2.000000,-1.000000 2.000000,2.000000 -1.000000,-1.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:outerBoundaryIs>
          <kml:innerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000 0.000000,0.000000</kml:coordinates>
            </kml:LinearRing>
          </kml:innerBoundaryIs>
        </kml:Polygon>
        """

        g.from_string(doc)
        self.assertEqual(
            g.geometry.__geo_interface__, {
                'type': 'Polygon',
                'coordinates': (
                    ((-1.0, -1.0), (2.0, -1.0), (2.0, 2.0),
                     (-1.0, -1.0)), ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0),
                                     (0.0, 0.0)),
                )
            })

    def test_multipoint(self):
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:Point>
            <kml:coordinates>0.000000,1.000000</kml:coordinates>
          </kml:Point>
          <kml:Point>
            <kml:coordinates>1.000000,1.000000</kml:coordinates>
          </kml:Point>
        </kml:MultiGeometry>
        """

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(len(g.geometry), 2)

    def test_multilinestring(self):
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:LineString>
            <kml:coordinates>0.000000,0.000000 1.000000,0.000000</kml:coordinates>
          </kml:LineString>
          <kml:LineString>
            <kml:coordinates>0.000000,1.000000 1.000000,1.000000</kml:coordinates>
          </kml:LineString>
        </kml:MultiGeometry>
        """

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(len(g.geometry), 2)

    def test_multipolygon(self):
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:Polygon>
            <kml:outerBoundaryIs>
              <kml:LinearRing>
                <kml:coordinates>-1.000000,-1.000000 2.000000,-1.000000 2.000000,2.000000 -1.000000,-1.000000</kml:coordinates>
              </kml:LinearRing>
            </kml:outerBoundaryIs>
            <kml:innerBoundaryIs>
              <kml:LinearRing>
                <kml:coordinates>0.000000,0.000000 1.000000,0.000000 1.000000,1.000000 0.000000,0.000000</kml:coordinates>
              </kml:LinearRing>
            </kml:innerBoundaryIs>
          </kml:Polygon>
          <kml:Polygon>
            <kml:outerBoundaryIs>
              <kml:LinearRing>
                <kml:coordinates>3.000000,0.000000 4.000000,0.000000 4.000000,1.000000 3.000000,0.000000</kml:coordinates>
              </kml:LinearRing>
            </kml:outerBoundaryIs>
          </kml:Polygon>
        </kml:MultiGeometry>
        """

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(len(g.geometry), 2)

    def test_geometrycollection(self):
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:Polygon>
            <kml:outerBoundaryIs>
              <kml:LinearRing>
                <kml:coordinates>3,0 4,0 4,1 3,0</kml:coordinates>
              </kml:LinearRing>
            </kml:outerBoundaryIs>
          </kml:Polygon>
          <kml:Point>
            <kml:coordinates>0.000000,1.000000</kml:coordinates>
          </kml:Point>
          <kml:LineString>
            <kml:coordinates>0.000000,0.000000 1.000000,1.000000</kml:coordinates>
          </kml:LineString>
          <kml:LinearRing>
            <kml:coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,1.0 0.0,0.0</kml:coordinates>
          </kml:LinearRing>
        </kml:MultiGeometry>
        """

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(len(g.geometry), 4)
        doc = """
        <kml:MultiGeometry xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:LinearRing>
            <kml:coordinates>3.0,0.0 4.0,0.0 4.0,1.0 3.0,0.0</kml:coordinates>
          </kml:LinearRing>
          <kml:LinearRing>
            <kml:coordinates>0.0,0.0 1.0,0.0 1.0,1.0 0.0,0.0</kml:coordinates>
          </kml:LinearRing>
        </kml:MultiGeometry>
        """

        g = Geometry()
        g.from_string(doc)
        self.assertEqual(len(g.geometry), 2)
        self.assertEqual(g.geometry.geom_type, 'GeometryCollection')


class Force3DTestCase(unittest.TestCase):

    def setUp(self):
        config.FORCE3D = False

    def tearDown(self):
        # Important: Set FORCE3D back to False!
        config.FORCE3D = False

    def test3d(self):
        config.FORCE3D = True
        ns = ''
        p2 = kml.Placemark(ns, 'id', 'name', 'description')
        p2.geometry = Polygon([(0, 0), (1, 1), (1, 0)])
        p3 = kml.Placemark(ns, 'id', 'name', 'description')
        p3.geometry = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0)])
        self.assertEqual(p2.to_string(), p3.to_string())

    def testno3d(self):
        config.FORCE3D = False
        ns = ''
        p2 = kml.Placemark(ns, 'id', 'name', 'description')
        p2.geometry = Polygon([(0, 0), (1, 1), (1, 0)])
        p3 = kml.Placemark(ns, 'id', 'name', 'description')
        p3.geometry = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0)])
        self.assertNotEqual(p2.to_string(), p3.to_string())


class BaseFeatureTestCase(unittest.TestCase):

    def test_address_string(self):
        f = kml._Feature()
        address = '1600 Amphitheatre Parkway, Mountain View, CA 94043, USA'
        f.address = address
        self.assertEqual(f.address, address)

    def test_address_none(self):
        f = kml._Feature()
        f.address = None
        self.assertEqual(f.address, None)

    def test_address_value_error(self):
        f = kml._Feature()
        with self.assertRaises(ValueError):
            f.address = 123

    def test_phone_number_string(self):
        f = kml._Feature()
        f.phoneNumber = '+1-234-567-8901'
        self.assertEqual(f.phoneNumber, '+1-234-567-8901')

    def test_phone_number_none(self):
        f = kml._Feature()
        f.phoneNumber = None
        self.assertEqual(f.phoneNumber, None)

    def test_phone_number_value_error(self):
        f = kml._Feature()
        with self.assertRaises(ValueError):
            f.phoneNumber = 123


class BaseOverlayTestCase(unittest.TestCase):

    def test_color_string(self):
        o = kml._Overlay(name='An Overlay')
        o.color = '00010203'
        self.assertEqual(o.color, '00010203')

    def test_color_none(self):
        o = kml._Overlay(name='An Overlay')
        o.color = '00010203'
        self.assertEqual(o.color, '00010203')
        o.color = None
        self.assertEqual(o.color, None)

    def test_color_value_error(self):
        o = kml._Overlay(name='An Overlay')
        with self.assertRaises(ValueError):
            o.color = object()

    def test_draw_order_string(self):
        o = kml._Overlay(name='An Overlay')
        o.drawOrder = '1'
        self.assertEqual(o.drawOrder, '1')

    def test_draw_order_int(self):
        o = kml._Overlay(name='An Overlay')
        o.drawOrder = 1
        self.assertEqual(o.drawOrder, '1')

    def test_draw_order_none(self):
        o = kml._Overlay(name='An Overlay')
        o.drawOrder = '1'
        self.assertEqual(o.drawOrder, '1')
        o.drawOrder = None
        self.assertEqual(o.drawOrder, None)

    def test_draw_order_value_error(self):
        o = kml._Overlay(name='An Overlay')
        with self.assertRaises(ValueError):
            o.drawOrder = object()

    def test_icon_without_tag(self):
        o = kml._Overlay(name='An Overlay')
        o.icon = 'http://example.com/'
        self.assertEqual(o.icon, '<href>http://example.com/</href>')

    def test_icon_with_open_tag(self):
        o = kml._Overlay(name='An Overlay')
        o.icon = '<href>http://example.com/'
        self.assertEqual(o.icon, '<href>http://example.com/</href>')

    def test_icon_with_close_tag(self):
        o = kml._Overlay(name='An Overlay')
        o.icon = 'http://example.com/</href>'
        self.assertEqual(o.icon, '<href>http://example.com/</href>')

    def test_icon_with_tag(self):
        o = kml._Overlay(name='An Overlay')
        o.icon = '<href>http://example.com/</href>'
        self.assertEqual(o.icon, '<href>http://example.com/</href>')

    def test_icon_to_none(self):
        o = kml._Overlay(name='An Overlay')
        o.icon = '<href>http://example.com/</href>'
        self.assertEqual(o.icon, '<href>http://example.com/</href>')
        o.icon = None
        self.assertEqual(o.icon, None)

    def test_icon_raise_exception(self):
        o = kml._Overlay(name='An Overlay')
        with self.assertRaises(ValueError):
            o.icon = 12345


class GroundOverlayTestCase(unittest.TestCase):

    def setUp(self):
        self.g = kml.GroundOverlay()

    def test_altitude_int(self):
        self.g.altitude = 123
        self.assertEqual(self.g.altitude, '123')

    def test_altitude_float(self):
        self.g.altitude = 123.4
        self.assertEqual(self.g.altitude, '123.4')

    def test_altitude_string(self):
        self.g.altitude = '123'
        self.assertEqual(self.g.altitude, '123')

    def test_altitude_value_error(self):
        with self.assertRaises(ValueError):
            self.g.altitude = object()

    def test_altitude_none(self):
        self.g.altitude = '123'
        self.assertEqual(self.g.altitude, '123')
        self.g.altitude = None
        self.assertEqual(self.g.altitude, None)

    def test_altitude_mode_default(self):
        self.assertEqual(self.g.altitudeMode, 'clampToGround')

    def test_altitude_mode_error(self):
        self.g.altitudeMode = ''
        self.assertEqual(self.g.altitudeMode, 'clampToGround')

    def test_altitude_mode_clamp(self):
        self.g.altitudeMode = 'clampToGround'
        self.assertEqual(self.g.altitudeMode, 'clampToGround')

    def test_altitude_mode_absolute(self):
        self.g.altitudeMode = 'absolute'
        self.assertEqual(self.g.altitudeMode, 'absolute')

    def test_latlonbox_function(self):
        self.g.latLonBox(10, 20, 30, 40, 50)

        self.assertEqual(self.g.north, '10')
        self.assertEqual(self.g.south, '20')
        self.assertEqual(self.g.east, '30')
        self.assertEqual(self.g.west, '40')
        self.assertEqual(self.g.rotation, '50')

    def test_latlonbox_string(self):
        self.g.north = '10'
        self.g.south = '20'
        self.g.east = '30'
        self.g.west = '40'
        self.g.rotation = '50'

        self.assertEqual(self.g.north, '10')
        self.assertEqual(self.g.south, '20')
        self.assertEqual(self.g.east, '30')
        self.assertEqual(self.g.west, '40')
        self.assertEqual(self.g.rotation, '50')

    def test_latlonbox_int(self):
        self.g.north = 10
        self.g.south = 20
        self.g.east = 30
        self.g.west = 40
        self.g.rotation = 50

        self.assertEqual(self.g.north, '10')
        self.assertEqual(self.g.south, '20')
        self.assertEqual(self.g.east, '30')
        self.assertEqual(self.g.west, '40')
        self.assertEqual(self.g.rotation, '50')

    def test_latlonbox_float(self):
        self.g.north = 10.0
        self.g.south = 20.0
        self.g.east = 30.0
        self.g.west = 40.0
        self.g.rotation = 50.0

        self.assertEqual(self.g.north, '10.0')
        self.assertEqual(self.g.south, '20.0')
        self.assertEqual(self.g.east, '30.0')
        self.assertEqual(self.g.west, '40.0')
        self.assertEqual(self.g.rotation, '50.0')

    def test_latlonbox_value_error(self):
        with self.assertRaises(ValueError):
            self.g.north = object()

        with self.assertRaises(ValueError):
            self.g.south = object()

        with self.assertRaises(ValueError):
            self.g.east = object()

        with self.assertRaises(ValueError):
            self.g.west = object()

        with self.assertRaises(ValueError):
            self.g.rotation = object()

        self.assertEqual(self.g.north, None)
        self.assertEqual(self.g.south, None)
        self.assertEqual(self.g.east, None)
        self.assertEqual(self.g.west, None)
        self.assertEqual(self.g.rotation, None)

    def test_latlonbox_empty_string(self):
        self.g.north = ''
        self.g.south = ''
        self.g.east = ''
        self.g.west = ''
        self.g.rotation = ''

        self.assertEqual(self.g.north, '')
        self.assertEqual(self.g.south, '')
        self.assertEqual(self.g.east, '')
        self.assertEqual(self.g.west, '')
        self.assertEqual(self.g.rotation, '')

    def test_latlonbox_none(self):
        self.g.north = None
        self.g.south = None
        self.g.east = None
        self.g.west = None
        self.g.rotation = None

        self.assertEqual(self.g.north, None)
        self.assertEqual(self.g.south, None)
        self.assertEqual(self.g.east, None)
        self.assertEqual(self.g.west, None)
        self.assertEqual(self.g.rotation, None)


class GroundOverlayStringTestCase(unittest.TestCase):

    def test_default_to_string(self):
        g = kml.GroundOverlay()

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '</kml:GroundOverlay>')
        self.assertEqual(g.to_string(), expected.to_string())

    def test_to_string(self):
        g = kml.GroundOverlay()
        g.icon = 'http://example.com'
        g.drawOrder = 1
        g.color = '00010203'

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:color>00010203</kml:color>'
            '<kml:drawOrder>1</kml:drawOrder>'
            '<kml:icon>&lt;href&gt;http://example.com&lt;/href&gt;</kml:icon>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_altitude_from_int(self):
        g = kml.GroundOverlay()
        g.altitude = 123

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:altitude>123</kml:altitude>'
            '<kml:altitudeMode>clampToGround</kml:altitudeMode>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_altitude_from_float(self):
        g = kml.GroundOverlay()
        g.altitude = 123.4

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:altitude>123.4</kml:altitude>'
            '<kml:altitudeMode>clampToGround</kml:altitudeMode>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_altitude_from_string(self):
        g = kml.GroundOverlay()
        g.altitude = '123.4'

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:altitude>123.4</kml:altitude>'
            '<kml:altitudeMode>clampToGround</kml:altitudeMode>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_altitude_mode_absolute(self):
        g = kml.GroundOverlay()
        g.altitude = '123.4'
        g.altitudeMode = 'absolute'

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:altitude>123.4</kml:altitude>'
            '<kml:altitudeMode>absolute</kml:altitudeMode>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_altitude_mode_unknown_string(self):
        g = kml.GroundOverlay()
        g.altitude = '123.4'
        g.altitudeMode = 'unknown string'

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:altitude>123.4</kml:altitude>'
            '<kml:altitudeMode>clampToGround</kml:altitudeMode>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_altitude_mode_value(self):
        g = kml.GroundOverlay()
        g.altitude = '123.4'
        g.altitudeMode = 1234

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:altitude>123.4</kml:altitude>'
            '<kml:altitudeMode>clampToGround</kml:altitudeMode>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_latlonbox_no_rotation(self):
        g = kml.GroundOverlay()
        g.latLonBox(10, 20, 30, 40)

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:latLonBox>'
            '<kml:north>10</kml:north>'
            '<kml:south>20</kml:south>'
            '<kml:east>30</kml:east>'
            '<kml:west>40</kml:west>'
            '<kml:rotation>0</kml:rotation>'
            '</kml:latLonBox>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_latlonbox_rotation(self):
        g = kml.GroundOverlay()
        g.latLonBox(10, 20, 30, 40, 50)

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:latLonBox>'
            '<kml:north>10</kml:north>'
            '<kml:south>20</kml:south>'
            '<kml:east>30</kml:east>'
            '<kml:west>40</kml:west>'
            '<kml:rotation>50</kml:rotation>'
            '</kml:latLonBox>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())

    def test_latlonbox_nswer(self):
        g = kml.GroundOverlay()
        g.north = 10
        g.south = 20
        g.east = 30
        g.west = 40
        g.rotation = 50

        expected = kml.GroundOverlay()
        expected.from_string(
            '<kml:GroundOverlay xmlns:kml="http://www.opengis.net/kml/2.2">'
            '<kml:visibility>1</kml:visibility>'
            '<kml:latLonBox>'
            '<kml:north>10</kml:north>'
            '<kml:south>20</kml:south>'
            '<kml:east>30</kml:east>'
            '<kml:west>40</kml:west>'
            '<kml:rotation>50</kml:rotation>'
            '</kml:latLonBox>'
            '</kml:GroundOverlay>')

        self.assertEqual(g.to_string(), expected.to_string())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseClassesTestCase))
    suite.addTest(unittest.makeSuite(BuildKmlTestCase))
    suite.addTest(unittest.makeSuite(KmlFromStringTestCase))
    suite.addTest(unittest.makeSuite(StyleTestCase))
    suite.addTest(unittest.makeSuite(StyleFromStringTestCase))
    suite.addTest(unittest.makeSuite(DateTimeTestCase))
    suite.addTest(unittest.makeSuite(AtomTestCase))
    suite.addTest(unittest.makeSuite(SetGeometryTestCase))
    suite.addTest(unittest.makeSuite(GetGeometryTestCase))
    suite.addTest(unittest.makeSuite(Force3DTestCase))
    suite.addTest(unittest.makeSuite(BaseOverlayTestCase))
    suite.addTest(unittest.makeSuite(GroundOverlayTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
