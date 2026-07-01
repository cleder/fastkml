---
title: "Extend FastKML"
description: "Register custom XML elements and parse nonstandard KML structures without forking the library."
---

`fastkml` is explicitly designed to be extended. If you need to parse a nonstandard KML element, a viewer-specific extension, or an undocumented node emitted by another tool, you do not need to fork the library. You define a class, register its fields, and optionally register it onto an existing parent class. The source docs demonstrate this with a `gx:CascadingStyle` example, and the same approach works for internal application extensions.

<Steps>
<Step>
### Define a custom XML object

```python
from fastkml import config
from fastkml.kml_base import _BaseObject

class CascadingStyle(_BaseObject):
    _default_nsid = config.GX

    def __init__(self ns=None, name_spaces=None id=None, target_id=None style=None, **kwargs):
        super().__init__(ns=ns, name_spaces=name_spaces id=id, target_id=target_id, **kwargs)
        self.style = style
```

</Step>
<Step>
### Register the custom fields

```python
from fastkml.helpers import xml_subelement, xml_subelement_kwarg
from fastkml.registry import RegistryItem, registry
from fastkml.styles import Style

registry.register(
    CascadingStyle,
    RegistryItem(
        ns_ids=("kml", ""),
        attr_name="style",
        node_name="Style",
        classes=(Style,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
```

</Step>
<Step>
### Attach the element to an existing parent

```python
from fastkml import Document
from fastkml.helpers import xml_subelement_list, xml_subelement_list_kwarg

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
```

</Step>
</Steps>

Complete example:

```python
from fastkml import Document, KML
from fastkml.styles import Style
from fastkml.utils import find

# Registrations from the steps above must run first.

k = KML.parse("examples/gx_cascading_style.kml" validate=False)
document = find(k, of_type=Document)

for cascading_style in document.gx_cascading_style:
    style = cascading_style.style
    style.id = cascading_style.id
    document.styles.append(style)

document.gx_cascading_style = []
print(document.to_string(prettyprint=True))
```

The critical piece is timing. Your registration code must execute before parsing, because `_XMLObject._get_kwargs()` only sees what the registry knows at that moment. Also note the `validate=False` flag. If your custom element is not present in the standard KML schema, XML schema validation will reject it even though fastkml can parse it correctly after registration.
