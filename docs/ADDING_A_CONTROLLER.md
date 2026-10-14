# Adding a controller

The bridge works with any controller that sends Nintendo **simple HID (0x3F)** reports. Adding one usually means adding a single line to the supported list.

## 1. Check compatibility

Pair the controller, turn it on, then run:

```bat
switch-xinput-bridge --list
```

Press a button while it probes. The result next to each gamepad means:

| Result | Meaning |
|---|---|
| `compatible (Switch simple HID 0x3F reports)` | It will work. Continue to step 2. |
| `Switch full-mode 0x30 reports` | Another app (usually Steam) changed its mode. Close that app, reconnect, and try again. |
| `not compatible (report ID 0x..)` | It uses a different protocol. If it has an X-input mode, use that instead. |
| `no data` | It's paired but silent. See the troubleshooting guide. |

## 2. Try it

```bat
switch-xinput-bridge --device VID:PID --test
```

Press every button and move both sticks. Check that the names printed match what you pressed. Then run the bridge without `--test` and try a game.

## 3. Share it

Open a [controller report](https://github.com/spshx/switch-xinput-bridge/issues/new?template=controller-report.yml) with the name, VID:PID and anything that didn't work. Or send a pull request that adds a line to `KNOWN_CONTROLLERS` in [`src/switch_xinput_bridge/devices.py`](../src/switch_xinput_bridge/devices.py):

```python
KnownController(0x1234, 0xABCD, "Brand Model", "verified"),
```

Then add a row to the table in the README. Use `"verified"` only if you've tested it with real hardware.

## Controllers with a different report layout

If your controller sends 0x3F reports but some buttons come out wrong, its bytes differ from the standard layout described in [HOW_IT_WORKS.md](HOW_IT_WORKS.md). Please include a raw capture in your report. Run this and press each button one at a time:

```bat
switch-xinput-bridge --device VID:PID --raw
```

It works like `--test`, but also prints the first 16 bytes of each report. Copy the output into your report.
