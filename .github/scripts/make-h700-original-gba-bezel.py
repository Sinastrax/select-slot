#!/usr/bin/env python3
"""Create an Original GBA bezel from the *same* H700 SP bezel alpha mask.

The source is upstream Slot's CC BY-SA 4.0 640x480 SP strip.
Do NOT rescale or alter the gameplay opening, screen placement, alpha,
animation or geometry. Change only the text in the bottom black strip:
remove SP; center the existing GAME BOY ADVANCE wordmark.

Standard-library PNG handling keeps the firmware build dependency-free.
"""
from pathlib import Path
import argparse
import struct
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"
WIDTH, HEIGHT = 640, 480
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
                pred = left + up - upper_left
                da, db, dc = abs(pred-left), abs(pred-up), abs(pred-upper_left)
                predictor = left if da <= db and da <= dc else up if db <= dc else upper_left
            else:
                raise ValueError(f"Unsupported PNG filter {method}")
            row[i] = (value + predictor) & 255
        result[y*stride:(y+1)*stride] = row
        above = row
    return result


def save_png(path: Path, rgba: bytes) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
    head = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 6, 0, 0, 0)
    stride = WIDTH * 4
    scanlines = b"".join(b"\x00" + rgba[y*stride:(y+1)*stride]
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
    width = WORD_END - WORD_START
    new_left = (WIDTH - width)//2
    for y in range(TOP, BOTTOM):
        row = y * stride
        lettering = source[row + WORD_START*4:row + WORD_END*4]
        if source[row + 80*4:row + 81*4] != b"\x00\x00\x00\xff":
            raise ValueError("Unexpected SP strip background; refusing redraw")
        target[row + CLEAN_START*4:row + CLEAN_END*4] = (
            b"\x00\x00\x00\xff" * (CLEAN_END-CLEAN_START))
        target[row + new_left*4:row + (new_left+width)*4] = lettering
    assert target[:TOP*stride] == source[:TOP*stride]
    assert target[BOTTOM*stride:] == source[BOTTOM*stride:]
    assert target[3::4] == source[3::4], "Bezel alpha changed!"
    save_png(args.gba_png, target)
    assert decode_png(args.gba_png) == target
    print(f"PASS: generated {args.gba_png}; 640x480 alpha and gameplay unchanged")


if __name__ == "__main__":
    main()
