from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='fastkml',
      version=version,
      description="Fast KML processing for python",
      long_description="""\
Create and read KML Files""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
