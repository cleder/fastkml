Use Geometries and Styles
==========================

This guide shows a realistic pattern for turning Python geometry data into styled KML
output. The library is especially strong here because ``Placemark`` accepts ordinary
geometry input while the style system stays close to the KML spec. You can build a map layer
from application geometry objects without hand-writing coordinate XML.

1. Create KML geometry from Python geometry

.. code-block:: pycon

    >>> from fastkml.features import Placemark
    >>> from pygeoif.geometry import Polygon

    >>> polygon = Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
    >>> placemark = Placemark(name="Protected area", geometry=polygon)

2. Define shared line and polygon styles

.. code-block:: pycon

    >>> from fastkml.styles import LineStyle, PolyStyle, Style, StyleUrl
    >>> from fastkml.enums import ColorMode

    >>> style = Style(
    ...     id="zone-style",
    ...     styles=[
    ...         LineStyle(color="55FF0000", width=2),
    ...         PolyStyle(
    ...             color="8800FF00", color_mode=ColorMode.normal, fill=True, outline=True
    ...         ),
    ...     ],
    ... )
    >>> placemark.style_url = StyleUrl(url="#zone-style")

3. Build the document

.. code-block:: pycon

    >>> from fastkml import Document, KML

    >>> doc = Document(id="zones", styles=[style], features=[placemark])
    >>> k = KML(features=[doc])
    >>> print(k.to_string(prettyprint=True, precision=3))
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document id="zones">
        <Style id="zone-style">
          <LineStyle>
            <color>55FF0000</color>
            <width>2</width>
          </LineStyle>
          <PolyStyle>
            <color>8800FF00</color>
            <colorMode>normal</colorMode>
            <fill>1</fill>
            <outline>1</outline>
          </PolyStyle>
        </Style>
        <Placemark>
          <name>Protected area</name>
          <styleUrl>#zone-style</styleUrl>
          <Polygon>
            <outerBoundaryIs>
              <LinearRing>
                <coordinates>0.000,0.000,0.000 1.000,1.000,0.000 1.000,0.000,1.000 0.000,0.000,0.000</coordinates>
              </LinearRing>
            </outerBoundaryIs>
          </Polygon>
        </Placemark>
      </Document>
    </kml>
    <BLANKLINE>

This pattern mirrors the ``examples/shp2kml.py`` example from the source repository, where
application geometry is converted once and then styled centrally. Prefer document-level
shared styles over large numbers of inline styles when many features share the same visual
treatment.

If your source geometries already come from Shapely or another library that exposes the geo
interface cleanly, keep the conversion boundary at the edge of your export function. That way
the rest of your application can stay geometry-library-native, while ``fastkml`` only handles
the KML-facing translation and serialization concerns. It also makes testing easier because
you can validate the geometry preparation separately from the KML output.
