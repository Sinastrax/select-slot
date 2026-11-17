#!/usr/bin/env python3
"""Compile/link the actual merged Slot game shaders as OpenGL ES 2.0.

The firmware previously passed Rust compilation but repeatedly exited before
its UI became visible on an RG35XX H after the first Ver. 5 shader edit.
This checks GLSL compilation and linking, not just string presence. It is
not a replacement for a real Mali GPU hardware boot test.
"""
from pathlib import Path
import subprocess
import tempfile

source = Path("crates/slot-gfx/src/shaders.rs").read_text()

def rust_string(symbol: str) -> str:
    marker = f'pub const {symbol}: &str = r#"'
    assert source.count(marker) == 1, f"Expected exactly one {symbol}"
    return source.split(marker, 1)[1].split('"#;', 1)[0]

with tempfile.TemporaryDirectory(prefix="slot-gles2-") as tmp:
    folder = Path(tmp)
    vert = folder / "game.vert"
    frag = folder / "game.frag"
    vert.write_text("#version 100\n" + rust_string("RECT_VERT"))
    frag.write_text(
        "#version 100\n#define FRAG_COLOR gl_FragColor\n"
        + rust_string("GAME_FRAG")
    )
    commands = [
        ["glslangValidator", "-S", "vert", str(vert)],
        ["glslangValidator", "-S", "frag", str(frag)],
        ["glslangValidator", "-l", str(vert), str(frag)],
    ]
    for cmd in commands:
        result = subprocess.run(cmd, text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(
                "OpenGL ES 2.0 shader failed validation:\n"
                + " ".join(cmd) + "\n" + result.stdout + result.stderr
            )
    print("PASS: actual merged Slot GAME_FRAG compiles and links as OpenGL ES 2.0")
