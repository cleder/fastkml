# -*- coding: utf-8 -*-
""" abstract base classes"""

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

import config

class _BaseObject(object):
    """ This is an abstract base class and cannot be used directly in a
    KML file. It provides the id attribute, which allows unique
    identification of a KML element, and the targetId attribute,
    which is used to reference objects that have already been loaded into
    Google Earth. The id attribute must be assigned if the <Update>
    mechanism is to be used."""
    __name__ = None
    id = None
    ns = None
    targetId = None

    def __init__(self, ns=None, id=None):
        self.id = id
        if ns == None:
            self.ns = config.NS
        else:
            self.ns = ns

    def etree_element(self):
        if self.__name__:
            element = etree.Element(self.ns + self.__name__)
            if self.id:
                element.set('id', self.id)
            if self.targetId:
                element.set('targetId', self.targetId)
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
            if element.get('targetId'):
                self.targetId = element.get('targetId')
