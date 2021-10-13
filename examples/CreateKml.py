# Import the library
from fastkml import kml
from shapely.geometry import Point, LineString, Polygon

# Create the root KML object
k = kml.KML()
ns = '{http://www.opengis.net/kml/2.2}'

# Create a KML Document and add it to the KML root object
d = kml.Document(ns, 'docid', 'doc name', 'doc description')
k.append(d)

# Create a KML Folder and add it to the Document
f = kml.Folder(ns, 'fid', 'f name', 'f description')
d.append(f)

# Create a KML Folder and nest it in the first Folder
nf = kml.Folder(ns, 'nested-fid', 'nested f name', 'nested f description')
f.append(nf)

# Create a second KML Folder within the Document
f2 = kml.Folder(ns, 'id2', 'name2', 'description2')
d.append(f2)

# Create a Placemark with a simple polygon geometry and add it to the
# second folder of the Document
p = kml.Placemark(ns, 'id', 'name', 'description')
p.geometry =  Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 1)])
f2.append(p)

# Print out the KML Object as a string
print(k.to_string(prettyprint=True))

expected = """<kml:kml xmlns:ns0="http://www.opengis.net/kml/2.2">
  <kml:Document id="docid">
    <kml:name>doc name</kml:name>
    <kml:description>doc description</kml:description>
    <kml:visibility>1</kml:visibility>
    <kml:open>0</kml:open>
    <kml:Folder id="fid">
      <kml:name>f name</kml:name>
      <kml:description>f description</kml:description>
      <kml:visibility>1</kml:visibility>
      <kml:open>0</kml:open>
      <kml:Folder id="nested-fid">
        <kml:name>nested f name</kml:name>
        <kml:description>nested f description</kml:description>
        <kml:visibility>1</kml:visibility>
        <kml:open>0</kml:open>
      </kml:Folder>
    </kml:Folder>
    <kml:Folder id="id2">
      <kml:name>name2</kml:name>
      <kml:description>description2</kml:description>
      <kml:visibility>1</kml:visibility>
      <kml:open>0</kml:open>
      <kml:Placemark id="id">
        <kml:name>name</kml:name>
        <kml:description>description</kml:description>
        <kml:visibility>1</kml:visibility>
        <kml:open>0</kml:open>
        <kml:Polygon>
          <kml:outerBoundaryIs>
            <kml:LinearRing>
              <kml:coordinates>
                0.000000,0.000000,0.000000
                1.000000,1.000000,0.000000
                1.000000,0.000000,1.000000
                0.000000,0.000000,0.000000
              </kml:coordinates>
            </kml:LinearRing>
         </kml:outerBoundaryIs>
        </kml:Polygon>
      </kml:Placemark>
    </kml:Folder>
  </kml:Document>
</kml:kml>"""