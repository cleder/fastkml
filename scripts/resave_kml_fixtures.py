# Copyright (C) 2012 - 2025  Christian Ledermann
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
"""
Re-serialize every .kml fixture under tests/ogc_conformance/data/kml through lxml.

Parses each file with lxml and writes it back to the same path, unchanged in
content but normalized through lxml's parser/serializer round trip.
"""

import logging
from pathlib import Path

from lxml import etree

logger = logging.getLogger(__name__)

DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "tests"
    / "ogc_conformance"
    / "data"
    / "kml"
)


def main() -> None:
    """Reparse and rewrite every .kml fixture under DATA_DIR in place."""
    parser = etree.XMLParser(
        strip_cdata=False,
        remove_blank_text=False,
        remove_comments=False,
    )
    for path in sorted(DATA_DIR.rglob("*.kml")):
        tree = etree.parse(str(path), parser)
        tree.write(
            str(path),
            xml_declaration=True,
            encoding=tree.docinfo.encoding or "UTF-8",
        )
        logger.info("resaved %s", path)


if __name__ == "__main__":
    main()
