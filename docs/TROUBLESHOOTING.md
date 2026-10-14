# Troubleshooting

Start with the diagnostics. They answer most questions:

- `check-controllers.bat` (`switch-xinput-bridge --list`) shows whether Windows sees the controller and what it's sending.
- `test-controller.bat` (`switch-xinput-bridge --test`) shows every button press as it happens.
- Adding `--verbose` to any command prints more detail.

---

## The controller is "Connected" in Windows, but nothing happens

**Symptom:** the bridge prints `input stopped` or `no input yet`, `--list` shows `no data`, and `--test` prints nothing when you press buttons.

**Cause:** this almost always happens after the controller went to sleep or was turned off while still paired. When it wakes, it reconnects at the Bluetooth level but the input channel fails straight away. Windows keeps showing it as connected. In **Event Viewer → Windows Logs → System** you'll see repeated `HidBth` warnings: *"Bluetooth HID device either went out of range or became unresponsive."*

**Fix (most reliable):** pair it again.
1. Close the bridge.
2. Go to **Settings → Bluetooth & devices**, open the **⋯** menu next to the controller and choose **Remove device**.
3. Hold the controller's sync button until its lights flash quickly.
4. Choose **Add device → Bluetooth** and pick the controller.
5. Start the bridge again.

**Fix (quicker, sometimes works):** restart the controller's driver from an **administrator** PowerShell window:

```powershell
Get-PnpDevice -Class HIDClass | Where-Object InstanceId -match "VID&00020E6F_PID&018C" | Select-Object FriendlyName, InstanceId
pnputil /restart-device "<InstanceId of the 'Bluetooth HID Device' entry>"
```

Replace `00020E6F_PID&018C` with your controller's IDs if it's a different model.

**Prevention:** turn the controller off yourself (usually by holding Home) when you stop playing, instead of letting it fall asleep while connected.

## "Could not connect to the ViGEmBus driver"

The bridge needs the ViGEmBus driver to create the virtual Xbox controller. Install `ViGEmBus_1.22.0_x64_x86_arm64.exe` from <https://github.com/nefarius/ViGEmBus/releases>, then reboot. You can check it's installed in Device Manager → System devices → **Nefarius Virtual Gamepad Emulation Bus**.

## "Waiting for a supported controller" never changes

- Make sure the controller is paired and turned on.
- Run `--list`. If your controller appears there as **compatible** but under a different VID:PID than the supported list, start the bridge with `--device VID:PID`.
- If it shows **not compatible**, your controller doesn't use the Switch simple HID protocol. It might have a mode switch: many controllers have a button combination or slider for Switch, X-input and D-input modes. In **X-input** mode it will work in games without this tool.

## The bridge says "full mode (0x30)"

Another program has sent the controller the Switch handshake, and the controller now sends a different report format. **Steam** does this when *Settings → Controller → Enable Switch controller support* is on. Close Steam or turn that setting off, then turn the controller off and on (or pair it again).

If you'd rather use Steam Input, you don't need this tool for Steam games. This tool is for games outside Steam, such as titles launched from the EA app or Epic.

## The game sees two controllers or reacts twice to each press

The game is reading both the real controller (DirectInput) and the virtual Xbox pad. Use [HidHide](https://github.com/nefarius/HidHide) to hide the real controller from games:
1. Install HidHide and open **HidHide Configuration Client**.
2. Under **Applications**, add the bridge's executable: `switch-xinput-bridge.exe`. If you run from source, add the `python.exe` of your Python installation (for example `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`), because the `.venv` launcher hands off to it.
3. Under **Devices**, tick the controller and enable **device hiding**.

## The sticks drift or feel too sensitive

- Keep the sticks still for the first half second after `connected`, because that's when their centres are calibrated.
- Increase the deadzone: `start.bat --deadzone 0.15`.
- The full stick range is learned as you move the sticks. If the first full push feels too sensitive, roll each stick around its edge once after connecting.

## The buttons feel swapped

By default the buttons are mapped by **position**: the bottom face button acts as Xbox A. If you'd rather go by the printed letter, run `start.bat --layout label`.

## Player 1 / player 2 order is wrong in the game

Games number XInput controllers in the order they connect. If you want the bridged controller to be player 1, start the bridge before turning on any other controllers. Otherwise, use the game's own controller assignment screen.

## The anti-cheat or the game blocks virtual controllers

ViGEm virtual controllers are widely used (by DS4Windows, Steam Remote Play tools and others) and normally work fine. A small number of competitive games block them, and this tool can't change that.
