# switch-xinput-bridge

**Use a Lic Pro Controller (or a similar Switch / Switch 2 style Bluetooth controller) on Windows in games that only support Xbox controllers.** Examples include *It Takes Two* and most other Unreal and EA games.

The controller pairs over Bluetooth and Windows shows it as connected, but the game does nothing when you press buttons. This tool fixes that. It reads the controller and mirrors every input onto a **virtual Xbox 360 controller**, which every PC game understands.

```
Lic Pro Controller ──Bluetooth HID──▶ switch-xinput-bridge ──ViGEmBus──▶ virtual Xbox 360 pad ──XInput──▶ game
```

- Works with several controllers at once (one virtual Xbox pad each), so local co-op works. It also works alongside a real Xbox controller.
- Picks the controller up again by itself when it reconnects.
- Detects when the controller has gone silent after sleep, and tells you how to fix it.
- Recalibrates the sticks so idle drift doesn't move your character.
- Comes as a standalone `.exe`, so you don't need to install Python.

---

## Supported controllers

| Controller | VID:PID | Status |
|---|---|---|
| Lic Pro Controller (Switch / Switch 2 style) | `0E6F:018C` | ✅ Verified |
| Nintendo Switch Pro Controller (Bluetooth) | `057E:2009` | 🟡 Expected to work (same protocol, untested) |
| Other Switch-style controllers | any | Run the check described in [Is my controller compatible?](#is-my-controller-compatible) |

The tool works with any controller that sends Nintendo's **"simple HID" (0x3F) input reports** over Bluetooth. Most third-party "Switch Pro" controllers do this when paired with a PC. Got another model working? [Report it](https://github.com/spshx/switch-xinput-bridge/issues/new?template=controller-report.yml) so it can be added to the table.

> **Not supported:** Joy-Cons (they use a different report layout), and the official Nintendo **Switch 2** Pro Controller, which uses a different Bluetooth LE protocol. Controllers that already show up as Xbox controllers don't need this tool.

---

## Quick start

### 1. Install the ViGEmBus driver (one time)

Download and install **`ViGEmBus_1.22.0_x64_x86_arm64.exe`** from <https://github.com/nefarius/ViGEmBus/releases>. This driver is what creates the virtual Xbox controller. You might already have it if you've used DS4Windows or similar tools.

### 2. Pair your controller

1. Go to **Settings → Bluetooth & devices → Add device → Bluetooth**.
2. Hold the controller's **sync/pairing button** until its lights flash quickly.
3. Select the controller (for example "Lic Pro Controller") in the list.

### 3. Run the bridge

**Option A: download the `.exe` (easiest)**
1. Download `switch-xinput-bridge.exe` from the [Releases page](https://github.com/spshx/switch-xinput-bridge/releases/latest).
2. Double-click it and keep the window open while you play.

Windows SmartScreen may warn about an unknown publisher because the `.exe` isn't code-signed. Click **More info → Run anyway**, or use option B, which runs the source directly.

**Option B: run from source (needs [Python 3.9+](https://www.python.org/downloads/))**
1. Download this repo (**Code → Download ZIP**) and extract it.
2. Double-click **`install.bat`** (only needed once).
3. Double-click **`start.bat`** and keep the window open while you play.

### 4. Play

Start the bridge **before** you launch the game. When the window shows `ready -> virtual Xbox 360 controller`, start the game. It will see the controller as an Xbox controller.

For *It Takes Two*: one player can use a real Xbox controller (or keyboard) and the other the Lic controller. Both work at the same time.

---

## Checking your buttons

Run **`test-controller.bat`** (or `switch-xinput-bridge --test`). It prints every button you press and the stick positions, without creating a virtual pad:

```
Lic Pro Controller (Switch / Switch 2 style) [0E6F:018C]: buttons: A ZR DPAD_RIGHT    L(+0.00,+0.00) R(+0.00,+0.00)
```

## Button mapping

Buttons are mapped **by position** by default: the face button at the bottom acts as Xbox **A**, so you press where the game's on-screen Xbox prompts point.

| Switch controller | Xbox (default `position` layout) | Xbox (`--layout label`) |
|---|---|---|
| B (bottom) | A | B |
| A (right) | B | A |
| Y (left) | X | Y |
| X (top) | Y | X |
| L / R | LB / RB | LB / RB |
| ZL / ZR | LT / RT (fully on or off) | LT / RT |
| − / + | Back / Start | Back / Start |
| Home | Guide | Guide |
| Capture | Back | Back |
| Left / right stick click | LS / RS | LS / RS |
| D-pad, sticks | D-pad, sticks | D-pad, sticks |

If you'd rather go by the printed letter (Switch "A" = Xbox "A"), use `start.bat --layout label`.

## Options

```
switch-xinput-bridge [--test | --raw | --list] [--layout {position,label}] [--deadzone 0.10]
                     [--device VID:PID] [--verbose]
```

| Option | What it does |
|---|---|
| `--test` | Shows what the controller sends instead of creating a virtual pad. |
| `--list` | Lists connected gamepads, checks each one for compatibility, then exits. |
| `--raw` | Like `--test`, but also prints the raw report bytes (useful for bug reports). |
| `--layout label` | Maps buttons by printed letter instead of by position. |
| `--deadzone 0.15` | Sets a larger stick deadzone (fraction of full tilt, default `0.10`), if you still see drift. |
| `--device VID:PID` | Also bridges a controller that isn't in the built-in list. Can be given more than once. |
| `--verbose` | Prints debug logging. |

You can pass these options to the batch files too, for example `start.bat --layout label`. To change the default for double-clicking, edit the last line of `start.bat`.

---

## Is my controller compatible?

1. Pair the controller and turn it on.
2. Run **`check-controllers.bat`** (or `switch-xinput-bridge --list`) and press a button while it's checking:

```
Gamepads connected now (probing each for ~1.5 s, press a button if it shows 'no data'):
  0E6F:018C  Lic Pro Controller (Switch / Switch 2 style): compatible (Switch simple HID 0x3F reports)
  1234:ABCD  Wireless Gamepad: compatible (Switch simple HID 0x3F reports)
```

3. If a controller shows **compatible** but isn't in the supported list, run it with its ID:
   `start.bat --device 1234:ABCD`
4. If it works, please [open a controller report](https://github.com/spshx/switch-xinput-bridge/issues/new?template=controller-report.yml) so it can be added.

More detail is in [docs/ADDING_A_CONTROLLER.md](docs/ADDING_A_CONTROLLER.md).

---

## Troubleshooting

The full guide is in [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md). The most common problems:

**The controller shows "Connected" but there's no input (often after it went to sleep).**
Many Switch-style controllers don't reconnect properly to a PC after sleeping. Windows keeps them listed as connected, but no data arrives, and the bridge will say `input stopped`. **Fix:** remove the controller in Bluetooth settings and pair it again. To avoid this, turn the controller off yourself when you stop playing.

**"Could not connect to the ViGEmBus driver"**
Install ViGEmBus (step 1 above), then reboot.

**The game reacts twice to each press, or sees an extra controller.**
Some games read both the real controller and the virtual one. Hide the real one with [HidHide](https://github.com/nefarius/HidHide).

**The bridge says the controller is in "full mode (0x30)".**
Another program, usually **Steam** with "Switch controller support" turned on, has taken over the controller. Close Steam (or turn that setting off), then turn the controller off and on.

---

## How it works

When a Switch-style controller connects over Bluetooth, it starts out in a basic HID mode and sends 64-byte **0x3F reports**: two bytes of button bits, one D-pad (hat) byte, and four 16-bit stick axes. Windows exposes this as a generic DirectInput gamepad. Games built on **XInput** (the Xbox controller API) ignore that kind of device completely.

The bridge reads those reports through [hidapi](https://github.com/trezor/cython-hidapi). It calibrates the stick centres, applies a deadzone, and translates the buttons. Then it drives a virtual Xbox 360 controller created by the [ViGEmBus](https://github.com/nefarius/ViGEmBus) driver (via [vgamepad](https://github.com/yannbouteiller/vgamepad)). Games just see an Xbox controller.

[docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) has the full report layout and a few driver quirks this tool works around.

## Limitations

- **No rumble.** Vibration from the game isn't sent to the controller.
- **No gyro or motion controls.** The simple report mode doesn't include motion data.
- **ZL / ZR are digital.** These controllers don't have analog triggers.
- **Windows only.** Linux already supports these controllers through the `hid-nintendo` driver.

## Development

```bat
python -m venv .venv
.venv\Scripts\pip install -e .[dev]
.venv\Scripts\pytest
```

The protocol, calibration and mapping code (`report.py`, `sticks.py`, `mapping.py`) doesn't depend on hardware and is unit-tested using report bytes captured from a real controller. `bridge.py` handles the HID devices and virtual pads, and `devices.py` contains the list of supported controllers.

To build the standalone `.exe` (it ends up in `dist\`):

```bat
.venv\Scripts\pip install pyinstaller
.venv\Scripts\python scripts\build_exe.py
```

Pushing a `v*` tag runs the release workflow, which builds the `.exe` and attaches it to a GitHub release.

Contributions are welcome, especially reports of new compatible controllers.

## Credits

- [ViGEmBus](https://github.com/nefarius/ViGEmBus) by Nefarius Software Solutions, for virtual gamepad emulation
- [vgamepad](https://github.com/yannbouteiller/vgamepad), Python bindings for ViGEm
- [cython-hidapi](https://github.com/trezor/cython-hidapi), for HID access
- The Switch controller report format is documented by the community in [dekuNukem/Nintendo_Switch_Reverse_Engineering](https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering), and implemented in SDL and Linux `hid-nintendo`

## License

[MIT](LICENSE). This project isn't affiliated with Nintendo, Microsoft, Lic, PDP, or EA. All trademarks belong to their owners.
