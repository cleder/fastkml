Architecture
============

``fastkml`` is organized around a small set of core abstractions: XML base classes, a
registry that maps Python attributes to XML nodes, and domain modules that model KML
features, geometry, styling, timing, and overlays. The public entry point in
``fastkml/__init__.py`` re-exports the main classes, then imports
``fastkml/_registry_setup.py`` so delayed registrations such as ``Track.extended_data`` and
``Update`` action payloads are available before user code parses documents.

Module layout
-------------

``fastkml.__init__`` pulls together the rest of the package:

* ``kml.py`` owns the root ``KML`` wrapper (``kml.KML``), which in turn relies on
  ``base._XMLObject`` for parsing and serialization.
* ``containers.py`` and ``features.py`` define the recursive tree of user-visible features,
  and both depend on ``geometry.py``, ``styles.py``, ``data.py``, ``times.py``, and
  ``views.py`` for the fields a feature can carry.
* ``base._XMLObject`` sits on top of ``registry.py``, which in turn relies on the helper
  functions in ``helpers.py``.
* ``network_link_control.py`` (update payloads) also builds on ``base._XMLObject``.
* The ``gx`` package depends on both ``geometry.py`` and ``data.py`` for its track and
  extended-data extensions.

Key Design Decisions
---------------------

Registry-driven XML mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The central decision lives in ``fastkml/registry.py`` and ``fastkml/base.py``: parsing and
serialization rules are registered outside the classes themselves.
``_XMLObject.populate_element()`` iterates through ``registry.get(self.__class__)``, while
``_XMLObject._get_kwargs()`` walks the same registry in reverse during parsing. That keeps
constructors focused on domain state and lets the library extend behavior without copying
XML code into every model.

A shared XML foundation
^^^^^^^^^^^^^^^^^^^^^^^^

Nearly every public class inherits from ``_XMLObject`` or ``_BaseObject``. ``_XMLObject`` in
``fastkml/base.py`` provides ``from_string()``, ``to_string()``, ``etree_element()``,
``class_from_element()``, and ``validate()``. ``_BaseObject`` in ``fastkml/kml_base.py`` adds
common KML object attributes such as ``id`` and ``target_id``. This means containers,
styles, geometry objects, and ``NetworkLinkControl`` behave consistently when you parse,
compare, serialize, or validate them.

Geometry as an adapter layer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Geometry objects in ``fastkml/geometry.py`` are wrappers around ``pygeoif`` geometry
instances rather than bespoke coordinate containers. ``Placemark.__init__()`` in
``fastkml/features.py`` accepts either a prebuilt KML geometry object or a generic geometry
and converts it through ``create_kml_geometry()``. That reduces friction when your
application already uses geometry objects elsewhere.

Configurable XML backend
^^^^^^^^^^^^^^^^^^^^^^^^^

``fastkml/config.py`` tries to import ``lxml.etree`` first and falls back to
``xml.etree.ElementTree``. The code paths in ``kml.py``, ``base.py``, and ``validator.py``
are written so the same object model works either way. ``lxml`` unlocks pretty-printing and
schema validation; the fallback keeps the dependency surface small for simple workloads.
See :doc:`configuration` for how to select the backend explicitly.

Data Lifecycle
--------------

Parsing and serialization mirror each other:

* **Parsing**: ``KML.parse()`` in ``fastkml/kml.py`` reads the XML, infers the namespace
  from the root tag, merges user-provided namespaces with ``config.NAME_SPACES``, and
  delegates to ``_XMLObject.class_from_element()``. That method asks the registry
  (``registry._get_kwargs()``) for the constructor keyword arguments matching every
  registered field, then instantiates the class tree from the parsed kwargs.
* **Serialization**: ``to_string()`` (or ``write()``) calls ``etree_element()``, which calls
  ``populate_element()``. That method visits every registry item for the class and calls
  its ``set_element`` helper from ``fastkml/helpers.py`` to write text nodes, attributes, or
  nested child objects onto the XML tree.
* In between, your code mutates the plain Python object tree returned by ``parse()`` —
  there is no separate "edit mode"; see :doc:`parse_edit_write`.

How The Pieces Fit Together
----------------------------

* ``kml.py`` owns the root document wrapper, file parsing, and KML versus KMZ writing.
* ``containers.py`` and ``features.py`` define the recursive tree of user-visible features.
* ``geometry.py``, ``model.py``, ``views.py``, ``times.py``, and ``overlays.py`` model
  specialized KML subtrees referenced by features.
* ``data.py`` and ``gx/data.py`` handle untyped, typed, and array-based metadata.
* ``styles.py`` centralizes shared style definitions and style maps that documents and
  features can reference.
* ``network_link_control.py`` models update payloads for remote KML refresh workflows.
* ``utils.py``, ``validator.py``, and ``config.py`` provide traversal, schema validation,
  and backend configuration utilities.

The result is a library that is object-oriented at the edges but declarative in the middle.
That balance is why fastkml can cover a broad slice of the KML spec without turning every
model class into a custom parser.
