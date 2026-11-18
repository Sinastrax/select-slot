#!/usr/bin/env python3
"""Build the original-GBA wordmark on the exact existing SP bottom bezel.

Only the lettering changes. The 640x480 alpha mask, screen opening and
bottom-bar geometry stay pixel-identical outside the old lettering.
Uses the Python standard library (no extra build dependency).

Derivative of Slot's original bezel, CC BY-SA 4.0:
System/licenses/bezel-CC-BY-SA-4.0.txt
"""
from pathlib import Path
import argparse
import struct
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"
WIDTH, HEIGHT = 640, 480
# The old logo uses x=154..442 for GAME BOY ADVANCE, x=449..492 for SP.
WORD_START, WORD_END = 150, 444
CLEAN_START, CLEAN_END = 145, 505
TOP, BOTTOM = 442, 474


def decode_png(path: Path) -> bytearray:
    blob = path.read_bytes()
    if not blob.startswith(SIGNATURE):
        raise ValueError("expected PNG")
    offset, compressed, header = len(SIGNATURE), bytearray(), None
    while offset < len(blob):
        size = struct.unpack_from(">I", blob, offset)[0]
        tag = blob[offset + 4:offset + 8]
        payload = blob[offset + 8:offset + 8 + size]
        offset += size + 12
        if tag == b"IHDR":
            header = struct.unpack(">IIBBBBB", payload)
        elif tag == b"IDAT":
            compressed.extend(payload)
        elif tag == b"IEND":
            break
    if header != (WIDTH, HEIGHT, 8, 6, 0, 0, 0):
        raise ValueError(f"Unexpected bezel format: {header}")
    scanlines = zlib.decompress(compressed)
    stride = WIDTH * 4
    if len(scanlines) != (stride + 1) * HEIGHT:
        raise ValueError("PNG size mismatch")
    result, above, cursor = bytearray(stride * HEIGHT), bytearray(stride), 0
    for y in range(HEIGHT):
        method = scanlines[cursor]
        source = scanlines[cursor + 1:cursor + 1 + stride]
        cursor += stride + 1
        row = bytearray(stride)
        for i, value in enumerate(source):
            left = row[i - 4] if i >= 4 else 0
            up = above[i]
            upper_left = above[i - 4] if i >= 4 else 0
            if method == 0:
                predictor = 0
            elif method == 1:
                predictor = left
            elif method == 2:
                predictor = up
            elif method == 3:
                predictor = (left + up) // 2
            elif method == 4:
                p = left + up - upper_left
                a, b, c = abs(p - left), abs(p - up), abs(p - upper_left)
                predictor = left if a <= b and a <= c else up if b <= c else upper_left
            else:
                raise ValueError(f"Unsupported PNG row filter: {method}")
            row[i] = (value + predictor) & 255
        result[y * stride:(y + 1) * stride] = row
        above = row
    return result


def save_png(path: Path, rgba: bytes) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
    head = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 6, 0, 0, 0)
    stride = WIDTH * 4
    scanlines = b"".join(b"\0" + rgba[y * stride:(y + 1) * stride]
                         for y in range(HEIGHT))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(SIGNATURE + chunk(b"IHDR", head)
                     + chunk(b"IDAT", zlib.compress(scanlines, 9))
                     + chunk(b"IEND", b""))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sp_png", type=Path)
    parser.add_argument("gba_png", type=Path)
    args = parser.parse_args()

    source = decode_png(args.sp_png)
    target = bytearray(source)
    stride = WIDTH * 4
    word_width = WORD_END - WORD_START
    new_left = (WIDTH - word_width) // 2
    for y in range(TOP, BOTTOM):
        row = y * stride
        lettering = source[row + WORD_START * 4:row + WORD_END * 4]
        # The black bottom bar is identical in every row; never touch the
        # transparent gameplay area above TOP.
        if source[row + 80 * 4:row + 80 * 4 + 4] != b"\0\0\0\xff":
            raise ValueError("Unexpected SP strip background; refusing redraw")
        target[row + CLEAN_START * 4:row + CLEAN_END * 4] = (
            b"\0\0\0\xff" * (CLEAN_END - CLEAN_START)
        )
        target[row + new_left * 4:row + (new_left + word_width) * 4] = lettering
    assert target[:TOP * stride] == source[:TOP * stride]
    assert target[BOTTOM * stride:] == source[BOTTOM * stride:]
    save_png(args.gba_png, target)
    assert decode_png(args.gba_png) == target
    print(f"Created {args.gba_png} (640x480; SP shape and screen unchanged)")


if __name__ == "__main__":
    main()
