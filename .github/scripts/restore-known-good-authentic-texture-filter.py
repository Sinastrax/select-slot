#!/usr/bin/env python3
"""Restore the Ver. 29 Authentic texture-filter path after the 1.16 merge."""
from pathlib import Path

path = Path("crates/slot-gfx/src/pipeline.rs")
source = path.read_text()
old = """        if effect != self.effect {
            self.effect = effect;
            let filter = match effect {
                ScreenEffect::Authentic => gl::LINEAR,
                _ => gl::NEAREST,
            };
            unsafe {
                for game in self.game {
                    gl::BindTexture(gl::TEXTURE_2D, game);
                    gl::TexParameteri(gl::TEXTURE_2D, gl::TEXTURE_MIN_FILTER, filter as i32);
                    gl::TexParameteri(gl::TEXTURE_2D, gl::TEXTURE_MAG_FILTER, filter as i32);
                }
            }
            self.ghost.set_filter(filter);
            self.reblend(quad);
        }
"""
new = """        if effect != self.effect {
            self.effect = effect;
            self.ghost.set_filter(match effect {
                ScreenEffect::Authentic => gl::LINEAR,
                _ => gl::NEAREST,
            });
            self.reblend(quad);
        }
"""
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    assert source.count(new) == 1, "Expected the upstream 1.16 Authentic texture-filter change"

# Keep the newer user-requested per-system blend setting and fast-forward
# override. Only restore the texture-sampling behavior from the Ver. 29 base.
assert "effective_blend(self.effect, self.authentic_fast_forward, self.blend)" in source
path.write_text(source)
