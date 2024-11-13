#!/usr/bin/env python
import pathlib
from typing import Any
from typing import Dict
from typing import Optional

from fastkml import KML
from fastkml import Document
from fastkml import Style
from fastkml import config
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.kml_base import _BaseObject
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.utils import find

examples_dir = pathlib.Path(__file__).parent


class CascadingStyle(_BaseObject):
    """
    CascadingStyle.

    The ``<gx:CascadingStyle>`` is an undocumented element that is created in
    Google Earth Web that is unsupported by Google Earth Pro
    """

    _default_nsid = config.GX

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        style: Optional[Style] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the CascadingStyle object."""
        self.style = style
        super().__init__(ns, name_spaces, id, target_id, **kwargs)


registry.register(
    CascadingStyle,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="style",
        node_name="Style",
        classes=(Style,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


registry.register(
    Document,
    RegistryItem(
        ns_ids=("gx",),
        attr_name="gx_cascading_style",
        node_name="CascadingStyle",
        classes=(CascadingStyle,),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)

cs_kml = KML.parse(examples_dir / "gx_cascading_style.kml", validate=False)
document = find(cs_kml, of_type=Document)
for cascading_style in document.gx_cascading_style:
    kml_style = cascading_style.style
    kml_style.id = cascading_style.id
    document.styles.append(kml_style)

document.gx_cascading_style = []
print(cs_kml.to_string(prettyprint=True))
