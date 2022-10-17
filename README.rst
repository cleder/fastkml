Introduction
============

KML is an XML geospatial data format and an `OGC standard <https://www.ogc.org/search/content/kml>`_
that deserves a canonical python implementation.

Fastkml is a library to read, write and manipulate KML files. It aims to keep
it simple and fast (using lxml_ if available). Fast refers to the time you
spend to write and read KML files as well as the time you spend to get
acquainted to the library or to create KML objects. It aims to provide all of
the functionality that KML clients such as `OpenLayers
<http://openlayers.org/>`_, `Google Maps <http://maps.google.com/>`_, and
`Google Earth <http://earth.google.com/>`_ provides.


Geometries are handled as pygeoif_ objects.

.. _pygeoif: http://pypi.python.org/pypi/pygeoif/
.. _lxml: https://pypi.python.org/pypi/lxml
.. _dateutils: https://pypi.python.org/pypi/dateutils
.. _pip: https://pypi.python.org/pypi/pip

Fastkml is continually tested

.. image:: https://github.com/cleder/fastkml/actions/workflows/run-all-tests.yml/badge.svg?branch=main
    :target: https://github.com/cleder/fastkml/actions/workflows/run-all-tests.yml
    :alt: Test

.. image:: http://codecov.io/github/cleder/fastkml/coverage.svg?branch=main
    :target: http://codecov.io/github/cleder/fastkml?branch=main
    :alt: codecov.io

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Black

Is Maintained and documented:

.. image:: https://img.shields.io/pypi/v/fastkml.svg
    :target: https://pypi.python.org/pypi/fastkml
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/status/fastkml.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Development Status

.. image:: https://readthedocs.org/projects/fastkml/badge/
    :target: https://fastkml.readthedocs.org/
    :alt: Documentation

.. image:: https://www.openhub.net/p/fastkml/widgets/project_thin_badge.gif
    :target: https://www.openhub.net/p/fastkml
    :alt: Statistics from OpenHub

.. image:: https://img.shields.io/pypi/pyversions/fastkml.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/implementation/fastkml.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Supported Python implementations

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
* dateutils_

Optional
---------

* lxml_

You can install all of the requirements for working with FastKML by using
pip_::

    pip install -r requirements.txt


Limitations
===========

*Tesselate*, *Extrude* and *Altitude Mode* are assigned to a Geometry or
Geometry collection (MultiGeometry). You cannot assign different values of
*Tesselate*, *Extrude* or *Altitude Mode* on parts of a MultiGeometry.

Currently, the only major feature missing for the full Google Earth experience
is the `gx extension
<https://developers.google.com/kml/documentation/kmlreference#kmlextensions>`_.
Please submit a PR with the features you'd like to see implementd.
