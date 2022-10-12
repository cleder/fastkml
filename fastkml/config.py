# Copyright (C) 2012 - 2021  Christian Ledermann
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
import warnings
from types import ModuleType

__all__ = [
    "ATOMNS",
    "DEFAULT_NAME_SPACES",
    "FORCE3D",
    "GXNS",
    "KMLNS",
    "register_namespaces",
    "set_default_namespaces",
    "set_etree_implementation",
]

try:  # pragma: no cover
    from lxml import etree

except ImportError:  # pragma: no cover
    warnings.warn("Package `lxml` missing. Pretty print will be disabled")
    import xml.etree.ElementTree as etree  # type: ignore[no-redef] # noqa: N813


logger = logging.getLogger(__name__)


def set_etree_implementation(implementation: ModuleType) -> None:
    """Set the etree implementation to use."""
    global etree
    etree = implementation


KMLNS = "{http://www.opengis.net/kml/2.2}"  # noqa: FS003
ATOMNS = "{http://www.w3.org/2005/Atom}"  # noqa: FS003
GXNS = "{http://www.google.com/kml/ext/2.2}"  # noqa: FS003

DEFAULT_NAME_SPACES = {
    "kml": KMLNS[1:-1],
    "atom": ATOMNS[1:-1],
    "gx": GXNS[1:-1],
}


def register_namespaces(**namespaces: str) -> None:
    """Register namespaces for use in etree.ElementTree.parse()."""
    try:
        for prefix, uri in namespaces.items():
            etree.register_namespace(prefix, uri)
    except AttributeError:  # pragma: no cover
        logger.warning("Namespaces were not registered.")


def set_default_namespaces() -> None:
    """Register the default namespaces for use in etree.ElementTree.parse()."""
    register_namespaces(**DEFAULT_NAME_SPACES)


set_default_namespaces()

FORCE3D = False
