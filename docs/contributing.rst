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

Start by submitting a pull request on GitHub against the ``develop`` branch of the
repository. Your pull request should provide a good description of the change
you are making, and/or the bug that you are fixing.


Running Tests Locally
---------------------

You can make use of tox_ >= 1.8 to test the entire matrix of options:

* with / without lxml
* py36,py37,py38,py39

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
    SKIPPED:  py36: InterpreterNotFound: python3.6
      py37: commands succeeded
      py38: commands succeeded
      py39: commands succeeded
    SKIPPED:  py36-lxml: InterpreterNotFound: python3.6
      py37-lxml: commands succeeded
      py38-lxml: commands succeeded
      py39-lxml: commands succeeded
      pep8: commands succeeded
      docs: commands succeeded
      congratulations :)

You are primarily looking for the ``congratulations :)`` line at the bottom,
signifying that the code is working as expected on all configurations
available.

.. _tox: https://pypi.python.org/pypi/tox

coverage
~~~~~~~~

You can also run the tests with coverage_ to see which lines are covered by the
tests. This is useful for writing new tests to cover any uncovered lines::

    pytest tests --cov=fastkml --cov=tests --cov-report=xml


pre-commit
~~~~~~~~~~~

Install the ``pre-commit`` hook with::

    pip install pre-commit
    pre-commit install

and check the code with::

    pre-commit run --all-files
