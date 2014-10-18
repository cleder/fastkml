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

"""Frequently used constants and configuration options"""

import logging
logger = logging.getLogger('fastkml.config')

try:
    from lxml import etree
    LXML = True
except ImportError:
    logger.warning('Package `lxml` missing. Pretty print will be disabled')
    import xml.etree.ElementTree as etree
    LXML = False


NS = '{http://www.opengis.net/kml/2.2}'
ATOMNS = '{http://www.w3.org/2005/Atom}'
GXNS = '{http://www.google.com/kml/ext/2.2}'

if hasattr(etree, 'register_namespace'):
    etree.register_namespace('kml', NS[1:-1])
    etree.register_namespace('atom', ATOMNS[1:-1])
    etree.register_namespace('gx', GXNS[1:-1])

FORCE3D = False
