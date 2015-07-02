Introduction
============

Fastkml is a library to read, write and manipulate KML files. It aims to keep
it simple and fast (using lxml_ if available). Fast refers to the time you
spend to write and read KML files as well as the time you spend to get
aquainted to the library or to create KML objects. It aims to provide all of
the functionality that KML clients such as `OpenLayers
<http://openlayers.org/>`_, `Google Maps <http://maps.google.com/>`_, and
`Google Earth <http://earth.google.com/>`_ provides.


Geometries are handled as pygeoif_ or, if installed, shapely_ objects.

.. _pygeoif: http://pypi.python.org/pypi/pygeoif/
.. _shapely: http://pypi.python.org/pypi/Shapely
.. _lxml: https://pypi.python.org/pypi/lxml
.. _dateutils: https://pypi.python.org/pypi/dateutils
.. _pip: https://pypi.python.org/pypi/pip

Fastkml is continually tested with *Travis CI*:

.. image:: https://api.travis-ci.org/cleder/fastkml.png
    :target: https://travis-ci.org/cleder/fastkml
    :alt: Tests

.. image:: https://coveralls.io/repos/cleder/fastkml/badge.png?branch=master
    :target: https://coveralls.io/r/cleder/fastkml?branch=master
    :alt: coveralls.io

.. image:: http://codecov.io/github/cleder/fastkml/coverage.svg?branch=master
    :target: http://codecov.io/github/cleder/fastkml?branch=master
    :alt: codecov.io

Is Maintained and documented:

.. image:: https://pypip.in/v/fastkml/badge.png
    :target: https://pypi.python.org/pypi/fastkml
    :alt: Latest PyPI version

.. image:: https://pypip.in/status/fastkml/badge.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Development Status

.. image:: https://readthedocs.org/projects/fastkml/badge/
    :target: https://fastkml.readthedocs.org/
    :alt: Documentation

.. image:: https://badge.waffle.io/cleder/fastkml.png?label=ready&title=Ready
    :target: https://waffle.io/cleder/fastkml
    :alt: 'Stories in Ready'

.. image:: https://www.openhub.net/p/fastkml/widgets/project_thin_badge.gif
    :target: https://www.openhub.net/p/fastkml
    :alt: Statistics from OpenHub

Supports python 2 and 3:

.. image:: https://pypip.in/py_versions/fastkml/badge.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Supported Python versions

.. image:: https://pypip.in/implementation/fastkml/badge.svg
    :target: https://pypi.python.org/pypi/fastkml/
    :alt: Supported Python implementations

Documentation
=============

You can find all of the documentation for FastKML at `fastkml.readthedocs.org
<https://fastkml.readthedocs.org>`_. If you find something that is missing,
please submit a pull request on `GitHub <https://github.com/cleder/fastkml>`_
with the improvement.


Install
========

You can install the package with ``pip install fastkml`` or ``easy_install
fastkml`` which should also pull in all requirements.

Requirements
-------------

* pygeoif_
* dateutils_

Optional
---------

* lxml_
* shapely_

You can install all of the requirements for working with FastKML by using
pip_::

    pip install -r requirements.txt

.. note::

    Shapely_ requires that libgeos be installed on your system. ``apt-get
    install libgeos-dev`` will install these requirements for you on Debian-
    based systems.


Limitations
===========

*Tesselate*, *Extrude* and *Altitude Mode* are assigned to a Geometry or
Geometry collection (MultiGeometry). You cannot assign different values of
*Tesselate*, *Extrude* or *Altitude Mode* on parts of a MultiGeometry.

Currently, the only major feature missing for the full Google Earth experience
is the `gx extension
<https://developers.google.com/kml/documentation/kmlreference#kmlextensions>`_.
This will most likely be added after the 1.0 version release.

You can find the complete list of current issues on `GitHub
<https://github.com/cleder/fastkml/issues>`_.
