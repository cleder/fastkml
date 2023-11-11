#!/usr/bin/env python

from fastkml import kml


def print_child_features(element):
    """Prints the name of every child node of the given element, recursively"""
    if not getattr(element, "features", None):
        return
    for feature in element.features():
        print(feature.name)
        print_child_features(feature)


if __name__ == "__main__":
    fname = "KML_Samples.kml"

    k = kml.KML()

    with open(fname) as kml_file:
        k.from_string(kml_file.read().encode("utf-8"))

    print_child_features(k)
