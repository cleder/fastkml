from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='fastkml',
      version=version,
      description="Fast KML processing in python",
      long_description=open(
              "README.rst").read() + "\n" +
              open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python",
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
      install_requires=[
          # -*- Extra requirements: -*-
          'pygeoif',
          'python-dateutil',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
