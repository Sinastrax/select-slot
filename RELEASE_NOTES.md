# select. slot. 1.16.0 Ver. 21

## Changes since select. slot. 1.16.0 Ver. 20

- **Correct the OTA version labels.** Update chips and the up-to-date message now display the public firmware format **1.16.0 Ver. 21** instead of the internal `v1.16.0-rgsp.21`. The up-to-date headline identifies **select. slot.** rather than generic Slot. BaseOS retains its original version labels.
- **Preserve Wi-Fi when a cartridge is ejected.** An already-running Wi-Fi connection is retained during the return to the shelf; pulling a cartridge no longer intentionally calls `slotlink wifi stop` to kill `wpa_supplicant` and DHCP. A temporary association or DHCP interruption during a game also no longer causes Slot to shut down an otherwise held Wi-Fi service.
- **Keep intentional radio behavior intact.** Wi-Fi Off, lid sleep, power off, link-play constraints, and starting a game while offline continue to use their existing paths. A game does not initiate an unsolicited Wi-Fi connection.
- **Regression checks.** The H700 build now runs the OTA UI tests and Wi-Fi UI tests, including a newly added connected-cartridge-eject test.

**Compatibility:** Only user-facing OTA labels and Wi-Fi connection lifetime are changed. The technical release filename `slot-v1.16.0-rgsp.21-h700.zip`, release manifest, download URLs, size and SHA-256 verification are preserved for OTA upgrades from earlier versions. All Ver. 20 GBA/GBA SP bezel choices and Ver. 18/17 shaders remain unchanged. This release does not change the light-theme clock, which requires separate verification.
