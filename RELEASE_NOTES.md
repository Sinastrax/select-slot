# select. slot. 1.16.0 Ver. 19

## Changes since select. slot. 1.16.0 Ver. 18

- **GBA / GBA SP bottom-bezel choice** under **Screen → Game Boy Advance → Bezel** on Anbernic **640×480 (3.5-inch-class)** screens, including RG35XX H. The existing AGS-102 bezel is now labeled **GBA SP** on GBA only; **GBA** selects the original horizontal Game Boy Advance surround. **None** and existing custom choices remain.
- **Same screen size and opening.** Both versions use the original SP bottom-strip rendering position, animation and gameplay cutout. Scaling, pixel sampling, shader, color correction and game placement do not change.
- **Strict panel restriction:** the new GBA choice appears only at exactly **640×480** for GBA games, not on RG SP/RG34XXSP's **720×480** screens, larger panels or GB/GBC pages. The existing SP option and all previous device layouts are retained.
- **Saved selection:** the new GBA option persists as `bezel_gba=agb-001`. The pre-existing AGS-102/GBA SP choice remains the default.
- **Pre-existing artwork, not a redraw:** mugwomp93's *Perfect GBA (no grid)* image, already used by the select. slot. Miyoo build, is sourced from the pinned [KNULLI bezels](https://github.com/chrizzo-hb/knulli-bezels) revision, resized for 640×480 and verified pixel-by-pixel to have exactly the same alpha mask as Slot's original SP bezel. Full CC BY-SA 4.0 attribution is included in the package.

**Verification:** CI checks 640×480-only eligibility and persistence, validates the original GBA image against the existing SP alpha mask, and locks the Ver. 18 shader/Authentic source hashes. Hardware appearance on the 3.5-inch Anbernic panel remains to be confirmed. No Miyoo changes are part of this H700 revision.
