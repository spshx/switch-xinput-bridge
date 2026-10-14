# Changelog

## 0.1.0 - 2026-10-14

First release.

- Bridges Switch-style Bluetooth controllers that send simple HID (0x3F) reports to a virtual Xbox 360 controller through ViGEmBus.
- Lic Pro Controller (`0E6F:018C`) verified. Nintendo Switch Pro Controller (`057E:2009`) included as expected to work.
- Supports several controllers at once (one virtual pad each) and reconnects automatically.
- Calibrates the stick centres at connect and recalibrates after input drops out. Deadzone is configurable.
- `position` (default) and `label` button layouts.
- Detects when a controller goes silent after sleep, and when another program has switched it to full (0x30) mode.
- Diagnostics: `--list` probes connected gamepads, `--test` and `--raw` show live input.
- Standalone `.exe` built by GitHub Actions for each release.
