Introduction
============

fastkml is a library to read, write and manipulate kml files. It aims
to keep it simple and fast (using lxml_ if available). Fast refers to
the time you spend to write and read KML files as well as the time you
spend to get aquainted to the library or to create KML objects. It provides
a subset of KML and is aimed at documents that can be read from multiple
clients such as openlayers and google maps rather than to give you all
functionality that KML on google earth provides.

Geometries are handled as pygeoif_ or shapely_ (if installed) objects.

.. _pygeoif: http://pypi.python.org/pypi/pygeoif/
.. _shapely: http://pypi.python.org/pypi/Shapely
.. _lxml: https://pypi.python.org/pypi/lxml
.. _dateutils: https://pypi.python.org/pypi/dateutils
.. _pip: https://pypi.python.org/pypi/pip

fastkml is continually tested with *Travis CI*

.. image:: https://api.travis-ci.org/cleder/fastkml.png
    :target: https://travis-ci.org/cleder/fastkml

.. image:: https://readthedocs.org/projects/fastkml/badge/
    :target: https://fastkml.readthedocs.org/

.. image:: https://coveralls.io/repos/cleder/fastkml/badge.png?branch=master
    :target: https://coveralls.io/r/cleder/fastkml?branch=master

.. image:: https://www.ohloh.net/p/fastkml/widgets/project_thin_badge.gif
    :target: https://www.ohloh.net/p/fastkml


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

You can install all of the requirements for working with fastkml by using pip_::

    pip install -r requirements.txt

.. note::

    Shapely_ requires that libgeos be installed on your system. ``apt-get
    install libgeos-dev`` will install these requirements for you on Debian-
    based systems.


Limitations
===========

*Tesselate*, *Extrude* and *Altitude Mode* are assigned to a Geometry or
Geometry collection (MultiGeometry). You cannot assign diffrent values of
*Tesselate*, *Extrude* or *Altitude Mode* on parts of a MultiGeometry.
