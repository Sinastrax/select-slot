# select. slot. 1.16.0 Ver. 20

## Changes since select. slot. 1.16.0 Ver. 19

- **Rename the GBA bezel choices to `GBA` and `GBA SP`.** The existing AGS-102 SP strip is called **GBA SP** specifically in the Game Boy Advance menu; GB and GBC keep their established labels. The new original-horizontal option is simply **GBA**, including in its saved selection. Existing `ags-102` and `agb-001` settings remain compatible.
- **Restrict the GBA-only alternative to physical 640×480 panels**, not just layouts that scale internally to 640×480. This includes RG35XX H and excludes RG SP/RG34XXSP 720×480 and larger 4:3 devices. A Rust regression test checks eligible and excluded panels.
- **Use existing, attributed GBA bezel artwork** rather than deriving a new logo from the SP image. The pinned *Perfect GBA (no grid)* design by mugwomp93 is the same existing option used in the Miyoo branch. At packaging, CI checks its SHA-256, converts it to the exact existing SP dimensions, and compares the entire transparency mask pixel-for-pixel with Slot's untouched AGS-102 image. License and author attribution are included.

**Preserved from Ver. 19:** the original SP default, image geometry and animation, persistent choice, arbitrary custom bezels, GB/GBC behavior and all Ver. 18 color/shader corrections. No emulator-core or Miyoo modifications. Hardware appearance still requires a 640×480 device test.
