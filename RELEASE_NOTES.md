# select. slot. 1.16.0 Ver. 30

## Menu and storage quality-of-life
- **Restart:** direct main settings entry immediately below System, using the original restart code.
- **RetroAchievements in-game browser:** from the paused game's menu, browse cached achievements and badges, locked/unlocked status, total points and a detailed description. X toggles locked-first order. No shelf viewer.
- **Storage Cleanup under Tools:** scan only eligible 7+-day-old rotated log files and temporary cache files. Preview count/size, then confirm a separate deletion action. Unrecognized files are never selected.
- **Protected folders:** System and its update staging folder, Games, Saves, Config, BIOS and screenshots are excluded. Custom exclusions can be added to Config/cleanup-protected.txt. Symlinks are never followed.
- **Original System manifest behavior preserved:** full OTA updates still remove System files absent from the package manifest, as before.
- **Smaller firmware download:** publish the MPL-2.0 corresponding modified mGBA source as an independent release asset, alongside the full firmware ZIP; retain the compiled emulator and the required license/source notice in System.

**Unchanged:** Wi-Fi while gaming, existing mGBA performance governor for all supported systems, GBA/GB/GBC/SGB shaders, color correction, scaling, bezels, RetroAchievements account and cache handling, and Miyoo firmware.

### Compatibility
H700 devices (RG34XXSP, RG35XXSP, RG35XX H); firmware updater remains version compatible. No ROMs or BIOS files included.
