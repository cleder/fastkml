#!/usr/bin/env python
"""
Remove all unused type ignores from source files.

Usage:
    remove_unused_type_ignores.py [--error-file = FILE]
    or read errors from STDIN.
"""
import sys

import click


@click.command()
@click.option(
    "--error-file",
    help="Filename of the mypy error messages, omit to read from STDIN.",
    type=click.File("rt"),
    default=sys.stdin,
)
def generate(error_file):
    """Read the file, and remove unused ignores from the source."""
    for errors in error_file.readlines():
        parts = errors.split(":", 3)
        if len(parts) != 4:
            continue
        filename = parts[0]
        line_number = parts[1]
        error = parts[2]
        error_code = parts[3]
        if error.strip() != "error":
            continue
        if error_code.strip() != 'Unused "type: ignore" comment':
            continue
        with open(filename) as source_file:
            source = source_file.readlines()
        line = source[int(line_number) - 1]
        if "# type: ignore" in line:
            column = line.find("# type: ignore")
            line = line[:column]
            click.echo(f"Removed type ignore from {filename}:{line_number}")
            click.echo(line)
            source[int(line_number) - 1] = line
            # with open(filename, "wt") as source_file:
            #     source_file.writelines(source)
    click.echo("#Write something")
    ...


if __name__ == "__main__":
    generate()
