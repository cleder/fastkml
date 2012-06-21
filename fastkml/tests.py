# -*- coding: utf-8 -*-
import unittest

import kml

import xml.etree.ElementTree as etree

class BuildKmlTestCase( unittest.TestCase ):
    """ Build a simple KML File """
    def test_kml(self):
        """ kml file without contents """
        k=None
        k = kml.KML()
        self.assertEqual(len(k.features()),0)
        self.assertEqual( k.to_string(),
        '<ns0:kml xmlns:ns0="http://www.opengis.net/kml/2.2" />')

    def test_folder(self):
        """ KML file with folders """
        k = kml.KML()
        f = kml.Folder('', 'id', 'name', 'description')
        nf = kml.Folder('', 'nested-id', 'nested-name', 'nested-description')
        f.append(nf)
        k.append(f)
        f2 = kml.Folder('', 'id2', 'name2', 'description2')
        k.append(f2)
        self.assertEqual(len(k.features()),2)
        self.assertEqual(len( k.features()[0].features()),1)
        print k.to_string()

    def test_placemark(self):
        k = kml.KML()
        p = kml.Placemark('', 'id', 'name', 'description')
        p2 = kml.Placemark('', 'id2', 'name2', 'description2')
        k.append(p)
        k.append(p2)
        self.assertEqual(len(k.features()),2)

    def test_document(self):
        k = kml.KML()
        d = kml.Document('', 'docid', 'doc name', 'doc description')
        f = kml.Folder('', 'fid', 'f name', 'f description')
        k.append(d)
        d.append(f)
        nf = kml.Folder('', 'nested-fid', 'nested f name', 'nested f description')
        f.append(nf)
        f2 = kml.Folder('', 'id2', 'name2', 'description2')
        d.append(f2)
        p = kml.Placemark('', 'id', 'name', 'description')
        p2 = kml.Placemark('', 'id2', 'name2', 'description2')
        f2.append(p)
        nf.append(p2)
        self.assertEqual(len(k.features()),1)
        self.assertEqual(len(k.features()[0].features()),2)

class KmlFromStringTestCase( unittest.TestCase ):

    def test_document(self):
        doc = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
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
          <Placemark>
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
        self.assertEqual(len(k.features()),1)
        self.assertEqual(len(k.features()[0].features()),2)
        print k.to_string()


    def test_folders(self):
        doc="""<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
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
        self.assertEqual(len(k.features()),1)
        self.assertEqual(len(k.features()[0].features()),3)
        print k.to_string()

    def test_placemark(self):
        doc="""<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
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
        self.assertEqual(len(k.features()),1)
        self.assertEqual(k.features()[0].name, "Simple placemark")
        print k.to_string()



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite( KmlFromStringTestCase ))
    suite.addTest(unittest.makeSuite( BuildKmlTestCase ))


    return suite

if __name__ == '__main__':
    unittest.main()
