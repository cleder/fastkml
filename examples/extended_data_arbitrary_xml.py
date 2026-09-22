from fastkml import KML
from fastkml import ExtendedData
from fastkml import Placemark
from fastkml import XMLData
from fastkml import config

if __name__ == "__main__":
    campsite_number = config.etree.fromstring(
        b'<camp:number xmlns:camp="http://campsites.com">14</camp:number>',
    )
    parking_spaces = config.etree.fromstring(
        b'<camp:parkingSpaces xmlns:camp="http://campsites.com">2</camp:parkingSpaces>',
    )

    placemark = Placemark(
        name="CampsiteData",
        extended_data=ExtendedData(
            elements=[campsite_number, parking_spaces],
        ),
    )
    kml = KML(features=[placemark])

    reparsed = KML.from_string(kml.to_string())
    custom_value = reparsed.features[0].extended_data.elements[0]

    assert isinstance(custom_value, XMLData)  # noqa: S101
    assert custom_value.element.tag == "{http://campsites.com}number"  # noqa: S101
    print(kml.to_string(prettyprint=True))
