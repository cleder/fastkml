import csv
import datetime
import pathlib
import random

import shapefile
from pygeoif.factories import force_3d
from pygeoif.factories import shape

import fastkml
import fastkml.containers
import fastkml.features
import fastkml.styles
import fastkml.times
from fastkml.enums import AltitudeMode
from fastkml.enums import DateTimeResolution
from fastkml.geometry import create_kml_geometry

shp = shapefile.Reader("ne_110m_admin_0_countries.shp")

co2_csv = pathlib.Path("owid-co2-data.csv")

co2_pa = {str(i): {} for i in range(1995, 2023)}

with co2_csv.open() as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["year"] >= "1995":
            co2_pa[row["year"]][row["iso_code"]] = (
                float(row["co2_per_capita"]) if row["co2_per_capita"] else 0
            )

styles = []
folders = []
for feature in shp.__geo_interface__["features"]:
    iso3_code = feature["properties"]["ADM0_A3"]
    geometry = shape(feature["geometry"])
    color = random.randint(0, 0xFFFFFF)
    styles.append(
        fastkml.styles.Style(
            id=iso3_code,
            styles=[
                fastkml.styles.LineStyle(color=f"33{color:06X}", width=2),
                fastkml.styles.PolyStyle(
                    color=f"88{color:06X}",
                    fill=True,
                    outline=True,
                ),
            ],
        ),
    )
    style_url = fastkml.styles.StyleUrl(url=f"#{iso3_code}")
    folder = fastkml.containers.Folder(name=feature["properties"]["NAME"])
    co2_growth = 0
    for year in range(1995, 2023):
        co2_year = co2_pa[str(year)].get(iso3_code, 0)
        co2_growth += co2_year

        kml_geometry = create_kml_geometry(
            force_3d(geometry, co2_growth * 5_000),
            extrude=True,
            altitude_mode=AltitudeMode.relative_to_ground,
        )
        timespan = fastkml.times.TimeSpan(
            begin=fastkml.times.KmlDateTime(
                datetime.date(year, 1, 1),
                resolution=DateTimeResolution.year_month,
            ),
            end=fastkml.times.KmlDateTime(
                datetime.date(year, 12, 31),
                resolution=DateTimeResolution.year_month,
            ),
        )
        placemark = fastkml.features.Placemark(
            name=f"{feature['properties']['NAME']} - {year}",
            description=feature["properties"]["FORMAL_EN"],
            kml_geometry=kml_geometry,
            style_url=style_url,
            times=timespan,
        )
        folder.features.append(placemark)
    folders.append(folder)

document = fastkml.containers.Document(features=folders, styles=styles)
kml = fastkml.KML(features=[document])

outfile = pathlib.Path("co2_growth_1995_2022.kml")
with outfile.open("w") as f:
    f.write(kml.to_string(prettyprint=True, precision=3))

csv_outfile = pathlib.Path("co2_per_capita_2020.csv")
with csv_outfile.open("w") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "iso_code", "co2_per_capita"])
    for year, co2_data in co2_pa.items():
        for iso_code, co2_per_capita in co2_data.items():
            writer.writerow([year, iso_code, co2_per_capita])
