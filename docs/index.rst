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

.. toctree::
   :maxdepth: 2

   quickstart
   create_kml_files
   working_with_kml
   configuration
   upgrading
   fastkml
   contributing
   kml
   alternatives
   HISTORY
