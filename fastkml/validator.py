# Copyright (C) 2024 Christian Ledermann
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
"""Validate KML files against the XML schema."""

import logging
import pathlib
from functools import lru_cache
from types import ModuleType
from typing import TYPE_CHECKING
from typing import Final
from typing import cast

from fastkml import config
from fastkml.types import Element

if TYPE_CHECKING:
    from collections.abc import Iterable

    from lxml import etree
    from typing_extensions import Protocol

    class _LogEntry(Protocol):
        """
        A single entry of an lxml `_ErrorLog`, which lxml-stubs omits.

        Other etree-compatible backends (e.g. pyuppsala) provide `message`
        but not `path`.
        """

        message: str
        path: str | None


__all__ = [
    "get_schema_parser",
    "validate",
]


logger = logging.getLogger(__name__)

MUTUAL_EXCLUSIVE: Final = "Only one of element and file_to_validate can be provided."
REQUIRE_ONE_OF: Final = "Either element or file_to_validate must be provided."


@lru_cache(maxsize=16)
def _build_schema_parser(
    etree_module: ModuleType,
    schema: pathlib.Path,
) -> "etree.XMLSchema":
    # Build from the file path (not a parsed tree) so relative
    # xsd:import/xsd:include schemaLocations resolve against the schema's own
    # directory; some backends (e.g. pyuppsala) lose that location when given
    # an already-parsed tree instead of a file.
    return etree_module.XMLSchema(file=schema)


def get_schema_parser(
    schema: pathlib.Path | None = None,
) -> "etree.XMLSchema":
    """
    Parse the XML schema.

    Args:
    ----
        schema: The path to the XML schema file.

    Returns:
    -------
        The parsed XML schema.

    To clear the cache call get_schema_parser.cache_clear().

    """
    if schema is None:
        schema = pathlib.Path(__file__).parent / "schema" / "ogckml22.xsd"
    # Keyed on the currently active etree module too, not just `schema`: a
    # process that calls `config.set_etree_implementation()` to switch
    # backends (e.g. between test runs, or a real caller alternating
    # implementations) must not be handed back a schema object built for the
    # previously active backend.
    return _build_schema_parser(config.etree, schema)


get_schema_parser.cache_clear = (  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    _build_schema_parser.cache_clear
)


def handle_validation_error(
    schema_parser: "etree.XMLSchema",
    element: Element,
) -> None:
    """
    Log the validation error in its XML context.

    Args:
    ----
        schema_parser: The parsed XML schema.
        element: The element to validate.

    """
    # lxml-stubs' `_ErrorLog` is an empty stub with no `__iter__` or entry
    # attributes, even though the real lxml class supports both.
    log = cast("Iterable[_LogEntry]", schema_parser.error_log)
    for error_entry in log:
        path = getattr(error_entry, "path", None)
        try:
            matches = cast("list[Element]", element.xpath(path) if path else [])
            parent = matches[0].getparent()
        except (config.etree.XPathEvalError, IndexError):
            parent = element
        if parent is None:
            parent = element
        error_in_xml = config.etree.tostring(
            parent,
            encoding="UTF-8",
            pretty_print=True,
        ).decode(
            "UTF-8",
        )
        logger.error(
            "Error <%s> in XML:\n %s",
            error_entry.message,
            error_in_xml,
        )


def assert_valid(schema_parser: "etree.XMLSchema", element: Element) -> None:
    """
    Raise `AssertionError` if `element` does not validate against `schema_parser`.

    lxml's `XMLSchema.assert_()` already raises `AssertionError`; other
    etree-compatible backends (e.g. pyuppsala) only provide `assertValid()`,
    which raises its own exception type, so it is re-raised as
    `AssertionError` here to give callers a backend-independent contract.
    """
    if hasattr(schema_parser, "assert_"):
        schema_parser.assert_(element)  # noqa: PT009
        return
    try:
        schema_parser.assertValid(element)
    except Exception as error:
        raise AssertionError(str(error)) from error


def validate(
    *,
    schema: pathlib.Path | None = None,
    element: Element | None = None,
    file_to_validate: pathlib.Path | None = None,
) -> bool | None:
    """
    Validate a KML file against the XML schema.

    Args:
    ----
        schema: The path to the XML schema file.
        element: The element to validate.
        file_to_validate: The file to validate.

    Returns:
    -------
            True if the file or element is valid.
            Raises an AssertionError if validation fails.
            Returns None if the schema parser is unavailable.

    """
    if element is None and file_to_validate is None:
        raise ValueError(REQUIRE_ONE_OF)
    if element is not None and file_to_validate is not None:
        raise ValueError(MUTUAL_EXCLUSIVE)

    try:
        schema_parser = get_schema_parser(schema)
    except AttributeError:
        return None

    if file_to_validate is not None:
        element = config.etree.parse(file_to_validate).getroot()
    assert element is not None  # noqa: S101
    try:
        assert_valid(schema_parser, element)
    except AssertionError:
        handle_validation_error(schema_parser, element)
        raise
    return True
