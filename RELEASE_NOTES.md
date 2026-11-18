# select. slot. 1.16.0 Ver. 25

## Changes since Ver. 24

- **RetroAchievements login from Tools.** Select **Tools → RetroAchievements**, enter the account username and password with Slot's existing on-screen keyboard, and save.
- **Masked password entry.** The keyboard renders stars in place of characters, retaining the actual secret only to submit the login. Existing login passwords are never prefilled into the on-screen keyboard.
- **Restart required, explicitly indicated.** A confirmation states: “RetroAchievements saved. Restart Slot for the login to take effect.” This intentionally avoids live account switching.
- **Safe staged configuration.** Login is written atomically to the SD card; the password is needed across the restart to perform the first login, after which the token is remembered and the UI-entered password is automatically cleared. A previously saved account can be selected without retyping its password.
- **Compatibility.** Manual TOML configurations continue working; a manually written password is not automatically erased. Existing offline achievement caches and unsynced unlocks are retained per account.
- **Regression tests.** Verify login staging, account isolation, password scrubbing, masked keyboard display and the existing RetroAchievements suite.

No changes to the single Wi-Fi On/Off control, Ver. 23 Wi-Fi/ejection fixes, Ver. 24 launch status, actual unlock popups, graphics, cores or bezels.

H700 firmware. Hardware login flow and live RetroAchievements acceptance require on-device verification.
