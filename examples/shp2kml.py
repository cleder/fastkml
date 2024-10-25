import csv
import pathlib
import random

import shapefile
from pygeoif.factories import force_3d
from pygeoif.factories import shape

import fastkml
import fastkml.containers
import fastkml.features
import fastkml.styles
from fastkml.enums import AltitudeMode
from fastkml.enums import ColorMode
from fastkml.geometry import create_kml_geometry

shp = shapefile.Reader("world-administrative-boundaries.shp")

co2_csv = pathlib.Path("owid-co2-data.csv")

co2_data = {}

with co2_csv.open() as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["year"] == "2020":
            co2_data[row["iso_code"]] = (
                float(row["co2_per_capita"]) if row["co2_per_capita"] else 0
            )

continents = {
    "Antarctica": fastkml.containers.Folder(name="Antarctica"),
    "Europe": fastkml.containers.Folder(name="Europe"),
    "Oceania": fastkml.containers.Folder(name="Oceania"),
    "Africa": fastkml.containers.Folder(name="Africa"),
    "Americas": fastkml.containers.Folder(name="Americas"),
    "Asia": fastkml.containers.Folder(name="Asia"),
}

for feature in shp.__geo_interface__["features"]:
    geometry = shape(feature["geometry"])
    co2_emission = co2_data.get(feature["properties"]["iso3"], 0)
    geometry = force_3d(geometry, co2_emission * 100_000)
    kml_geometry = create_kml_geometry(
        geometry,
        extrude=True,
        altitude_mode=AltitudeMode.relative_to_ground,
    )
    color = random.randint(0, 0xFFFFFF)
    style = fastkml.styles.Style(
        id=feature["properties"]["iso3"],
        styles=[
            fastkml.styles.LineStyle(color=f"55{color:06X}", width=2),
            fastkml.styles.PolyStyle(
                color_mode=ColorMode.random,
                color=f"88{color:06X}",
                fill=True,
                outline=True,
            ),
        ],
    )

    style_url = fastkml.styles.StyleUrl(url=f"#{feature['properties']['iso3']}")
    placemark = fastkml.features.Placemark(
        name=feature["properties"]["name"],
        description=feature["properties"]["status"],
        kml_geometry=kml_geometry,
        styles=[style],
    )
    continents[feature["properties"]["continent"]].features.append(placemark)

document = fastkml.containers.Document(features=continents.values())
kml = fastkml.KML(features=[document])

outfile = pathlib.Path("co2_per_capita_2020.kml")
with outfile.open("w") as f:
    f.write(kml.to_string(prettyprint=True, precision=3))
