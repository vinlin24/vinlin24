#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convenience script for renaming an image generated from copy-pasting
into my Markdown editor to some chosen name, moving it into the global
assets/ directory, and updating all references to the image in the
Markdown sources.
"""

import os
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

__author__ = "Vincent Lin"

parser = ArgumentParser(description=__doc__)
parser.add_argument("old_name", metavar="NAME.png", help="image to move")
parser.add_argument("new_name", metavar="NEW_NAME.png", help="new image name")
parser.add_argument("-f", "--force", action="store_true",
                    help="overwrite existing assets image if exists")

ASSETS_DIR = Path.cwd() / "assets"


def move_image(old_name: str, new_name: str) -> Path:
    """Rename and move an image to the assets/ directory."""
    # Fill whitespace in new_name (can't have spaces in Markdown).
    new_name = new_name.replace(" ", "-")
    # Enforce .png extension.
    new_path = Path(ASSETS_DIR / new_name).with_suffix(".png")
    # Disallow overwriting.
    if new_path.exists():
        sys.stderr.write(
            f"{new_path.name} already exists. Pick a different name.\n"
        )
        sys.exit(1)
    return Path(old_name).rename(new_path)


def get_new_relative_path(path: Path) -> str:
    """Get the path that should be used in the Markdown."""
    relative_path = path.relative_to(Path.cwd())
    # Markdown uses "/" for path separators.
    safe_path = str(relative_path).replace(os.path.sep, "/")
    return safe_path


def update_references(file: Path, old_name: str, new_path: str) -> None:
    """Update references of our old path in a Markdown file."""
    content = file.read_text(encoding="utf-8")
    pattern = f"!\\[(.*)\\]\\({old_name}\\)"
    replace = f"![\\g<1>]({new_path})"  # \g<num> to refer to groups.
    new_content = re.sub(pattern, replace, content)
    # newline="\n" to write LF, not CRLF.
    file.write_text(new_content, encoding="utf-8", newline="\n")


def main() -> None:
    """Main driver function."""
    args = parser.parse_args()
    old_name: str = args.old_name
    new_name: str = args.new_name

    ASSETS_DIR.mkdir(exist_ok=True)

    new_path = move_image(old_name, new_name)
    new_relative_path = get_new_relative_path(new_path)

    for file in Path.cwd().iterdir():
        if file.suffix != ".md" or file.name.startswith("README"):
            continue
        update_references(file, old_name, new_relative_path)


if __name__ == "__main__":
    main()
