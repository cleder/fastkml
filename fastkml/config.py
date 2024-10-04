# Copyright (C) 2012 - 2023  Christian Ledermann
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

"""Frequently used constants and configuration options."""
import logging
import warnings
from types import ModuleType
from typing import Final

__all__ = [
    "ATOMNS",
    "DEFAULT_NAME_SPACES",
    "GXNS",
    "KMLNS",
    "etree",
    "register_namespaces",
    "set_default_namespaces",
    "set_etree_implementation",
]

try:  # pragma: no cover
    from lxml import etree

except ImportError:  # pragma: no cover
    warnings.warn("Package `lxml` missing. Pretty print will be disabled")  # noqa: B028
    import xml.etree.ElementTree as etree  # noqa: N813


logger = logging.getLogger(__name__)


def set_etree_implementation(implementation: ModuleType) -> None:
    """Set the etree implementation to use."""
    global etree  # noqa: PLW0603
    etree = implementation


KML: Final = "kml"
ATOM: Final = "atom"
GX: Final = "gx"

KMLNS = "{http://www.opengis.net/kml/2.2}"
ATOMNS = "{http://www.w3.org/2005/Atom}"
GXNS = "{http://www.google.com/kml/ext/2.2}"

NAME_SPACES = {
    KML: KMLNS,
    ATOM: ATOMNS,
    GX: GXNS,
}


DEFAULT_NAME_SPACES = {k: v[1:-1] for k, v in NAME_SPACES.items()}


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
