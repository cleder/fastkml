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

"""Abstract base classes"""

import fastkml.config as config
from fastkml.config import etree


class _XMLObject(object):
    """ XML Baseclass"""

    __name__ = None
    ns = None

    def __init__(self, ns=None):
        if ns is None:
            self.ns = config.NS
        else:
            self.ns = ns

    def etree_element(self):
        if self.__name__:
            element = etree.Element(self.ns + self.__name__)
        else:
            raise NotImplementedError(
                "Call of abstract base class, subclasses implement this!"
            )
        return element

    def from_element(self, element):
        if self.ns + self.__name__ != element.tag:
            raise TypeError(
                "Call of abstract base class, subclasses implement this!"
            )

    def from_string(self, xml_string):
        self.from_element(etree.XML(xml_string))

    def to_string(self, prettyprint=True):
        """ Return the KML Object as serialized xml """
        if config.LXML and prettyprint:
            return etree.tostring(
                self.etree_element(),
                encoding='utf-8',
                pretty_print=True).decode('UTF-8')
        else:
            return etree.tostring(
                self.etree_element(),
                encoding='utf-8').decode('UTF-8')


class _BaseObject(_XMLObject):
    """ This is an abstract base class and cannot be used directly in a
    KML file. It provides the id attribute, which allows unique
    identification of a KML element, and the targetId attribute,
    which is used to reference objects that have already been loaded into
    Google Earth. The id attribute must be assigned if the <Update>
    mechanism is to be used."""
    id = None
    targetId = None

    def __init__(self, ns=None, id=None):
        super(_BaseObject, self).__init__(ns)
        self.id = id
        if ns is None:
            self.ns = config.NS
        else:
            self.ns = ns

    def etree_element(self):
        element = super(_BaseObject, self).etree_element()
        if self.id:
            element.set('id', self.id)
        if self.targetId:
            element.set('targetId', self.targetId)
        return element

    def from_element(self, element):
        super(_BaseObject, self).from_element(element)
        if element.get('id'):
            self.id = element.get('id')
        if element.get('targetId'):
            self.targetId = element.get('targetId')
