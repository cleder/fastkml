from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys, os

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


version = '0.6'

setup(name='fastkml',
      version=version,
      description="Fast KML processing in python",
      long_description=open(
              "README.rst").read() + "\n" +
              open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
              open(os.path.join("docs", "TODO.txt")).read(),
      classifiers=[
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='GIS KML Google Maps OpenLayers',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='https://github.com/cleder/fastkml',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      tests_require=['pytest'],
      cmdclass = {'test': PyTest},
      install_requires=[
          # -*- Extra requirements: -*-
          'pygeoif',
          'python-dateutil',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
