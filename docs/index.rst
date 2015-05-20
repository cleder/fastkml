Welcome to FastKML's documentation!
===================================

Fastkml is continually tested with *Travis CI*:

.. image:: https://api.travis-ci.org/cleder/fastkml.png
    :target: https://travis-ci.org/cleder/fastkml

.. image:: https://coveralls.io/repos/cleder/fastkml/badge.png?branch=master
    :target: https://coveralls.io/r/cleder/fastkml?branch=master


Is Maintained and documented:

.. image:: https://pypip.in/v/fastkml/badge.png
    :target: https://pypi.python.org/pypi/fastkml
    :alt: Latest PyPI version

.. image:: https://pypip.in/status/fastkml/badge.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Development Status

.. image:: https://readthedocs.org/projects/fastkml/badge/
    :target: https://fastkml.readthedocs.org/

.. image:: https://www.openhub.net/p/fastkml/widgets/project_thin_badge.gif
    :target: https://www.openhub.net/p/fastkml

Follows best practises:

.. image:: https://landscape.io/github/cleder/fastkml/master/landscape.svg?style=plastic
   :target: https://landscape.io/github/cleder/fastkml/master
   :alt: Code Health


Supports python 2 and 3:

.. image:: https://pypip.in/py_versions/fastkml/badge.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Supported Python versions

.. image:: https://pypip.in/implementation/fastkml/badge.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Supported Python implementations

fastkml is a library to read, write and manipulate KML files. It aims to keep
it simple and fast (using lxml_ if available). "Fast" refers to the time you
spend to write and read KML files, as well as the time you spend to get
acquainted with the library or to create KML objects. It provides a subset of KML
and is aimed at documents that can be read from multiple clients such as
openlayers and google maps rather than to give you all functionality that KML
on google earth provides.

For more details about the KML Specification, check out the `KML Reference
<https://developers.google.com/kml/documentation/kmlreference>`_ on the Google
developers site.

Rationale
---------

Why yet another KML library? None of the existing ones quite fit my
requirements, namely:

* fastkml can *read and write* KML files, feeding fastkml's output back into
  fastkml and serializing it again will result in the same output.
* You can parse any KML snippet, it does not need to be a complete KML
  document.
* It runs on Python 2 and 3.
* It is fully tested and actively maintained.
* Geometries are handled in the `__geo_interface__` standard.
* Minimal dependencies, pure Python.
* If available, lxml_ will be used to increase its speed.

.. toctree::
   :maxdepth: 2

   quickstart
   installing
   usage_guide
   reference_guide
   contributing

.. _lxml: https://pypi.python.org/pypi/lxml
.. _tox: https://pypi.python.org/pypi/tox
.. _kml_reference: https://developers.google.com/kml/documentation/kmlreference
