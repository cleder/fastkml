Contributing
============

Getting Involved
----------------

So you'd like to contribute? That's awesome! We would love to have your help,
especially in the following ways:

* Making Pull Requests for code, tests, or docs
* Commenting on open issues and pull requests
* Suggesting new features

Setting Up Your Environment
---------------------------

First, clone the repository:

.. code-block:: bash

    git clone https://github.com/yourusername/fastkml.git
    cd fastkml

Next, set up a virtual environment. This helps to manage dependencies and avoid conflicts:

.. code-block:: bash

    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Then, install the required packages:

.. code-block:: bash

    pip install -e ".[dev]"

Install the ``pre-commit`` hook with:

.. code-block:: bash

    pre-commit install

and check the code with:

.. code-block:: bash

    pre-commit run --all-files

Running the Tests
-----------------

To run the tests, simply use:

.. code-block:: bash

    pytest

coverage
~~~~~~~~

You can also run the tests with coverage_ to see which lines are covered by the
tests. This is useful for writing new tests to cover any uncovered lines::

.. code-block:: bash

    pytest  --cov=fastkml --cov-report=term


Tips
----

- Commit often, commit early.
- Make a draft PR while you are still working on it to give your work some visibility.
