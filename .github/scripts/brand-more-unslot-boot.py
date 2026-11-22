#!/usr/bin/env python3
"""Apply more.slot's boot wordmark to UnsloT's H700 System tree."""
import base64
from pathlib import Path
import sys
import zlib

from PIL import Image

SIZE = (514, 75)
BACKGROUND = (11, 14, 17)
FOREGROUND = (244, 245, 249)


def apply(system: Path) -> None:
    if not system.is_dir():
        raise SystemExit(f"Missing firmware System directory: {system}")
    source = Path(__file__).resolve().parents[2] / "branding" / "more-slot-wordmark.b85"
    pixels = zlib.decompress(base64.b85decode("".join(source.read_text().splitlines())))
    if len(pixels) != SIZE[0] * SIZE[1]:
        raise SystemExit("Corrupt more.slot wordmark")
    mask = Image.frombytes("L", SIZE, pixels)
    logo = system / "bootlogo.bmp"
    Image.composite(Image.new("RGB", SIZE, FOREGROUND), Image.new("RGB", SIZE, BACKGROUND), mask).save(logo, format="BMP")
    with Image.open(logo) as check:
        if check.format != "BMP" or check.mode != "RGB" or check.size != SIZE:
            raise SystemExit("Incorrect H700 boot wordmark format")
    print("Branded more.slot boot wordmark")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: brand-more-unslot-boot.py <unslot/card/System>")
    apply(Path(sys.argv[1]))
