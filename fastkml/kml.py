# Copyright (C) 2012-2024 Christian Ledermann
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
KML is an open standard officially named the OpenGIS KML Encoding Standard (OGC KML).

It is maintained by the Open Geospatial Consortium, Inc. (OGC).
The complete specification for OGC KML can be found at
http://www.opengeospatial.org/standards/kml/.

The complete XML schema for KML is located at
http://schemas.opengis.net/kml/.

"""
import logging
from pathlib import Path
from typing import IO
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from typing_extensions import Self

from fastkml import config
from fastkml.base import _XMLObject
from fastkml.containers import Document
from fastkml.containers import Folder
from fastkml.enums import Verbosity
from fastkml.features import Placemark
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.overlays import GroundOverlay
from fastkml.overlays import PhotoOverlay
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.types import Element

logger = logging.getLogger(__name__)

kml_children = Union[Folder, Document, Placemark, GroundOverlay, PhotoOverlay]


class KML(_XMLObject):
    """represents a KML File."""

    _default_nsid = config.KML

    features: List[kml_children]
    ns: str

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        features: Optional[Iterable[kml_children]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Leave the namespace (ns) empty ('') if the 'kml:' prefix is undesired.

        Note that all child elements like Document or Placemark need
        to be initialized with empty namespace as well in this case.
        """
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            **kwargs,
        )
        self.features = list(features) if features is not None else []

    def __repr__(self) -> str:
        """Create a string (c)representation for KML."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"features={self.features!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return cls.__name__.lower()

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        """
        Return an Element object representing the KML element.

        Args:
        ----
            precision (Optional[int]): The precision used for floating-point values.
            verbosity (Verbosity): The verbosity level for generating the KML element.

        Returns:
        -------
            Element: The etree Element object representing the KML element.

        """
        # self.ns may be empty, which leads to unprefixed kml elements.
        # However, in this case the xlmns should still be mentioned on the kml
        # element, just without prefix.
        if not self.ns:
            root = config.etree.Element(
                f"{self.ns}{self.get_tag_name()}",
            )
            root.set("xmlns", config.KMLNS[1:-1])
        elif hasattr(config.etree, "LXML_VERSION"):
            root = config.etree.Element(
                f"{self.ns}{self.get_tag_name()}",
                nsmap={None: self.ns[1:-1]},
            )
        else:
            root = config.etree.Element(
                f"{self.ns}{self.get_tag_name()}",
            )
        xml_subelement_list(
            obj=self,
            element=root,
            attr_name="features",
            node_name="",
            precision=precision,
            verbosity=verbosity,
        )
        return cast(Element, root)

    def append(
        self,
        kmlobj: kml_children,
    ) -> None:
        """Append a feature."""
        if kmlobj is self:
            msg = "Cannot append self"
            raise ValueError(msg)
        self.features.append(kmlobj)

    @classmethod
    def parse(
        cls,
        file: Union[Path, str, IO[AnyStr]],
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        strict: bool = True,
    ) -> Self:
        """
        Parse a KML file and return a KML object.

        Args:
        ----
            file: The file to parse.
                Can be a file path (str or Path), or a file-like object.

        Keyword Args:
        ------------
            ns (Optional[str]): The namespace of the KML file.
                If not provided, it will be inferred from the root element.
            name_spaces (Optional[Dict[str, str]]): Additional namespaces.
            strict (bool): Whether to enforce strict parsing rules. Defaults to True.

        Returns:
        -------
            KML object: The parsed KML object.

        """
        try:
            tree = config.etree.parse(
                file,
                parser=config.etree.XMLParser(
                    huge_tree=True,
                    recover=True,
                ),
            )
        except TypeError:
            tree = config.etree.parse(file)
        root = tree.getroot()
        if ns is None:
            ns = cast(str, root.tag[:-3] if root.tag.endswith("kml") else "")
        name_spaces = name_spaces or {}
        if ns:
            name_spaces["kml"] = ns
        name_spaces = {**config.NAME_SPACES, **name_spaces}
        return cls.class_from_element(
            ns=ns,
            name_spaces=name_spaces,
            strict=strict,
            element=root,
        )


registry.register(
    KML,
    RegistryItem(
        ns_ids=("kml",),
        classes=(Document, Folder, Placemark, GroundOverlay, PhotoOverlay),
        node_name="Document,Folder,Placemark,GroundOverlay,PhotoOverlay",
        attr_name="features",
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


__all__ = [
    "KML",
]
