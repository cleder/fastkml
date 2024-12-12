import pathlib

from xmldiff import formatting
from xmldiff import main

import fastkml
import fastkml.validator
from tests.base import Lxml

BASEDIR = pathlib.Path(__file__).parent
KMLFILEDIR = BASEDIR / "data" / "kml"


class TestLxml(Lxml):
    """Test with the standard library."""

    def test_document_clean(self) -> None:
        clean_doc = KMLFILEDIR / "Document-clean.kml"
        expected_xml = clean_doc.open("rb").read()
        formatter = formatting.XmlDiffFormatter(normalize=formatting.WS_BOTH)
        # TODO: Add NetworkLinkControl parser
        doc = fastkml.kml.KML.parse(clean_doc)

        diff = main.diff_texts(
            doc.to_string().encode("utf-8"),
            expected_xml,
        )

        assert fastkml.validator.validate(file_to_validate=clean_doc)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_docunemt_empty_placemark_without_id(self) -> None:
        empty_placemark = KMLFILEDIR / "emptyPlacemarkWithoutId.xml"
        expected_xml = empty_placemark.open("rb").read()
        formatter = formatting.DiffFormatter(normalize=formatting.WS_BOTH)

        doc = fastkml.kml.KML.parse(empty_placemark)

        diff = main.diff_texts(
            doc.to_string(),
            expected_xml,
        )
        assert diff == []
        assert fastkml.validator.validate(file_to_validate=empty_placemark)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_document_deprecated(self) -> None:
        deprecated_doc = KMLFILEDIR / "Document-deprecated.kml"
        expected_xml = deprecated_doc.open("rb").read()
        formatter = formatting.DiffFormatter(normalize=formatting.WS_BOTH)

        doc = fastkml.kml.KML.parse(deprecated_doc)

        diff = main.diff_texts(
            doc.to_string(),
            expected_xml,
        )

        # assert diff is None

    def test_document_places(self) -> None:
        places_doc = KMLFILEDIR / "Document-places.kml"
        expected_xml = places_doc.open("rb").read()
        formatter = formatting.DiffFormatter(normalize=formatting.WS_BOTH)

        doc = fastkml.kml.KML.parse(places_doc)

        diff = main.diff_texts(
            doc.to_string(precision=2),
            expected_xml,
            formatter=formatter,
        )

        assert diff == ""
        assert fastkml.validator.validate(file_to_validate=places_doc)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_document_kml_samples(self) -> None:
        kml_samples_doc = KMLFILEDIR / "KML_Samples.kml"
        expected_xml = kml_samples_doc.open("rb").read()
        formatter = formatting.DiffFormatter(normalize=formatting.WS_BOTH)

        doc = fastkml.kml.KML.parse(kml_samples_doc)

        diff = main.diff_texts(
            doc.to_string(),
            expected_xml,
            formatter=formatter,
        )

        # assert diff is None
        assert fastkml.validator.validate(file_to_validate=kml_samples_doc)
        assert fastkml.validator.validate(element=doc.etree_element())

    def test_document_linearring_with_1d_tuple(self) -> None:
        linearring_1d_tuples = KMLFILEDIR / "LinearRingWith1DTuple.kml"
        expected_xml = linearring_1d_tuples.open("rb").read()
        formatter = formatting.DiffFormatter(normalize=formatting.WS_BOTH)

        doc = fastkml.kml.KML.parse(linearring_1d_tuples)

        diff = main.diff_texts(
            doc.to_string(precision=1),
            expected_xml,
            formatter=formatter,
        )

        # assert diff is None
        assert fastkml.validator.validate(file_to_validate=linearring_1d_tuples)
        # assert fastkml.validate.validate(element=doc.etree_element())

    def test_read_kml_samples(self) -> None:
        for p in KMLFILEDIR.glob("**/models/*.kml"):
            doc = fastkml.kml.KML.parse(p)
            diff = main.diff_texts(
                doc.to_string(),
                p.open("rb").read()
            )
            assert diff == []
            assert doc.validate()
            