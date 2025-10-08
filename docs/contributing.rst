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

Fork the repository and clone your fork to your local machine:

.. code-block:: bash

    git clone https://github.com/yourusername/fastkml.git
    cd fastkml
    git checkout develop

Next, set up a virtual environment. This helps to manage dependencies and avoid conflicts:

.. code-block:: bash

    python3 -m venv .venv
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

You can also run the tests with `coverage <https://coverage.readthedocs.io/>`_
to see which lines are covered by the tests.
This is useful for writing new tests to cover any uncovered lines:

.. code-block:: bash

    pytest  --cov=fastkml --cov-report=term

To get a report on the individual lines that are not covered, use the
``--cov-report=term-missing`` option, or generate an HTML report with
``--cov-report=html``.
Some editor extensions can also show the coverage directly in the editor, notably
`coverage-gutter <https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters>`_
for VSCode, which needs the output to be in the ``xml`` format produced with
``--cov-report=xml``.

Building the Documentation
-------------------------

To build and preview the documentation locally:

1. **Install documentation dependencies** (if not already installed):

    .. code-block:: bash

        pip install -r docs/requirements.txt

2. **Build the HTML documentation**:

    .. code-block:: bash

        cd docs
        make html

    The generated HTML files will be in `docs/_build/html`. Open `index.html` in your browser to preview.

If you encounter issues, ensure you have Sphinx and the required extensions installed, and that your virtual environment is activated.

Submitting Changes
------------------

Once you've made your changes and ensured that all tests pass, you can submit a pull request:

Tips:

* Write clear and concise commit messages.
* Follow the existing code style and conventions.
* Reference any related issues in your pull request description.
* Ensure your changes are well-tested.
* Commit to the ``develop`` branch, not ``main``.
* Avoid large, monolithic pull requests; smaller, focused PRs are easier to review.
* Commit often with logical chunks of work.
* Open a draft pull request early to get feedback.
* Be patient and responsive to feedback on your pull request.
* Celebrate your contribution to the project! Add a line to the ``HISTORY.rst`` file
  in the "unreleased" section, following the existing format.

We appreciate your contributions and look forward to collaborating with you!
