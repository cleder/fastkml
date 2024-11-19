Changelog
=========

1.0.0dev0 (unreleased)
----------------------


1.0 (2024/11/19)
-----------------

- Drop Python 2 support
- Use pygeoif >=1.0
- Drop shapely native support
- Add type annotations
- refactor
- Use arrow instead of dateutil
- Add an informative ``__repr__``

0.12 (2020/09/23)
-----------------

- add track and multi track [dericke]
- remove travis, add github actions
- raise error and debug log for no geometries found case [hyperknot]
- protect AttributeError from data element without value [fpassaniti]
- examples and fixes [heltonbiker]
- improve documentation [whatnick]

0.11.1 (2015/07/13)
-------------------

- add travis deploy to travis.yml

0.11 (2015/07/10)
-----------------

-  handle coordinates tuples which contain spaces

0.10 (2015/06/09)
-----------------

- Fix bug when the fill or outline attributes of a PolyStyle are float strings

0.9 (2014/10/17)
-----------------

- Add tox.ini for running tests using tox [Ian Lee]
- Add documentation, hosted at https://fastkml.readthedocs.org [Ian Lee]

0.8 (2014/09/18)
-----------------

- Add support for address and phoneNumber [Ian Lee]
- Add support for Ground Overlay kml [Ian Lee]

0.7 (2014/08/01)
----------------

- Handle case where Document booleans (visibility,isopen) are 'true' or 'false' [jwhelland]
- test case additions and lxml warning [Ian Lee]
- pep8-ify source code (except test_main.py) [Ian Lee]
- pyflakes-ify source code (except __init__.py) [Ian Lee]

0.6 (2014/05/29)
----------------

- add Schema
- add SchemaData
- make use of lxmls default namespace

0.5 (2013/10/23)
-----------------

- handle big files with huge_tree for lxml [Egil Moeller]
- bugfixes


0.4 (2013/09/05)
-----------------

- adds the ability to add untyped extended data / named value pairs [Denis Krienbuehl]

0.3 (2012/11/15)
-----------------

- specify minor python versions tested with Travis CI
- add support for tessellation, altitudeMode and extrude to Geometries
- move implementation of geometry from kml.Placemark to geometry.Geometry
- add support for heterogenous GeometryCollection
- python 3 compatible
- fix test for python 3
- change license to LGPL
- register namespaces for a more pleasant, human readable xml output

0.2 (2012/07/27)
-----------------

- remove dependency on shapely
- add more functionality


0.1.1 (2012/06/29)
------------------

- add MANIFEST.in

0.1 (2012/06/27)
----------------

- initial release
