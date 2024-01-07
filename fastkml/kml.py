# Copyright (C) 2012-2023 Christian Ledermann
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
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union
from typing import cast

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
from fastkml.types import Element

logger = logging.getLogger(__name__)


class KML(_XMLObject):
    """represents a KML File."""

    _default_ns = config.KMLNS

    _features: List[Union[Folder, Document, Placemark]]
    ns: str

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
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
        )
        self.features = list(features) if features is not None else []

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        # self.ns may be empty, which leads to unprefixed kml elements.
        # However, in this case the xlmns should still be mentioned on the kml
        # element, just without prefix.
        if not self.ns:
            root = config.etree.Element(f"{self.ns}kml")  # type: ignore[attr-defined]
            root.set("xmlns", config.KMLNS[1:-1])
        elif hasattr(config.etree, "LXML_VERSION"):  # type: ignore[attr-defined]
            root = config.etree.Element(  # type: ignore[attr-defined]
                f"{self.ns}kml",
                nsmap={None: self.ns[1:-1]},
            )
        else:
            root = config.etree.Element(  # type: ignore[attr-defined]
                f"{self.ns}kml",
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

    def append(self, kmlobj: Union[Folder, Document, Placemark]) -> None:
        """Append a feature."""
        if kmlobj is self:
            msg = "Cannot append self"
            raise ValueError(msg)
        self.features.append(kmlobj)

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        name_spaces = kwargs["name_spaces"]
        assert name_spaces is not None
        kwargs["features"] = []
        kwargs.update(
            xml_subelement_list_kwarg(
                element=element,
                ns=ns,
                name_spaces=name_spaces,
                node_name="",
                kwarg="features",
                classes=(Document, Folder, Placemark, GroundOverlay, PhotoOverlay),
                strict=strict,
            ),
        )
        return kwargs

    @classmethod
    def class_from_string(
        cls,
        string: str,
        *,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        strict: bool = True,
    ) -> _XMLObject:
        """
        Creates a geometry object from a string.

        Args:
        ----
            string: String representation of the geometry object

        Returns:
        -------
            Geometry object
        """
        try:
            element = config.etree.fromstring(  # type: ignore[attr-defined]
                string,
                parser=config.etree.XMLParser(  # type: ignore[attr-defined]
                    huge_tree=True,
                    recover=True,
                ),
            )
        except TypeError:
            element = config.etree.XML(string)  # type: ignore[attr-defined]
        if not element.tag.endswith("kml"):
            raise TypeError
        if ns is None:
            ns = cast(str, element.tag.rstrip("kml"))
        name_spaces = name_spaces or {}
        name_spaces = {**config.NAME_SPACES, **name_spaces}
        return cls.class_from_element(
            ns=ns,
            name_spaces=name_spaces,
            strict=strict,
            element=element,
        )


# registry.register(KML, RegistryItem(
#     classes=(Document, Folder, Placemark, GroundOverlay, PhotoOverlay),
#     node_name='',
#     attr_name="features",
#     get_kwarg=xml_subelement_list_kwarg,
#     set_element=xml_subelement_list,
# ))


__all__ = [
    "KML",
]
