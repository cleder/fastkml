Working with KML Files
======================

Import the necessary modules:

.. code-block:: pycon

    >>> from fastkml.utils import find_all
    >>> from fastkml import KML
    >>> from fastkml import Placemark, Point


Open a KML file:

.. code-block:: pycon

    >>> k = KML.parse("docs/Document-clean.kml")

Extract all placemarks and print their geometries.
The function ``find_all`` recursively searches a KML document for elements of a specific
type and returns an iterator of all matching elements found in the document tree.

.. code-block:: pycon

    >>> placemarks = list(find_all(k, of_type=Placemark))
    >>> for p in placemarks:
    ...     print(p.geometry)  # doctest: +ELLIPSIS
    ...
    POINT Z (-123.93563168 49.16716103 5.0)
    POLYGON Z ((-123.940449937288 49.16927524669021 17.0, ...
    >>> pts = list(find_all(k, of_type=Point))
    >>> for point in pts:
    ...     print(point.geometry)
    ...
    POINT Z (-123.93563168 49.16716103 5.0)
    POINT Z (-123.1097 49.2774 0.0)
    POINT Z (-123.028369 49.26107900000001 0.0)
    POINT Z (-123.3215766 49.2760338 0.0)
    POINT Z (-123.2643704 49.3301853 0.0)
    POINT Z (-123.2477084 49.2890857 0.0)



``find_all`` can also search for arbitrary   elements by their attributes, by passing the
attribute name and value as keyword arguments:


.. code-block:: pycon

    >>> al = list(find_all(k, name="Vancouver Film Studios"))
    >>> al[0].name
    'Vancouver Film Studios'
    >>> al[0].get_tag_name()
    'Placemark'
    >>> list(find_all(k, href="http://www.vancouverfilmstudios.com/"))  # doctest: +ELLIPSIS
    [fastkml.atom.Link(ns=...
