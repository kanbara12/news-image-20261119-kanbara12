#!/usr/bin/env python3
"""Entry point for news-image-20261119 (@kanbara12), rebuilt version.

The front page is rendered at build time by render.py into entry.png.
This program just copies that file into the output directory, so it
needs nothing but the standard library and writes identical bytes on
every run.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "entry.png", output / "entry.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
