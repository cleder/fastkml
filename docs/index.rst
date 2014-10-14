Welcome to FastKML's documentation!
===================================

fastkml is a library to read, write and manipulate kml files. It aims to keep
it simple and fast (using lxml_ if available). "Fast" refers to the time you
spend to write and read KML files as well as the time you spend to get
aquainted to the library or to create KML objects. It provides a subset of KML
and is aimed at documents that can be read from multiple clients such as
openlayers and google maps rather than to give you all functionality that KML
on google earth provides.

For more details about the KML Specification, check out the `KML Reference
<https://developers.google.com/kml/documentation/kmlreference>`_ on the Google
developers site.

.. toctree::
   :maxdepth: 2

   quickstart
   installing
   usage_guide
   reference_guide

.. _lxml: https://pypi.python.org/pypi/lxml
.. _kml_reference: https://developers.google.com/kml/documentation/kmlreference
