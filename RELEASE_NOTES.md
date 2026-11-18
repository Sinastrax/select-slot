# select. slot. 1.16.0 Ver. 28

## Changes since Ver. 27

- **Original-style select. slot. boot logo.** The bundled logo now reads `select. slot.`, with the same minimal white-on-dark styling as the original Slot wordmark. It is built into the frontend and included in the full firmware update package.
- **Branded OTA installation screen.** During firmware installation, the progress screen now says `UPDATING SELECT. SLOT.` instead of `UPDATING SLOT`.
- **Persistent branding across updates.** Branding is applied to the upstream source before compiling and checked in the release archive, rather than patched only in the final package.

**Existing custom boot logos are preserved.** A user-provided `Config/bootlogo.bmp` continues to take priority. The boot-resource logo is installed by the firmware at startup, so the old startup logo may still appear during the first installation of this release; the new logo appears on a subsequent power-on.

H700 firmware only. No changes to emulators, RetroAchievements configuration, saves, scaling or shaders.
