#!/usr/bin/env python
# coding: utf-8

from fastkml.kml import *

def printChildFeatures(element):
    level = 0
    for feature in element.features():
        try:
            print "    " * level, feature.name
            printChildFeatures(feature)
            level += 1
        except:
            pass

if __name__ == '__main__':
    
    fname = "KML_Samples.kml"

    k = KML()

    with open(fname) as kmlFile:
        k.from_string(kmlFile.read())    

    printChildFeatures(k)