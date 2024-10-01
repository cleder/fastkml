Introduction
============

KML is an XML geospatial data format and an OGC_ standard that deserves a canonical python implementation.

Fastkml is a library to read, write and manipulate KML files. It aims to keep
it simple and fast (using lxml_ if available). Fast refers to the time you
spend to write and read KML files as well as the time you spend to get
acquainted to the library or to create KML objects. It aims to provide all of
the functionality that KML clients such as `OpenLayers
<http://openlayers.org/>`_, `Google Maps <http://maps.google.com/>`_, and
`Google Earth <http://earth.google.com/>`_ provides.


Geometries are handled as pygeoif_ objects.

Fastkml is continually tested

|test| |cov| |black| |mypy| |commit|

.. |test| image:: https://github.com/cleder/fastkml/actions/workflows/run-all-tests.yml/badge.svg?branch=main
    :target: https://github.com/cleder/fastkml/actions/workflows/run-all-tests.yml
    :alt: Test

.. |cov| image:: http://codecov.io/github/cleder/fastkml/coverage.svg?branch=main
    :target: http://codecov.io/github/cleder/fastkml?branch=main
    :alt: codecov.io

.. |black| image:: https://img.shields.io/badge/code_style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Black

.. |mypy| image:: https://img.shields.io/badge/type_checker-mypy-blue
    :target: http://mypy-lang.org/
    :alt: Mypy

.. |commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

Is Maintained and documented:

|pypi| |status| |license| |doc| |stats| |pyversion| |pyimpl| |dependencies| |downloads|

.. |pypi| image:: https://img.shields.io/pypi/v/fastkml.svg
    :target: https://pypi.python.org/pypi/fastkml
    :alt: Latest PyPI version

.. |status| image:: https://img.shields.io/pypi/status/fastkml.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Development Status

.. |license| image:: https://img.shields.io/pypi/l/fastkml
    :target: https://www.gnu.org/licenses/lgpl-3.0.en.html
    :alt: LGPL - License

.. |doc| image:: https://readthedocs.org/projects/fastkml/badge/
    :target: https://fastkml.readthedocs.org/
    :alt: Documentation

.. |stats| image:: https://www.openhub.net/p/fastkml/widgets/project_thin_badge.gif
    :target: https://www.openhub.net/p/fastkml
    :alt: Statistics from OpenHub

.. |pyversion| image:: https://img.shields.io/pypi/pyversions/fastkml.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Supported Python versions

.. |pyimpl| image:: https://img.shields.io/pypi/implementation/fastkml.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Supported Python implementations

.. |dependencies| image:: https://img.shields.io/librariesio/release/pypi/fastkml
    :target: https://libraries.io/pypi/fastkml
    :alt: Libraries.io dependency status for latest release

.. |downloads| image:: https://static.pepy.tech/badge/fastkml/month
    :target: https://pepy.tech/project/fastkml
    :alt: Downloads


Documentation
=============

You can find all of the documentation for FastKML at `fastkml.readthedocs.org
<https://fastkml.readthedocs.org>`_. If you find something that is missing,
please submit a pull request on `GitHub <https://github.com/cleder/fastkml>`_
with the improvement.

Have a look at Aryan Guptas
`The Definite Guide to FastKML. <https://medium.com/@wwaryan/the-definite-only-guide-to-fastkml-58b8e19b8454>`_

Alternatives
============

`Keytree <https://github.com/Toblerity/keytree>`_ provides a less comprehensive, but more flexible
approach.

Install
========

You can install the package with ``pip install fastkml`` which will pull in all requirements.

Requirements
-------------

* pygeoif_
* arrow_

Optional
---------

* lxml_::

    pip install --pre "fastkml[lxml]"

Limitations
===========

*Tessellate*, *Extrude* and *Altitude Mode* are assigned to a Geometry or
Geometry collection (MultiGeometry). You cannot assign different values of
*Tessellate*, *Extrude* or *Altitude Mode* on parts of a MultiGeometry.

Currently, the only major feature missing for the full Google Earth experience
is the `gx extension
<https://developers.google.com/kml/documentation/kmlreference#kmlextensions>`_.
Please submit a PR with the features you'd like to see implemented.

.. _pygeoif: https://pypi.python.org/pypi/pygeoif/
.. _lxml: https://pypi.python.org/pypi/lxml
.. _arrow: https://pypi.python.org/pypi/arrow
.. _OGC: https://www.ogc.org/standard/kml/
