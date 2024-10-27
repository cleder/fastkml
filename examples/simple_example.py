#!/usr/bin/env python
import pathlib

from fastkml import kml


def print_child_features(element, depth=0):
    """Prints the name of every child node of the given element, recursively."""
    if not getattr(element, "features", None):
        return
    for feature in element.features:
        print("  " * depth, feature.name)
        print_child_features(feature, depth + 1)


if __name__ == "__main__":
    fname = pathlib.Path("examples/KML_Samples.kml")

    with fname.open(encoding="utf-8") as kml_file:
        k = kml.KML.from_string(kml_file.read().encode("utf-8"))

    print_child_features(k)
