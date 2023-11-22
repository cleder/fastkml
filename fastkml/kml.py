# Copyright (C) 2012-2022  Christian Ledermann
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

"""
KML is an open standard officially named the OpenGIS KML Encoding Standard
(OGC KML). It is maintained by the Open Geospatial Consortium, Inc. (OGC).
The complete specification for OGC KML can be found at
http://www.opengeospatial.org/standards/kml/.

The complete XML schema for KML is located at
http://schemas.opengis.net/kml/.

"""
import logging
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Union

from fastkml import config
from fastkml.containers import Document
from fastkml.containers import Folder
from fastkml.enums import Verbosity
from fastkml.features import Placemark
from fastkml.overlays import GroundOverlay
from fastkml.overlays import PhotoOverlay
from fastkml.overlays import _Overlay
from fastkml.types import Element

logger = logging.getLogger(__name__)


class KML:
    """represents a KML File."""

    _features = []
    ns = None

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        features: Optional[Iterable[Union[Folder, Document, Placemark]]] = None,
    ) -> None:
        """
        The namespace (ns) may be empty ('') if the 'kml:' prefix is
        undesired. Note that all child elements like Document or Placemark need
        to be initialized with empty namespace as well in this case.

        """
        self._features = list(features) if features is not None else []

        self.ns = config.KMLNS if ns is None else ns

    def from_string(self, xml_string: str) -> None:
        """Create a KML object from a xml string."""
        try:
            element = config.etree.fromstring(
                xml_string,
                parser=config.etree.XMLParser(huge_tree=True, recover=True),
            )
        except TypeError:
            element = config.etree.XML(xml_string)

        if not element.tag.endswith("kml"):
            raise TypeError

        ns = element.tag.rstrip("kml")
        documents = element.findall(f"{ns}Document")
        for document in documents:
            feature = Document(ns)
            feature.from_element(document)
            self.append(feature)
        folders = element.findall(f"{ns}Folder")
        for folder in folders:
            feature = Folder(ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall(f"{ns}Placemark")
        for placemark in placemarks:
            feature = Placemark(ns)
            feature.from_element(placemark)
            self.append(feature)
        groundoverlays = element.findall(f"{ns}GroundOverlay")
        for groundoverlay in groundoverlays:
            feature = GroundOverlay(ns)
            feature.from_element(groundoverlay)
            self.append(feature)
        photo_overlays = element.findall(f"{ns}PhotoOverlay")
        for photo_overlay in photo_overlays:
            feature = PhotoOverlay(ns)
            feature.from_element(photo_overlay)
            self.append(feature)

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        # self.ns may be empty, which leads to unprefixed kml elements.
        # However, in this case the xlmns should still be mentioned on the kml
        # element, just without prefix.
        if not self.ns:
            root = config.etree.Element(f"{self.ns}kml")
            root.set("xmlns", config.KMLNS[1:-1])
        else:
            try:
                root = config.etree.Element(
                    f"{self.ns}kml",
                    # nsmap={None: self.ns[1:-1]},
                )
            except TypeError:
                root = config.etree.Element(f"{self.ns}kml")
        for feature in self.features():
            root.append(feature.etree_element())
        return root

    def to_string(self, prettyprint: bool = False) -> str:
        """Return the KML Object as serialized xml."""
        try:
            return config.etree.tostring(
                self.etree_element(),
                encoding="UTF-8",
                pretty_print=prettyprint,
            ).decode("UTF-8")
        except TypeError:
            return config.etree.tostring(self.etree_element(), encoding="UTF-8").decode(
                "UTF-8",
            )

    def features(self) -> Iterator[Union[Folder, Document, Placemark]]:
        """Iterate over features."""
        for feature in self._features:
            if isinstance(feature, (Document, Folder, Placemark, _Overlay)):
                yield feature
            else:
                msg = (
                    "Features must be instances of "
                    "(Document, Folder, Placemark, Overlay)"
                )
                raise TypeError(msg)

    def append(self, kmlobj: Union[Folder, Document, Placemark]) -> None:
        """Append a feature."""
        if id(kmlobj) == id(self):
            msg = "Cannot append self"
            raise ValueError(msg)
        if isinstance(kmlobj, (Document, Folder, Placemark, _Overlay)):
            self._features.append(kmlobj)
        else:
            msg = "Features must be instances of (Document, Folder, Placemark, Overlay)"
            raise TypeError(
                msg,
            )


__all__ = [
    "Document",
    "Folder",
    "PhotoOverlay",
    "GroundOverlay",
    "KML",
    "Placemark",
]
