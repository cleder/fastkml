Installation
============

fastkml works with CPython version 2.6, 2.7, 3.2, 3.3, 3.4 and is
continually tested with TravisCI for these version. The tests break
intermittently for pypy and pypy3 so they are not tested but *should* work,
Jython and IronPython are not tested but *should* work.

.. image:: https://api.travis-ci.org/cleder/fastkml.png
    :target: https://travis-ci.org/cleder/fastkml

fastkml works on Unix/Linux, OS X, and Windows.

Install it with ``pip install fastkml`` or ``easy_install fastkml``.

If you use fastkml extensively or need to process big KML files, consider
installing lxml_ as it speeds up processing.

You can install all requirements for working with fastkml by using pip_ from
the base of the source tree::

    pip install -r requirements.txt

.. note::

    Shapely_ requires that libgeos be installed on your system. ``apt-get
    install libgeos-dev`` will install these requirements for you on Debian-
    based systems.

.. _lxml: https://pypi.python.org/pypi/lxml
.. _pip: https://pypi.python.org/pypi/pip
.. _shapely: http://pypi.python.org/pypi/Shapely
