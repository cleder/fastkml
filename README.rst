FastKML
=======

A Python library for reading, writing and manipulating KML files.

.. contents:: Table of Contents
   :local:
   :depth: 2

.. inclusion-marker-do-not-remove

Introduction
============

KML is an XML geospatial data format and an OGC_ standard that deserves a canonical
python implementation.

Fastkml is a library to read, write and manipulate KML files. It aims to keep
it simple and fast (using lxml_ if available). Fast refers to the time you
spend to write and read KML files as well as the time you spend to get
acquainted to the library or to create KML objects. It aims to provide all of
the functionality that KML clients such as `Marble <https://marble.kde.org/>`_,
`NASA WorldWind <https://github.com/NASAWorldWind>`_,
`Cesium JS <https://cesium.com/>`_, `OpenLayers <https://openlayers.org/>`_,
`Google Maps <http://maps.google.com/>`_, and
`Google Earth <http://earth.google.com/>`_ support.

For more details about the KML Specification, check out the `KML Reference
<https://developers.google.com/kml/documentation/kmlreference>`_ on the Google
developers site.

Features
========

* **Simple and fast**: Easy-to-use API with fast performance
* **Geometry support**: Handles geometries as pygeoif_ objects, compatible with any geometry that implements the ``__geo_interface__`` protocol, such as shapely_
* **Cross-platform compatibility**: Tested on `CPython <https://python.org>`_, `PyPy <https://www.pypy.org/>`_ and `GraalPy <https://www.graalvm.org/python/>`_
* **Python 3.9+**: Works on alternative Python implementations that support Python *>=3.9*

Status
======

**Quality Assurance:**

|test| |hypothesis| |cov| |black| |mypy| |commit|

**Package Information:**

|pypi| |conda-forge| |status| |license| |pyversion| |pyimpl| |dependencies| |downloads|

**Documentation & Community:**

|doc| |stats|

.. |test| image:: https://github.com/cleder/fastkml/actions/workflows/run-all-tests.yml/badge.svg?branch=main
    :target: https://github.com/cleder/fastkml/actions/workflows/run-all-tests.yml
    :alt: Test

.. |hypothesis| image:: https://img.shields.io/badge/hypothesis-tested-brightgreen.svg
    :alt: Tested with Hypothesis
    :target: https://hypothesis.readthedocs.io

.. |cov| image:: https://codecov.io/gh/cleder/fastkml/branch/main/graph/badge.svg?token=VIuhPHq0ow
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

.. |conda-forge| image:: https://img.shields.io/conda/vn/conda-forge/fastkml.svg
    :target: https://anaconda.org/conda-forge/fastkml
    :alt: Conda-Forge

Installation
============

Basic Installation
------------------

Install the package using pip:

.. code-block:: bash

    pip install fastkml

This will install FastKML with all required dependencies.

With Optional Dependencies
--------------------------

For enhanced performance, install with lxml:

.. code-block:: bash

    pip install "fastkml[lxml]"

Using Conda
-----------

You can also install FastKML using conda-forge:

.. code-block:: bash

    conda install -c conda-forge fastkml

Requirements
============

Required Dependencies
---------------------

* pygeoif_ - For geometry handling
* arrow_ - For date and time processing

Optional Dependencies
---------------------

* lxml_ - For improved XML parsing performance (recommended)

Documentation
=============

You can find all of the documentation for FastKML at `fastkml.readthedocs.org <https://fastkml.readthedocs.org>`_. If you find something that is missing, please submit a pull request on `GitHub <https://github.com/cleder/fastkml>`_ with the improvement.

Limitations
===========

Currently, the only major feature missing for the full Google Earth experience
is the `gx extension
<https://developers.google.com/kml/documentation/kmlreference#kmlextensions>`_.

Please submit a PR with the features you'd like to see implemented.

Contributing
============

We welcome contributions! Please check out our `contributing guide <docs/contributing.rst>`_ for guidelines on how to contribute.

.. _pygeoif: https://pypi.python.org/pypi/pygeoif/
.. _lxml: https://pypi.python.org/pypi/lxml
.. _arrow: https://pypi.python.org/pypi/arrow
.. _OGC: https://www.ogc.org/standard/kml/
.. _shapely: https://shapely.readthedocs.io/
