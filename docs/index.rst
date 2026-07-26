Welcome to FastKML's documentation!
===================================

.. include:: ../README.rst
    :start-after: inclusion-marker-do-not-remove

Rationale
---------

Why yet another KML library? None of the existing ones quite fit my
requirements, namely:

* fastkml can *read and write* KML files, feeding fastkml's output back into
  fastkml and serializing it again will result in the same output.
* You can parse any KML snippet, it does not need to be a complete KML
  document.
* It is fully tested and actively maintained.
* Geometries are handled in the ``__geo_interface__`` standard.
* Minimal dependencies, pure Python.
* If available, ``lxml`` will be used to increase its speed.

Key Features
------------

* Full KML object tree with ``KML``, ``Document``, ``Folder``, ``Placemark``, overlays,
  views, and styles.
* Geometry adapters for ``Point``, ``LineString``, ``Polygon``, ``MultiGeometry``,
  ``gx:Track``, and ``gx:MultiTrack``.
* Typed extended data with ``Schema``, ``SchemaData``, ``Data``, and ``gx:SimpleArrayData``.
* Namespace-aware parsing and serialization backed by a central registry.
* XML schema validation helpers and recursive search helpers like ``find()`` and
  ``find_all()``.
* Support for Google extension elements through ``fastkml.gx``.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quickstart
   create_kml_files
   working_with_kml
   parse_edit_write
   geometries_and_styles
   build_rich_documents
   configuration
   upgrading

.. toctree::
   :maxdepth: 2
   :caption: Concepts & Architecture

   architecture
   kml_document_model
   geometry_bridge
   extended_data
   registry_and_serialization
   time_and_views

.. toctree::
   :maxdepth: 2
   :caption: Reference & Project Info

   fastkml
   contributing
   kml
   alternatives
   HISTORY
