# -*- coding: utf-8 -*-

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

class KML(object):
    """ represents a KML File """

    _features = []

    def __init__(self):
        self._features =[]

    def from_file(self, filename):
        """ read a KML File and parse into a KML Object"""
        f = open(filename, 'r')
        self.from_string(f.read())
        f.close()

    def from_string(self, xml_string):
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
        root = etree.Element('{http://www.opengis.net/kml/2.2}kml')
        for feature in self.features():
            root.append(feature.etree_element())
        return root


    def to_string(self, prettyprint=False):
        """ Returm the KML Object as xml """
        return etree.tostring(self.etree_element(), encoding='utf-8')

    def features(self):
        """ return a list of features """
        return self._features

    def append(self, kmlobj):
        """ append a feature """
        if isinstance(kmlobj, (Document, Folder, Placemark)):
            self._features.append(kmlobj)


class _Feature(object):
    """
    abstract element; do not create
    subclasses are:
    Container (Document, Folder),
    Placemark,
    NetworkLink,
    GroundOverlay,
    PhotoOverlay,
    ScreenOverlay
    """

    id = None
    name = None
    description = None
    visibility = 1
    isopen = 0
    #atom_author = None
    #atom_link = None
    #styleUrl = None


    def __init__(self, ns, id=None, name=None, description=None):
        self.id = id
        self.name=name
        self.description=description
        self.ns = ns

    def etree_element(self):
        if self.__name__:
            element = etree.Element(self.__name__)
            if self.id:
                element.set('id', self.id)
            if self.name:
                name = etree.SubElement(element, "name")
                name.text = self.name
            if self.description:
                description =etree.SubElement(element, "description")
                description.text = self.description
            visibility = etree.SubElement(element, "visibility")
            visibility.text = str(self.visibility)
            isopen = etree.SubElement(element, "open")
            isopen.text = str(self.isopen)
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
                self.visibility = visibility.text
            isopen = element.find('%sopen' %self.ns)
            if isopen is not None:
                self.isopen = isopen.text

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

    def __init__(self, ns, id=None, name=None, description=None):
        super(_Container, self).__init__(ns, id, name, description)
        self._features =[]

    def features(self):
        """ return a list of features """
        return self._features

    def etree_element(self):
        element = super(_Container, self).etree_element()
        for feature in self.features():
            assert(feature != self)
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
    (Folders, Placemarks, NetworkLinks, or Overlays).
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
    __name__ = "Placemark"
    styleUrl = None
    geometry = None
    pass


