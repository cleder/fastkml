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
    examples_dir = pathlib.Path(__file__).parent
    fname = pathlib.Path(examples_dir / "KML_Samples.kml")

    k = kml.KML.parse(fname)

    print_child_features(k)
