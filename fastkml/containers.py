"""Container classes for KML elements."""
import logging
import urllib.parse as urlparse
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

from fastkml import gx
from fastkml.data import Schema
from fastkml.enums import Verbosity
from fastkml.features import Placemark
from fastkml.features import _Feature
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.overlays import _Overlay
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.types import Element

logger = logging.getLogger(__name__)

KmlGeometry = Union[
    Point,
    LineString,
    LinearRing,
    Polygon,
    MultiGeometry,
    gx.MultiTrack,
    gx.Track,
]


class _Container(_Feature):
    """
    abstract element; do not create
    A Container element holds one or more Features and allows the
    creation of nested hierarchies.
    subclasses are:
    Document,
    Folder.
    """

    _features = []

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        styles: Optional[List[Style]] = None,
        style_url: Optional[str] = None,
        features: None = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            description=description,
            styles=styles,
            style_url=style_url,
        )
        self._features = features or []

    def features(self) -> Iterator[_Feature]:
        """Iterate over features."""
        for feature in self._features:
            if isinstance(feature, (Folder, Placemark, Document, _Overlay)):
                yield feature
            else:
                msg = (
                    "Features must be instances of "
                    "(Folder, Placemark, Document, Overlay)"
                )
                raise TypeError(
                    msg,
                )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        for feature in self.features():
            element.append(feature.etree_element())
        return element

    def append(self, kmlobj: _Feature) -> None:
        """Append a feature."""
        if id(kmlobj) == id(self):
            msg = "Cannot append self"
            raise ValueError(msg)
        if isinstance(kmlobj, (Folder, Placemark, Document, _Overlay)):
            self._features.append(kmlobj)
        else:
            msg = "Features must be instances of (Folder, Placemark, Document, Overlay)"
            raise TypeError(
                msg,
            )


class Folder(_Container):
    """
    A Folder is used to arrange other Features hierarchically
    (Folders, Placemarks, #NetworkLinks, or #Overlays).
    """

    __name__ = "Folder"

    def from_element(self, element: Element) -> None:
        super().from_element(element)
        folders = element.findall(f"{self.ns}Folder")
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall(f"{self.ns}Placemark")
        for placemark in placemarks:
            feature = Placemark(self.ns)
            feature.from_element(placemark)
            self.append(feature)
        documents = element.findall(f"{self.ns}Document")
        for document in documents:
            feature = Document(self.ns)
            feature.from_element(document)
            self.append(feature)


class Document(_Container):
    """
    A Document is a container for features and styles. This element is
    required if your KML file uses shared styles or schemata for typed
    extended data.
    """

    __name__ = "Document"
    _schemata = None

    def schemata(self) -> Iterator["Schema"]:
        if self._schemata:
            yield from self._schemata

    def append_schema(self, schema: "Schema") -> None:
        if self._schemata is None:
            self._schemata = []
        if isinstance(schema, Schema):
            self._schemata.append(schema)
        else:
            s = Schema(schema)
            self._schemata.append(s)

    def from_element(self, element: Element, strict: bool = False) -> None:
        super().from_element(element)
        documents = element.findall(f"{self.ns}Document")
        for document in documents:
            feature = Document(self.ns)
            feature.from_element(document)
            self.append(feature)
        folders = element.findall(f"{self.ns}Folder")
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall(f"{self.ns}Placemark")
        for placemark in placemarks:
            feature = Placemark(self.ns)
            feature.from_element(placemark)
            self.append(feature)
        schemata = element.findall(f"{self.ns}Schema")
        for schema in schemata:
            s = Schema.class_from_element(ns=self.ns, element=schema, strict=strict)
            self.append_schema(s)

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self._schemata is not None:
            for schema in self._schemata:
                element.append(schema.etree_element())
        return element

    def get_style_by_url(self, style_url: str) -> Optional[Union[Style, StyleMap]]:
        id = urlparse.urlparse(style_url).fragment
        for style in self.styles():
            if style.id == id:
                return style
        return None
