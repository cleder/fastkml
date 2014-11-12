Contributing
============

Getting Involved
----------------

So you'd like to contribute? That's awesome! We would love to have your help,
especially in the following ways:

* Making Pull Requests for code, tests, or docs
* Commenting on open issues and pull requests
* Suggesting new features


Pull Requests
-------------

Start by submitting a pull request on GitHub against the `master` branch of the
repository. Your pull request should provide a good description of the change
you are making, and/or the bug that you are fixing. This will then trigger a
build in `Travis-CI`_ where your contribution will be tested to verify it does
not break existing functionality.

.. _travis-ci: https://travis-ci.org/cleder/fastkml


Running Tests Locally
---------------------

You can make use of tox_ >= 1.8 to test the entire matrix of options:

* with / without lxml
* pygeoif vs shapely
* py26,py27,py32,py33,py34

as well as pep8 style checking in a single call (this approximates what happens
when the package is run through Travis-CI)

.. code-block:: python

    # Install tox
    pip install tox>=1.8

    # Run tox
    tox

    # Or optionally
    # (to skip tests for Python versions you do not have installed)
    tox --skip-missing-interpreters

This will run through all of the tests and produce an output similar to::

    ______________________________________________________ summary ______________________________________________________
    SKIPPED:  py26: InterpreterNotFound: python2.6
      py27: commands succeeded
    SKIPPED:  py32: InterpreterNotFound: python3.2
    SKIPPED:  py33: InterpreterNotFound: python3.3
      py34: commands succeeded
    SKIPPED:  py26-shapely: InterpreterNotFound: python2.6
    SKIPPED:  py26-lxml: InterpreterNotFound: python2.6
      py27-shapely: commands succeeded
      py27-lxml: commands succeeded
    SKIPPED:  py32-shapely: InterpreterNotFound: python3.2
    SKIPPED:  py32-lxml: InterpreterNotFound: python3.2
    SKIPPED:  py33-shapely: InterpreterNotFound: python3.3
    SKIPPED:  py33-lxml: InterpreterNotFound: python3.3
      py34-shapely: commands succeeded
      py34-lxml: commands succeeded
    SKIPPED:  py26-shapely-lxml: InterpreterNotFound: python2.6
      py27-shapely-lxml: commands succeeded
    SKIPPED:  py32-shapely-lxml: InterpreterNotFound: python3.2
    SKIPPED:  py33-shapely-lxml: InterpreterNotFound: python3.3
      py34-shapely-lxml: commands succeeded
      pep8: commands succeeded
      congratulations :)

You are primarily looking for the ``congratulations :)`` line at the bottom,
signifying that the code is working as expected on all configurations
available.

.. _tox: https://pypi.python.org/pypi/tox
