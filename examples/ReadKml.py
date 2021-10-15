from fastkml import kml

# Setup the string which contains the KML file we want to read
doc = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Document.kml</name>
  <open>1</open>
  <Style id="exampleStyleDocument">
    <LabelStyle>
      <color>ff0000cc</color>
    </LabelStyle>
  </Style>
  <Placemark>
    <name>Document Feature 1</name>
    <styleUrl>#exampleStyleDocument</styleUrl>
    <Point>
      <coordinates>-122.371,37.816,0</coordinates>
    </Point>
  </Placemark>
  <Placemark>
    <name>Document Feature 2</name>
    <styleUrl>#exampleStyleDocument</styleUrl>
    <Point>
      <coordinates>-122.370,37.817,0</coordinates>
    </Point>
  </Placemark>
</Document>
</kml>"""

# Create the KML object to store the parsed result
k = kml.KML()

# Read in the KML string
k.from_string(doc)

# Next we perform some simple sanity checks

# Check that the number of features is correct
# This corresponds to the single ``Document``
features = list(k.features())
print(len(features))

# Check that we can access the features as a generator
# (The two Placemarks of the Document)
print(features[0].features())

f2 = list(features[0].features())
print(len(f2))


# Check specifics of the first Placemark in the Document
print(f2[0])
print(f2[0].description)
print(f2[0].name)

# Check specifics of the second Placemark in the Document
print(f2[1].name)
f2[1].name = "ANOTHER NAME"
print(f2[1].name)

# Verify that we can print back out the KML object as a string
print(k.to_string(prettyprint=True))

expected = """<kml:kml xmlns:ns0="http://www.opengis.net/kml/2.2">
  <kml:Document>
    <kml:name>Document.kml</kml:name>
    <kml:visibility>1</kml:visibility>
    <kml:open>1</kml:open>
    <kml:Style id="exampleStyleDocument">
      <kml:LabelStyle>
        <kml:color>ff0000cc</kml:color>
        <kml:scale>1.0</kml:scale>
      </kml:LabelStyle>
    </kml:Style>
    <kml:Placemark>
      <kml:name>Document Feature 1</kml:name>
      <kml:visibility>1</kml:visibility>
      <kml:open>0</kml:open>
      <kml:Point>
        <kml:coordinates>-122.371000,37.816000,0.000000</kml:coordinates>
      </kml:Point>
    </kml:Placemark>
    <kml:Placemark>
      <kml:name>ANOTHER NAME</kml:name>
      <kml:visibility>1</kml:visibility>
      <kml:open>0</kml:open>
      <kml:Point>
        <kml:coordinates>-122.370000,37.817000,0.000000</kml:coordinates>
      </kml:Point>
    </kml:Placemark>
  </kml:Document>
</kml:kml>"""
