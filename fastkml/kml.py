# -*- coding: utf-8 -*-
"""
KML is an open standard officially named the OpenGIS KML Encoding Standard
(OGC KML). It is maintained by the Open Geospatial Consortium, Inc. (OGC).
The complete specification for OGC KML can be found at
http://www.opengeospatial.org/standards/kml/.

The complete XML schema for KML is located at
http://schemas.opengis.net/kml/.

"""

from shapely.geometry import Point, LineString, Polygon
from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
from shapely.geometry.polygon import LinearRing
import config
import logging
logger = logging.getLogger('fastkml.kml')


try:
    from lxml import etree
    LXML = True
except ImportError:
    import xml.etree.ElementTree as etree
    LXML = False

from styles import StyleUrl, Style, StyleMap, _StyleSelector

import atom
import gx


class KML(object):
    """ represents a KML File """

    _features = []
    ns = None

    def __init__(self, ns=None):
        self._features =[]
        if ns == None:
            self.ns = config.NS
        else:
            self.ns = ns

    def from_string(self, xml_string):
        """ create a KML object from a xml string"""
        element = etree.XML(xml_string)
        if element.tag.endswith('kml'):
            ns = element.tag.rstrip('kml')
            documents = element.findall('%sDocument' % ns)
            for document in documents:
                feature = Document(ns)
                feature.from_element(document)
                self.append(feature)
            folders = element.findall('%sFolder' % ns)
            for folder in folders:
                feature = Folder(ns)
                feature.from_element(folder)
                self.append(feature)
            placemarks = element.findall('%sPlacemark' % ns)
            for placemark in placemarks:
                feature = Placemark(ns)
                feature.from_element(placemark)
                self.append(feature)
        else:
            raise TypeError

    def etree_element(self):
        root = etree.Element('%skml' % self.ns)
        for feature in self.features():
            root.append(feature.etree_element())
        return root


    def to_string(self, prettyprint=False):
        """ Returm the KML Object as xml """
        if LXML and prettyprint:
            return etree.tostring(self.etree_element(), encoding='utf-8',
                                    pretty_print=True)
        else:
            return etree.tostring(self.etree_element(), encoding='utf-8')

    def features(self):
        """ return a list of features """
        #XXX yield feature, test if they are valid features
        return self._features

    def append(self, kmlobj):
        """ append a feature """
        if isinstance(kmlobj, (Document, Folder, Placemark)):
            self._features.append(kmlobj)
        else:
            raise TypeError

class _Feature(object):
    """
    abstract element; do not create
    subclasses are:
    Container (Document, Folder),
    Placemark,
    #NetworkLink,
    #GroundOverlay,
    #PhotoOverlay,
    #ScreenOverlay
    """
    ns = None
    id = None
    name = None
    #User-defined text displayed in the 3D viewer as the label for the
    #object (for example, for a Placemark, Folder, or NetworkLink).
    description = None
    #User-supplied content that appears in the description balloon.
    visibility = 1
    #Boolean value. Specifies whether the feature is drawn in the 3D
    #viewer when it is initially loaded. In order for a feature to be
    #visible, the <visibility> tag of all its ancestors must also be
    #set to 1.
    isopen = 0
    #Boolean value. Specifies whether a Document or Folder appears
    #closed or open when first loaded into the Places panel.
    #0=collapsed (the default), 1=expanded.
    styleUrl = None
    #URL of a <Style> or <StyleMap> defined in a Document.
    #If the style is in the same file, use a # reference.
    #If the style is defined in an external file, use a full URL
    #along with # referencing.
    _styles = None

    #XXX atom_author = None
    #XXX atom_link = None

    def __init__(self, ns=None, id=None, name=None, description=None,
                styles=None, styleUrl=None):
        self.id = id
        self.name=name
        self.description=description
        self.styleUrl = styleUrl
        self._styles = []
        if styles:
            for style in styles:
                self.append_style(style)
        if ns == None:
            self.ns = config.NS
        else:
            self.ns = ns

    def append_style(self, style):
        """ append a style to the feature """
        if isinstance(style, _StyleSelector):
            self._styles.append(style)
        else:
            raise TypeError

    def styles(self):
        """ iterate over the styles of this feature """
        for style in self._styles:
            if isinstance(style, _StyleSelector):
                yield style
            else:
                raise TypeError


    def etree_element(self):
        if self.__name__:
            element = etree.Element(self.ns + self.__name__)
            if self.id:
                element.set('id', self.id)
            if self.name:
                name = etree.SubElement(element, "%sname" %self.ns)
                name.text = self.name
            if self.description:
                description =etree.SubElement(element, "%sdescription" %self.ns)
                description.text = self.description
            visibility = etree.SubElement(element, "%svisibility" %self.ns)
            visibility.text = str(self.visibility)
            isopen = etree.SubElement(element, "%sopen" %self.ns)
            isopen.text = str(self.isopen)
            if self.styleUrl:
                styleUrl = StyleUrl( self.ns, self.styleUrl)
                element.append(styleUrl.etree_element())
            for style in self.styles():
                element.append(style.etree_element())
        else:
            raise NotImplementedError
        return element


    def from_string(self, xml_string):
        self.from_element(etree.XML(xml_string))

    def from_element(self, element):
        if self.ns + self.__name__ != element.tag:
            raise TypeError
        else:
            if element.get('id'):
                self.id = element.get('id')
            name = element.find('%sname' %self.ns)
            if name is not None:
                self.name = name.text
            description = element.find('%sdescription' %self.ns)
            if description is not None:
                self.description = description.text
            visibility = element.find('%svisibility' %self.ns)
            if visibility is not None:
                self.visibility = int(visibility.text)
            isopen = element.find('%sopen' %self.ns)
            if isopen is not None:
                self.isopen = int(isopen.text)
            styles = element.findall('%sStyle' % self.ns)
            for style in styles:
                s = Style(self.ns)
                s.from_element(style)
                self.append_style(s)
            styles = element.findall('%sStyleMap' % self.ns)
            for style in styles:
                s = StyleMap(self.ns)
                s.from_element(style)
                self.append_style(s)
            style_url = element.find('%sstyleUrl' % self.ns)
            if style_url:
                s = StyleUrl(self.ns)
                s.from_element(style_url)
                self.styleUrl = s.url



class _Container(_Feature):
    """
    abstract element; do not create
    A Container element holds one or more Features and allows the
    creation of nested hierarchies.
    subclasses are:
    Document,
    Folder
    """

    _features = []

    def __init__(self, ns=None, id=None, name=None, description=None):
        super(_Container, self).__init__(ns, id, name, description)
        self._features =[]
        if ns == None:
            self.ns = config.NS
        else:
            self.ns = ns

    def features(self):
        """ return a list of features """
        return self._features

    def etree_element(self):
        element = super(_Container, self).etree_element()
        for feature in self.features():
            element.append(feature.etree_element())
        return element


    def append(self, kmlobj):
        """ append a feature """
        if isinstance(kmlobj, _Feature):
            self._features.append(kmlobj)
        assert(kmlobj != self)



class Document(_Container):
    """
    A Document is a container for features and styles. This element is
    required if your KML file uses shared styles
    """
    __name__ = "Document"

    def from_element(self, element):
        super(Document, self).from_element(element)
        folders = element.findall('%sFolder' % self.ns)
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall('%sPlacemark' % self.ns)
        for placemark in placemarks:
            feature = Placemark(self.ns)
            feature.from_element(placemark)
            self.append(feature)


class Folder(_Container):
    """
    A Folder is used to arrange other Features hierarchically
    (Folders, Placemarks, #NetworkLinks, or #Overlays).
    """
    __name__ = "Folder"

    def from_element(self, element):
        super(Folder, self).from_element(element)
        folders = element.findall('%sFolder' % self.ns)
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall('%sPlacemark' % self.ns)
        for placemark in placemarks:
            feature = Placemark(self.ns)
            feature.from_element(placemark)
            self.append(feature)

class Placemark(_Feature):
    """
    A Placemark is a Feature with associated Geometry.
    In Google Earth, a Placemark appears as a list item in the Places
    panel. A Placemark with a Point has an icon associated with it that
    marks a point on the Earth in the 3D viewer.
    """

    __name__ = "Placemark"
    geometry = None



    def _get_coordinates(self, element):
        coordinates = element.find('%scoordinates' % self.ns)
        if coordinates is not None:
            latlons = coordinates.text.strip().split()
            coords = []
            for latlon in latlons:
                coords.append([float(c) for c in latlon.split(',')])
            return coords

    def _get_linear_ring(self, element):
        # LinearRing
        lr = element.find('%sLinearRing' % self.ns)
        if lr is not None:
            coords = self._get_coordinates(lr)
            return LinearRing(coords)

    def _get_geometry(self, element):
        # Point, LineString,
        # Polygon,
        point = element.find('%sPoint' % self.ns)
        if point is not None:
            coords = self._get_coordinates(point)
            return Point(coords[0])
        line = element.find('%sLineString' % self.ns)
        if line is not None:
            coords = self._get_coordinates(line)
            return LineString(coords)
        polygon = element.find('%sPolygon' % self.ns)
        if polygon is not None:
            outer_boundary = polygon.find('%souterBoundaryIs' %self.ns)
            ob = self._get_linear_ring(outer_boundary)
            inner_boundaries = polygon.findall('%sinnerBoundaryIs' %self.ns)
            ibs = []
            for inner_boundary in inner_boundaries:
                ibs.append(self._get_linear_ring(inner_boundary))
            return Polygon(ob, ibs)
        return self._get_linear_ring(element)



    def _get_multigeometry(self, element):
        # MultiGeometry
        multigeometry = element.find('%sMultiGeometry' % self.ns)
        geoms = []
        if multigeometry is not None:
            points = multigeometry.findall('%sPoint' % self.ns)
            if points:
                for point in points:
                    geoms.append(Point(self._get_coordinates(point)[0]))
                return MultiPoint(geoms)
            linestrings = multigeometry.findall('%sLineString' % self.ns)
            if linestrings:
                for ls in linestrings:
                    geoms.append(LineString(self._get_coordinates(ls)))
                return MultiLineString(geoms)
            polygons = multigeometry.findall('%sPolygon' % self.ns)
            if polygons:
                for polygon in polygons:
                    outer_boundary = polygon.find('%souterBoundaryIs' %self.ns)
                    ob = self._get_linear_ring(outer_boundary)
                    inner_boundaries = polygon.findall('%sinnerBoundaryIs' %self.ns)
                    ibs = []
                    for inner_boundary in inner_boundaries:
                        ibs.append(self._get_linear_ring(inner_boundary))
                    geoms.append(Polygon(ob, ibs))
                return MultiPolygon(geoms)




    def from_element(self, element):
        super(Placemark, self).from_element(element)
        mgeom = self._get_multigeometry(element)
        geom = self._get_geometry(element)
        if mgeom is not None:
            self.geometry = mgeom
        elif geom is not None:
            self.geometry = geom
        else:
            logger.warn('No geometries found')


    def _etree_coordinates(self, coordinates):
        element = etree.Element("%scoordinates" %self.ns)
        if len(coordinates[0]) == 2:
            tuples = ('%f,%f,0.0' % tuple(c) for c in coordinates)
        elif len(coordinates[0]) == 3:
            tuples = ('%f,%f,%f' % tuple(c) for c in coordinates)
        else:
            raise ValueError("Invalid dimensions")
        element.text = ' '.join(tuples)
        return element

    def _etree_point(self, point):
        element = etree.Element("%sPoint" %self.ns)
        coords = list(point.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_linestring(self, linestring):
        element = etree.Element("%sLineString" %self.ns)
        coords = list(linestring.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_linearring(self, linearring):
        element = etree.Element("%sLinearRing" %self.ns)
        coords = list(linearring.coords)
        element.append(self._etree_coordinates(coords))
        return element

    def _etree_polygon(self, polygon):
        element = etree.Element("%sPolygon" %self.ns)
        outer_boundary = etree.SubElement(element, "%souterBoundaryIs" %self.ns)
        outer_boundary.append(self._etree_linearring(polygon.exterior))
        for ib in polygon.interiors:
            inner_boundary = etree.SubElement(element, "%sinnerBoundaryIs" %self.ns)
            inner_boundary.append(self._etree_linearring(ib))
        return element

    def _etree_multipoint(self, points):
        element = etree.Element("%sMultiGeometry" %self.ns)
        for point in points.geoms:
            element.append(self._etree_point(point))
        return element

    def _etree_multilinestring(self, linestrings):
        element = etree.Element("%sMultiGeometry" %self.ns)
        for linestring in linestrings.geoms:
            element.append(self._etree_linestring(linestring))
        return element

    def _etree_multipolygon(self, polygons):
        element = etree.Element("%sMultiGeometry" %self.ns)
        for polygon in polygons.geoms:
            element.append(self._etree_polygon(polygon))
        return element

    def _etree_geometry(self):
        if isinstance(self.geometry, Point):
            return self._etree_point(self.geometry)
        elif isinstance(self.geometry, LineString):
            return self._etree_linestring(self.geometry)
        elif isinstance(self.geometry, LinearRing):
            return self._etree_linearring(self.geometry)
        elif isinstance(self.geometry, Polygon):
            return self._etree_polygon(self.geometry)
        elif isinstance(self.geometry, MultiPoint):
            return self._etree_multipoint(self.geometry)
        elif isinstance(self.geometry, MultiLineString):
            return self._etree_multilinestring(self.geometry)
        elif isinstance(self.geometry, MultiPolygon):
            return self._etree_multipolygon(self.geometry)


    def etree_element(self):
        element = super(Placemark, self).etree_element()
        if self.geometry is not None:
            element.append(self._etree_geometry())
        else:
            logger.error('Object does not have a geometry')
        return element



