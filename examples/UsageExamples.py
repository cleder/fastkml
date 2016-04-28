#!/usr/bin/env python
# coding: utf-8

from fastkml import kml

def print_child_features(element):    
    if not getattr(element, 'features', None):
        return
    for feature in element.features():
        print feature.name
        print_child_features(feature)

if __name__ == '__main__':
    
    fname = "KML_Samples.kml"

    k = kml.KML()

    with open(fname) as kmlFile:
        k.from_string(kmlFile.read())    

    print_child_features(k)