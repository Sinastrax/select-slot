# select. slot. 1.16.0 Ver. 23

## Changes since Ver. 22

- **Wi-Fi stays active during normal gameplay.** Previously Slot required an already-established IP address to retain Wi-Fi after a game launched. If Wi-Fi was still joining, or the IP lease was lost, it executed `Cmd::Release`, whose backend runs `slotlink wifi stop`. This could leave Wi-Fi disabled on return to the shelf. The game policy now retains a held service **or** starts a saved connection, independent of current DHCP status. This supports online features such as RetroAchievements when the selected emulator/core supports them.
- **Automatic reconnection after gameplay.** Saved Wi-Fi may reconnect during gameplay or after ejection; no manual toggle is needed. Existing Ver. 22 ejection handling is retained.
- **Local link play remains a special case.** Link play uses a dedicated radio handoff; it is not ordinary internet Wi-Fi and may require infrastructure Wi-Fi to stop temporarily. Normal Wi-Fi policy resumes when link play releases the radio.
- **Explicit Wi-Fi Off, sleep and shutdown still release Wi-Fi.** No changes to verified shaders, color correction, scaling, bezels, emulator cores or OTA file safety.
- **Regression tests:** Wi-Fi starts for a saved network even when a game begins before connection, remains held through gameplay and loss of DHCP, and survives cartridge ejection with subsequent reconnection.

H700 firmware. Physical hardware validation remains necessary.
