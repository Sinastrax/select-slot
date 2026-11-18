# select. slot. 1.16.0 Ver. 23

## Changes since select. slot. 1.16.0 Ver. 22

- **Fix the underlying Wi-Fi shutdown on normal cartridge removal.** Plain game ejection calls `end_link()` as part of cleanup, even when no link-play session was started. Previously, that unconditional call queued `RadioJob::Down`, which runs `slotlink.sh link down`. The link script's cleanup calls `wifi_stop`, terminating the normal `wpa_supplicant` and `udhcpc` processes outside Slot's main Wi-Fi state machine. This bypassed the safeguards in Ver. 21/22. **Normal game ejection now never queues a link-radio Down job unless there is a real or in-flight link session.**
- **Retain enabled home Wi-Fi throughout ordinary games.** A network still obtaining DHCP or reconnecting is no longer deliberately stopped at game launch. RetroAchievements can maintain online HTTPS access and rich presence during gameplay. The existing Wi-Fi Off toggle, sleep/power shutdown and no-config behavior are preserved.
- **Keep direct-console link play working.** When link play actually takes the wireless radio for softAP/STA, normal internet Wi-Fi yields. The link-radio Down job still runs when that session ends. Saved home networks reconnect afterward; restoration is deferred sufficiently to avoid racing the link's asynchronous radio teardown.
- **Test real teardown commands, not just UI flags.** Wi-Fi regressions assert that an ordinary cartridge eject never emits `RadioJob::Down` and never stops the wireless worker, even without a DHCP lease; verify that real link play still emits Down and subsequently reconnects; and preserve Wi-Fi Off, the network menu, RetroAchievements connectivity and existing link-play tests.

**Unchanged:** Ver. 22 light-theme clock/battery improvements and GBA scale choices, all verified color/shader and core fixes, GBA/GBA SP bezel artwork, OTA version display and checksum validation, and Miyoo builds. Hardware behavior still requires on-device confirmation.
