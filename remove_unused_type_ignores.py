#!/usr/bin/env python
"""
Remove all unused type ignores from source files.

Usage:
    remove_unused_type_ignores.py remove FILENAME
    or read errors from STDIN.

Example:
    mypy fastkml | python remove_unused_type_ignores.py remove

    or

    mypy fastkml > errors.txt
    python remove_unused_type_ignores.py --error-file errors.txt
"""
import re
import sys
from typing import IO, Tuple, List

import click

DRY_RUN = "Dry run, no changes were written to disk."
DRY_RUN_HELP = "Do not write changes to disk."

square_bracket_regex = re.compile(r'\[(.*?)\]')

@click.group()
def cli():
    pass

def split_error_line(line: str) -> Tuple[str, int, str]:
    parts = line.split(":", 3)
    if len(parts) != 4:
        return '', -1, ''
    filename = parts[0]
    line_number = int(parts[1]) -1
    error = parts[2]
    if error.strip() != "error":
        return filename, line_number, ''
    error_code = parts[3]
    return filename, line_number, error_code

def save_source_file(filename: str, source: List[str], dry_run: bool) -> None:
    if dry_run:
        return
    with open(filename, "w") as dest_file:
        dest_file.writelines(source)

def get_source(filename: str, line_number) -> Tuple[List[str], str]:
        with open(filename) as source_file:
            source = source_file.readlines()
        line = source[line_number]
        line = line.rstrip()
        return source, line

@click.command()
@click.option(
    "--dry-run", is_flag=True, default=False, help=DRY_RUN_HELP
)
@click.argument(
    "error_file",
    type=click.File("rt"),
    default=sys.stdin,
)
def add(dry_run: bool, error_file: IO[str]):
    """Add missing type ignores to the source files."""
    line_count = 0
    for errors in error_file.readlines():
        filename, line_number, error_code = split_error_line(errors)
        if not error_code:
            continue
        match = square_bracket_regex.search(error_code)
        if match is None:
            continue
        code = match.group(0)
        source, line = get_source(filename, line_number)
        new_line = f'{line}  # type: ignore{code}\n'
        click.echo(f"Added '# type ignore' to {filename}:{line_number}")
        click.echo(f"-{line.rstrip()}")
        click.echo(f"+{new_line.rstrip()}")
        line_count += 1
        source[line_number] = new_line
        save_source_file(filename, source, dry_run)

    click.echo(f"Added {line_count} '# type ignore's.")
    if dry_run:
        click.echo(DRY_RUN_HELP)


@click.command()
@click.option(
    "--dry-run", is_flag=True, default=False, help=DRY_RUN_HELP
)
@click.argument(
    "error_file",
    type=click.File("rt"),
    default=sys.stdin,
)
def remove(dry_run: bool, error_file: IO[str]) -> None:
    """Remove unused ignores from the source files."""
    line_count = 0
    for errors in error_file.readlines():
        filename, line_number, error_code = split_error_line(errors)
        if error_code.strip() != 'Unused "type: ignore" comment':
            continue
        source, line = get_source(filename, line_number)
        if "# type: ignore" not in line:
            continue
        column = line.find("# type: ignore")
        new_line = f'{line[:column]}\n'
        click.echo(f"Removed '# type ignore' from {filename}:{line_number}")
        click.echo(f"-{line.rstrip()}")
        click.echo(f"+{new_line.rstrip()}")
        line_count += 1
        source[line_number] = new_line
        save_source_file(filename, source, dry_run)
    click.echo(f"Removed {line_count} '# type ignore's.")
    if dry_run:
        click.echo(DRY_RUN)


if __name__ == "__main__":
    cli.add_command(add)
    cli.add_command(remove)
    cli()
