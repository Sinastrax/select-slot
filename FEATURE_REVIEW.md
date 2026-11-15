# Feature review: extended Authentic GB display modes for Slot

This is a **code-review index** for a request to [pvaibhav/slot](https://github.com/pvaibhav/slot). The changes were developed against **v1.15.3-pvaibhav.1** for the original Anbernic RG SP.

> **Scope:** This is a proof of concept, **not a clean pull request or merge-ready diff**. The repository contains multiple sequential patches and experimental/retired audio and SameBoy changes. Review the feature patches below, not the entire branch as a proposed drop-in update. Some patches overlap and later patches refine or supersede earlier implementations.

## Features and source links

| Requested behavior | Relevant source patch | Notes |
| --- | --- | --- |
| GBC Authentic screen for GB cartridges | [`rgsp-authentic-gbc.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/rgsp-authentic-gbc.patch) | Offers the existing GBC Authentic display model while playing .gb titles, with GB palette selection instead of forcing grayscale. |
| Pocket Color hybrid | [`pocket-color.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/pocket-color.patch) | Adds the Pocket Color model (Pocket pixel geometry with color input). |
| Pocket Color response refinement | [`pocket-color-gbc-correction.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/pocket-color-gbc-correction.patch) | Adjusts Pocket Color color-response processing. |
| Pocket SGB + actual SGB palette-command mode | [`sgb-pocket-pixel-separation.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/sgb-pocket-pixel-separation.patch) | Adds Pocket SGB and configures mGBA's Super Game Boy hardware mode; this is different from a static Gambatte SGB palette. |
| Independent GB display profiles per core | [`core-specific-gb-screen-sgb-correction-performance.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/core-specific-gb-screen-sgb-correction-performance.patch) | Stores and restores separate GB shader and model settings for Gambatte and mGBA. |
| Color-correction controls (mixed historical patch) | [`sameboy-authentic-correction.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/sameboy-authentic-correction.patch) | Introduces Authentic correction switches and saved flags, but ALSO contains a retired SameBoy experiment: requires extraction before upstreaming. |
| Separate correction preferences | [`per-core-authentic-color-correction.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/per-core-authentic-color-correction.patch) | Makes GB color-correction choices independent between Gambatte and mGBA. |
| Consistent neutral values and stable LCD texture | [`color-transfer-only-gambatte-sgb-fix.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/color-transfer-only-gambatte-sgb-fix.patch) | Separates source RGB color transfer from underlying monochrome LCD geometry. |
| Neutral-white color response | [`authentic-color-response-only.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/authentic-color-response-only.patch) | Keeps neutral whites/grays and source luminance stable when correction is switched while preserving the display's pixel geometry. |

### Fast-forward blending

[`rgsp-authentic-gbc.patch`](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/patches/rgsp-authentic-gbc.patch) also makes Authentic frame blending/ghosting temporarily turn off during fast-forward, returning to the selected effect at normal speed.

### Reproducing the patch sequence

The [H700 build workflow](https://github.com/Sinastrax/slot-rgsp-mod/blob/main/.github/workflows/build-h700.yml) checks out the pinned upstream version and applies patches in order. This is the reproducibility reference; **it is not a recommendation to merge all the patches unchanged**.

### Important integration caveats

- The existing [pvaibhav/slot README](https://github.com/pvaibhav/slot) already provides the Authentic shader framework. These requests are extensions of that fork, not features built for the official `slot-cfw/slot` tree in isolation.
- The original `sameboy-authentic-correction.patch` includes useful color-correction wiring **and** a retired SameBoy emulator experiment; only the correction features are relevant here. The separate `restore-mgba-gb-and-disable-autoframeskip.patch` later removes SameBoy from the active emulator choices. Neither experimental change should be merged wholesale.
- Later shader patches refine the rendering and neutral/uncorrected appearance. Treat the aggregate behavior as a proposal, rather than reviewing an early patch as final.
- Audio queue drift, sample dropping/crossfade, buffer-recovery and frameskip experiments were **not** validated as fixes and are not requested for inclusion. An older mGBA libretro core has worked better in device testing; that is a **separate compatibility/performance topic**, not part of this feature proposal.
- The requested `Pocket Color` and `Pocket SGB` modes are intentional *hybrids*, not claims of historically accurate hardware colorimetry.
- A properly reviewable PR would rebase onto the current `pvaibhav-improvements` branch, separate these features into focused commits, and exclude obsolete patches.
