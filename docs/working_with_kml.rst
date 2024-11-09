Working with KML Files
======================

Import the necessary modules:

.. code-block:: pycon

    >>> from fastkml.utils import find, find_all
    >>> from fastkml import KML
    >>> from fastkml import Placemark, Point, StyleUrl, Style
    >>> from typing import Dict, Any, Optional, Iterable


Open a KML file:

.. code-block:: pycon

    >>> k = KML.parse("docs/Document-clean.kml")

Extract all placemarks and print their geometries.
The function ``find_all`` recursively searches a KML document for elements of a specific
type and returns an iterator of all matching elements found in the document tree.

.. code-block:: pycon

    >>> placemarks = list(find_all(k, of_type=Placemark))
    >>> for p in placemarks:
    ...     print(p.geometry)  # doctest: +ELLIPSIS
    ...
    POINT Z (-123.93563168 49.16716103 5.0)
    POLYGON Z ((-123.940449937288 49.16927524669021 17.0, ...

We could also search for all Points, which will also return the Points inside the
``MultiGeometries``.

.. code-block:: pycon

    >>> pts = list(find_all(k, of_type=Point))
    >>> for point in pts:
    ...     print(point.geometry)
    ...
    POINT Z (-123.93563168 49.16716103 5.0)
    POINT Z (-123.1097 49.2774 0.0)
    POINT Z (-123.028369 49.26107900000001 0.0)
    POINT Z (-123.3215766 49.2760338 0.0)
    POINT Z (-123.2643704 49.3301853 0.0)
    POINT Z (-123.2477084 49.2890857 0.0)



``find_all`` can also search for arbitrary elements by their attributes, by passing the
attribute name and value as keyword arguments.
``find`` is a shortcut for ``find_all`` that returns the first element found, which is
useful when we know there is only one element that matches the search criteria.

.. code-block:: pycon

    >>> pm = find(k, name="Vancouver Film Studios")
    >>> pm.name
    'Vancouver Film Studios'
    >>> pm.get_tag_name()
    'Placemark'
    >>> find(k, href="http://www.vancouverfilmstudios.com/")  # doctest: +ELLIPSIS
    fastkml.atom.Link(ns=...

We can also use ``find`` to get the parent of the element we found:

.. code-block:: pycon

    >>> a_link = find(k, href="http://www.vancouverfilmstudios.com/")
    >>> find(k, atom_link=a_link)  # doctest: +ELLIPSIS
    fastkml.features.Placemark(ns=...

For more targeted searches, we can combine multiple search criteria:

.. code-block:: pycon

    >>> style_url = StyleUrl(url="#khStyle712")
    >>> pm = find(k, of_type=Placemark, name="HBC Bastion", style_url=style_url)
    >>> pm.geometry
    Point(-123.93563168, 49.16716103, 5.0)
    >>> pm.style_url.url
    '#khStyle712'
    >>> pm.name
    'HBC Bastion'


Extending FastKML
-----------------

FastKML is designed to be easily extended. For example, we can add a new object to KML
by subclassing ``fastkml.base.__XMLObject`` or  ``fastkml.kml_base._BaseObject`` and
defining the new element's tag name and attributes.
The ``<gx:CascadingStyle>`` is an undocumented element that is created in
Google Earth Web that is unsupported by Google Earth Pro, we want to transform it into
a supported element.

.. code-block:: pycon

    >>> from fastkml.kml_base import _BaseObject
    >>> from fastkml import config
    >>> class CascadingStyle(_BaseObject):
    ...     _default_nsid = config.GX
    ...     def __init__(
    ...         self,
    ...         ns: Optional[str] = None,
    ...         name_spaces: Optional[Dict[str, str]] = None,
    ...         id: Optional[str] = None,
    ...         target_id: Optional[str] = None,
    ...         style: Optional[Style] = None,
    ...         **kwargs: Any,
    ...     ) -> None:
    ...         self.style = style
    ...         super().__init__(ns, name_spaces, id, target_id, **kwargs)
    ...

We need to register the attributes of the KML object to be able to parse it:

.. code-block:: pycon

    >>> from fastkml.registry import RegistryItem, registry
    >>> from fastkml.helpers import xml_subelement, xml_subelement_kwarg
    >>> registry.register(
    ...     CascadingStyle,
    ...     RegistryItem(
    ...         ns_ids=("kml",),
    ...         attr_name="style",
    ...         node_name="Style",
    ...         classes=(Style,),
    ...         get_kwarg=xml_subelement_kwarg,
    ...         set_element=xml_subelement,
    ...     ),
    ... )

And register the new element with the KML Document object:

.. code-block:: pycon

    >>> from fastkml import Document
    >>> from fastkml.helpers import xml_subelement_list, xml_subelement_list_kwarg
    >>> registry.register(
    ...     Document,
    ...     RegistryItem(
    ...         ns_ids=("gx",),
    ...         attr_name="gx_cascading_style",
    ...         node_name="CascadingStyle",
    ...         classes=(CascadingStyle,),
    ...         get_kwarg=xml_subelement_list_kwarg,
    ...         set_element=xml_subelement_list,
    ...     ),
    ... )

The CascadingStyle object is now part of the KML document and can be accessed like any
other element.
Now we can create a new KML object and confirm that the new element is parsed correctly:

.. code-block:: pycon

    >>> cs_kml = KML.parse("examples/gx_cascading_style.kml")
    >>> cs = find(cs_kml, of_type=CascadingStyle)
    >>> cs.style  # doctest: +ELLIPSIS
    fastkml.styles.Style(...


To be able to open the KML file in Google Earth Pro, we need to transform the
CascadingStyle element into a supported Style element.
To achieve this we copy the styles into the document styles and adjust their id
to match the id of the CascadingStyle.

.. code-block:: pycon

    >>> document = find(cs_kml, of_type=Document)
    >>> for cascading_style in document.gx_cascading_style:
    ...     kml_style = cascading_style.style
    ...     kml_style.id = cascading_style.id
    ...     document.styles.append(kml_style)
    ...

Now we can remove the CascadingStyle from the document and have a look at the result.

.. code-block:: pycon

    >>> document.gx_cascading_style = []
    >>> print(document.to_string(prettyprint=True))
    <kml:Document xmlns:kml="http://www.opengis.net/kml/2.2">
      <kml:name>Test2</kml:name>
      <kml:StyleMap id="__managed_style_0D301BCC0014827EFCCB">
        <kml:Pair>
          <kml:key>normal</kml:key>
          <kml:styleUrl>#__managed_style_14CDD4276C14827EFCCB</kml:styleUrl>
        </kml:Pair>
        <kml:Pair>
          <kml:key>highlight</kml:key>
          <kml:styleUrl>#__managed_style_25EBAAC82614827EFCCB</kml:styleUrl>
        </kml:Pair>
      </kml:StyleMap>
      <kml:Style id="__managed_style_25EBAAC82614827EFCCB">
        <kml:BalloonStyle>
          <kml:displayMode>hide</kml:displayMode>
        </kml:BalloonStyle>
        <kml:IconStyle>
          <kml:scale>1.2</kml:scale>
          <kml:Icon>
            <kml:href>https://earth.google.com/earth/rpc/cc/icon?color=1976d2&amp;id=2000&amp;scale=4</kml:href>
          </kml:Icon>
          <kml:hotSpot x="64.0" y="128.0" xunits="pixels" yunits="insetPixels"/>
        </kml:IconStyle>
        <kml:LineStyle>
          <kml:width>24.0</kml:width>
        </kml:LineStyle>
        <kml:PolyStyle>
          <kml:color>80000000</kml:color>
        </kml:PolyStyle>
      </kml:Style>
      <kml:Style id="__managed_style_14CDD4276C14827EFCCB">
        <kml:BalloonStyle>
          <kml:displayMode>hide</kml:displayMode>
        </kml:BalloonStyle>
        <kml:IconStyle>
          <kml:Icon>
            <kml:href>https://earth.google.com/earth/rpc/cc/icon?color=1976d2&amp;id=2000&amp;scale=4</kml:href>
          </kml:Icon>
          <kml:hotSpot x="64.0" y="128.0" xunits="pixels" yunits="insetPixels"/>
        </kml:IconStyle>
        <kml:LineStyle>
          <kml:width>16.0</kml:width>
        </kml:LineStyle>
        <kml:PolyStyle>
          <kml:color>80000000</kml:color>
        </kml:PolyStyle>
      </kml:Style>
      <kml:Placemark id="04SAFE6060F147CE66FBD">
        <kml:name>Ort1</kml:name>
        <kml:LookAt>
          <kml:longitude>10.06256752902339</kml:longitude>
          <kml:latitude>53.57036326842834</kml:latitude>
          <kml:altitude>13.96486261382906</kml:altitude>
          <kml:heading>0.0</kml:heading>
          <kml:tilt>0.0</kml:tilt>
          <kml:range>632.584179697442</kml:range>
          <kml:altitudeMode>absolute</kml:altitudeMode>
        </kml:LookAt>
        <kml:styleUrl>#__managed_style_0D301BCC0014827EFCCB</kml:styleUrl>
        <kml:Polygon>
          <kml:outerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>10.05998904317019,53.57172202479447,10.32521244530025 10.06072970043745,53.57050957507556,13.60797686155092 10.06170365480513,53.57072597737833,13.60026817081542 10.06094034058923,53.57192922042453,10.47620396741323 10.05998904317019,53.57172202479447,10.32521244530025</kml:coordinates>
            </kml:LinearRing>
          </kml:outerBoundaryIs>
        </kml:Polygon>
      </kml:Placemark>
    </kml:Document>
    <BLANKLINE>
