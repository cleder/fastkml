Installation
============

fastkml works with CPython and Pypy version 3.7+ and is
continually tested for these version.
Jython and IronPython are not tested but *should* work.

.. image:: https://api.travis-ci.org/cleder/fastkml.png
    :target: https://travis-ci.org/cleder/fastkml

fastkml works on Unix/Linux, OS X, and Windows.

Install it with ``pip install fastkml``.

If you use fastkml extensively or need to process big KML files, consider
installing lxml_ as it speeds up processing.

You can install all requirements for working with fastkml by using pip_ from
the base of the source tree::

    pip install -r requirements.txt

.. _lxml: https://pypi.python.org/pypi/lxml
.. _pip: https://pypi.python.org/pypi/pip
