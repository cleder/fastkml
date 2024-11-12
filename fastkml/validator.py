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
from typing import TYPE_CHECKING
from typing import Final
from typing import Optional

from fastkml import config
from fastkml.types import Element

if TYPE_CHECKING:
    import contextlib

    with contextlib.suppress(ImportError):
        from lxml import etree

__all__ = [
    "get_schema_parser",
    "validate",
]


logger = logging.getLogger(__name__)

MUTUAL_EXCLUSIVE: Final = "Only one of element and file_to_validate can be provided."
REQUIRE_ONE_OF: Final = "Either element or file_to_validate must be provided."


@lru_cache(maxsize=16)
def get_schema_parser(
    schema: Optional[pathlib.Path] = None,
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
    return config.etree.XMLSchema(config.etree.parse(schema))


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
    log = schema_parser.error_log
    for error_entry in log:
        try:
            parent = element.xpath(error_entry.path)[  # type: ignore[attr-defined]
                0
            ].getparent()
        except config.etree.XPathEvalError:
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


def validate(
    *,
    schema: Optional[pathlib.Path] = None,
    element: Optional[Element] = None,
    file_to_validate: Optional[pathlib.Path] = None,
) -> Optional[bool]:
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
        element = config.etree.parse(file_to_validate)
    assert element is not None  # noqa: S101
    try:
        schema_parser.assert_(element)  # noqa: PT009
    except AssertionError:
        handle_validation_error(schema_parser, element)
        raise
    return True
