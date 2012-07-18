# -*- coding: utf-8 -*-
"""frequently used constants and abstract base classes"""
try:
    from lxml import etree
    LXML = True
except ImportError:
    import xml.etree.ElementTree as etree
    LXML = False


NS = '{http://www.opengis.net/kml/2.2}'
