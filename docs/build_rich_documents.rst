Build Rich Documents
=====================

Use this guide when you are generating KML from application data rather than editing an
existing file. The goal is to build a document that is structured enough for real viewers
and downstream systems: shared styles live on the document, folders group features, and
typed schema metadata travels with the placemarks that need it.

1. Create the document shell and shared assets

.. code-block:: pycon

    >>> from fastkml import Document, Schema, SimpleField, Style
    >>> from fastkml.enums import DataType
    >>> from fastkml.styles import IconStyle

    >>> schema = Schema(
    ...     id="asset-schema",
    ...     fields=[SimpleField(name="asset_id", type_=DataType.string)],
    ... )
    >>> style = Style(
    ...     id="asset-style", styles=[IconStyle(icon_href="https://example.com/icon.png")]
    ... )
    >>> doc = Document(id="assets", name="Asset inventory", schemata=[schema], styles=[style])

2. Group placemarks inside folders

.. code-block:: pycon

    >>> from fastkml import Folder

    >>> substations = Folder(name="Substations")
    >>> inspectors = Folder(name="Inspection points")
    >>> doc.append(substations)
    >>> doc.append(inspectors)

3. Attach features and serialize the root KML

.. code-block:: pycon

    >>> from fastkml import KML

    >>> k = KML(features=[doc])
    >>> print(k.to_string(prettyprint=True, precision=3))
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document id="assets">
        <name>Asset inventory</name>
        <Style id="asset-style">
          <IconStyle>
            <Icon>
              <href>https://example.com/icon.png</href>
            </Icon>
          </IconStyle>
        </Style>
        <Folder>
          <name>Substations</name>
        </Folder>
        <Folder>
          <name>Inspection points</name>
        </Folder>
        <Schema id="asset-schema">
          <SimpleField name="asset_id" type="string"/>
        </Schema>
      </Document>
    </kml>
    <BLANKLINE>

Complete example, with a placemark carrying both untyped and schema-backed extended data:

.. code-block:: pycon

    >>> from fastkml import (
    ...     Data,
    ...     Document,
    ...     ExtendedData,
    ...     Folder,
    ...     KML,
    ...     Placemark,
    ...     Schema,
    ...     SchemaData,
    ...     SimpleData,
    ...     SimpleField,
    ...     Style,
    ...     StyleUrl,
    ... )
    >>> from fastkml.enums import DataType
    >>> from fastkml.styles import IconStyle
    >>> from pygeoif import Point

    >>> schema = Schema(
    ...     id="asset-schema", fields=[SimpleField(name="asset_id", type_=DataType.string)]
    ... )
    >>> style = Style(
    ...     id="asset-style", styles=[IconStyle(icon_href="https://example.com/icon.png")]
    ... )

    >>> placemark = Placemark(
    ...     name="North substation",
    ...     geometry=Point(7.12, 50.73, 0),
    ...     style_url=StyleUrl(url="#asset-style"),
    ...     extended_data=ExtendedData(
    ...         elements=[
    ...             Data(name="owner", value="Grid Ops"),
    ...             SchemaData(
    ...                 schema_url="#asset-schema",
    ...                 data=[SimpleData(name="asset_id", value="SS-14")],
    ...             ),
    ...         ]
    ...     ),
    ... )

    >>> folder = Folder(name="Substations", features=[placemark])
    >>> doc = Document(
    ...     id="assets",
    ...     name="Asset inventory",
    ...     schemata=[schema],
    ...     styles=[style],
    ...     features=[folder],
    ... )
    >>> k = KML(features=[doc])
    >>> print(k.to_string(prettyprint=True, precision=3))
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document id="assets">
        <name>Asset inventory</name>
        <Style id="asset-style">
          <IconStyle>
            <Icon>
              <href>https://example.com/icon.png</href>
            </Icon>
          </IconStyle>
        </Style>
        <Folder>
          <name>Substations</name>
          <Placemark>
            <name>North substation</name>
            <styleUrl>#asset-style</styleUrl>
            <ExtendedData>
              <Data name="owner">
                <value>Grid Ops</value>
              </Data>
              <SchemaData schemaUrl="#asset-schema">
                <SimpleData name="asset_id">SS-14</SimpleData>
              </SchemaData>
            </ExtendedData>
            <Point>
              <coordinates>7.120,50.730,0.000</coordinates>
            </Point>
          </Placemark>
        </Folder>
        <Schema id="asset-schema">
          <SimpleField name="asset_id" type="string"/>
        </Schema>
      </Document>
    </kml>
    <BLANKLINE>

This pattern lines up with the KML structure in ``fastkml/containers.py``,
``fastkml/features.py``, ``fastkml/styles.py``, and ``fastkml/data.py`` (see
:doc:`kml_document_model` and :doc:`extended_data`). It is also the safest way to use shared
styles because ``Document.get_style_by_url()`` expects those styles to be document-local.

In practice, this structure scales well when one application needs to emit many feature
classes into the same file. A single ``Document`` becomes the place where you publish schema
declarations, shared styles, and other reusable assets, while folders act as coarse logical
groupings for viewers. That mirrors how Google Earth and similar tools expose the document
tree to users, so the generated file stays understandable even after it leaves your
codebase.
