#!/usr/bin/env python
"""
Remove all unused type ignores from source files.

Usage:
    remove_unused_type_ignores.py [--error-file = FILE]
    or read errors from STDIN.

Example:
    mypy fastkml | python remove_unused_type_ignores.py

    or

    mypy fastkml > errors.txt
    python remove_unused_type_ignores.py --error-file errors.txt
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
def remove(error_file):
    """Remove unused ignores from the source files."""
    line_count = 0
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
            new_line = line[:column] + "\n"
            click.echo(f"Removed '# type ignore' from {filename}:{line_number}")
            click.echo(f"-{line.rstrip()}")
            click.echo(f"+{new_line.rstrip()}")
            line_count += 1
            source[int(line_number) - 1] = new_line
            with open(filename, "w") as dest_file:
                dest_file.writelines(source)
    click.echo(f"Removed {line_count} '# type ignore's.")


if __name__ == "__main__":
    remove()
