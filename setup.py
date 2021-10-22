import os
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name="fastkml",
    version="1.0.alpha.0",
    description="Fast KML processing in python",
    long_description=(
        open("README.rst").read()
        + "\n"
        + open(os.path.join("docs", "HISTORY.txt")).read()
    ),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        # "Development Status :: 5 - Production/Stable",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
    ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords="GIS KML Google Maps OpenLayers",
    author="Christian Ledermann",
    author_email="christian.ledermann@gmail.com",
    url="https://github.com/cleder/fastkml",
    license="LGPL",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    tests_require=["pytest"],
    cmdclass={"test": PyTest},
    install_requires=[
        # -*- Extra requirements: -*-
        "pygeoif>=1.0b1",
        "python-dateutil",
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
