# select. slot. 1.16.0 Ver. 24

## Changes since Ver. 23

- **RetroAchievements connection status at game launch.** A silent, brief achievement-themed banner reports the actual state of the selected game's RetroAchievements session. "Connected" requires a successful RetroAchievements session and is not inferred from Wi-Fi being on. With a prepared game cache, "Offline ready" means achievements can still be earned without internet; the banner also distinguishes connecting, missing offline data, no supported achievements, and disabled RetroAchievements.
- **Status updates during launch.** The banner changes from cached or connecting to connected if the achievement service completes a session while it is visible. Status rendering happens away from the UI thread and uses a separate texture, so it does not overwrite an actual achievement award.
- **Achievement unlock popups remain unchanged.** Earned badges, achievement titles, points and the existing brief chime continue to work online or from a previously prepared offline cache. Earned notifications take priority if both banners occur together.
- **No new Wi-Fi modes.** The existing single Wi-Fi On/Off control and Ver. 23 gameplay connection, ejection and wireless link-play handling are unchanged.
- **New automated checks.** The complete slot-achievements test suite is included in H700 CI, with additional launch-status and per-game session-generation checks. No changes to emulation cores, shaders, bezels, scaling, audio or firmware update behavior.

H700 firmware. Final pop-up timing and live RetroAchievements server verification still require testing on a physical device.
