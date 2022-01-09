Configuration
==============

ElementTree configuration
--------------------------

By default, fastkml uses the standard libraries
``xml.etree.ElementTree`` or, if installed, ``lxml.etree``
as its parser, but you can change this by setting the
``fastkml.config.etree`` module variable to a different
implementation.

E.g. if you have lxml installed, but you want to use the
standard ``xml.etree.ElementTree``, you can do this::

    >>> import fastkml.config
    >>> import xml.etree.ElementTree
    >>> fastkml.config.set_etree_implementation(xml.etree.ElementTree)
    >>> fastkml.config.set_default_namespaces()

You can pass any module that implements the ``ElementTree`` interface
to the ``set_etree_implementation`` function.

Registering additional namespaces
----------------------------------
The ``fastkml.config.set_default_namespaces`` function registers
the ``kml``, ``gx`` and ``atom`` namespaces with the ``ElementTree``.
You can add any other namespaces you want to use by calling
``fastkml.config.register_namespace`` with the namespace prefix and
the namespace URI.

.. code-block:: python

    >>> import fastkml.config
    >>> import xml.etree.ElementTree
    >>> fastkml.config.set_etree_implementation(xml.etree.ElementTree)
    >>> fastkml.config.register_namespace(foo='http://foo.com')
    >>> config.set_default_namespaces()
