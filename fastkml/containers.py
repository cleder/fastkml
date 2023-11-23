"""Container classes for KML elements."""
import logging
import urllib.parse as urlparse
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from fastkml import atom
from fastkml import gx
from fastkml.data import ExtendedData
from fastkml.data import Schema
from fastkml.enums import Verbosity
from fastkml.features import Placemark
from fastkml.features import Snippet
from fastkml.features import _Feature
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.types import Element
from fastkml.views import Camera
from fastkml.views import LookAt
from fastkml.views import Region

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

    _features: Optional[List[_Feature]]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[List[Style]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        # Container specific
        features: Optional[List[_Feature]] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
        )
        self._features = features or []

    def features(self) -> Iterator[_Feature]:
        """Iterate over features."""
        assert self._features is not None
        yield from self._features

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
        if kmlobj is self:
            msg = "Cannot append self"
            raise ValueError(msg)
        assert self._features is not None
        self._features.append(kmlobj)


class Folder(_Container):
    """
    A Folder is used to arrange other Features hierarchically
    (Folders, Placemarks, #NetworkLinks, or #Overlays).
    """

    __name__ = "Folder"

    def from_element(self, element: Element, strict: bool = False) -> None:
        super().from_element(element)
        folders = element.findall(f"{self.ns}Folder")
        for folder in folders:
            feature = Folder(self.ns)
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall(f"{self.ns}Placemark")
        for placemark in placemarks:
            feature = Placemark(self.ns)  # type: ignore[assignment]
            feature.from_element(placemark)
            self.append(feature)
        documents = element.findall(f"{self.ns}Document")
        for document in documents:
            feature = Document(self.ns)  # type: ignore[assignment]
            feature.from_element(document)
            self.append(feature)


class Document(_Container):
    """
    A Document is a container for features and styles. This element is
    required if your KML file uses shared styles or schemata for typed
    extended data.
    """

    __name__ = "Document"
    _schemata: Optional[List[Schema]]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[List[Style]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        features: Optional[List[_Feature]] = None,
        schemata: Optional[Iterable[Schema]] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
            features=features,
        )
        self._schemata = list(schemata) if schemata else []

    def schemata(self) -> Iterator[Schema]:
        if self._schemata:
            yield from self._schemata

    def append_schema(self, schema: Schema) -> None:
        assert self._schemata is not None
        self._schemata.append(schema)

    def from_element(self, element: Element, strict: bool = False) -> None:
        super().from_element(element)
        documents = element.findall(f"{self.ns}Document")
        for document in documents:
            feature = Document(self.ns)
            feature.from_element(document)
            self.append(feature)
        folders = element.findall(f"{self.ns}Folder")
        for folder in folders:
            feature = Folder(self.ns)  # type: ignore[assignment]
            feature.from_element(folder)
            self.append(feature)
        placemarks = element.findall(f"{self.ns}Placemark")
        for placemark in placemarks:
            feature = Placemark(self.ns)  # type: ignore[assignment]
            feature.from_element(placemark)
            self.append(feature)
        schemata = element.findall(f"{self.ns}Schema")
        for schema in schemata:
            s = cast(
                Schema,
                Schema.class_from_element(ns=self.ns, element=schema, strict=strict),
            )
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
        id_ = urlparse.urlparse(style_url).fragment
        return next((style for style in self.styles() if style.id == id_), None)
