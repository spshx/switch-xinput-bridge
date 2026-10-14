# How it works

## Why the game ignores the controller

Windows has two main gamepad APIs:

- **DirectInput / HID**, the old generic one. Any HID gamepad shows up here, with no fixed button meanings.
- **XInput**, the Xbox controller API. Only Xbox-compatible devices show up here, and every button has a fixed meaning.

Many modern PC games, including most Unreal Engine titles like *It Takes Two*, only read XInput. A Switch-style controller paired over Bluetooth shows up as a generic HID gamepad ("HID-compliant game controller" in Device Manager), so those games never see it.

## The 0x3F simple HID report

When a Switch Pro-style controller connects over Bluetooth, it starts in a basic HID mode. It stays there unless the host sends it a vendor handshake, which only Switch consoles, Steam and a few drivers do. In this mode it sends report ID `0x3F` continuously, because stick noise means the data never stops changing:

| Byte | Contents |
|---|---|
| 0 | Report ID `0x3F` |
| 1 | `B`=bit0, `A`=bit1, `Y`=bit2, `X`=bit3, `L`=bit4, `R`=bit5, `ZL`=bit6, `ZR`=bit7 |
| 2 | `−`=bit0, `+`=bit1, `LStick`=bit2, `RStick`=bit3, `Home`=bit4, `Capture`=bit5 |
| 3 | Hat (D-pad): `0`=up, clockwise to `7`=up-left, `8`=released |
| 4–5 | Left stick X (uint16, little-endian, centre ≈ `0x8000`) |
| 6–7 | Left stick Y (grows **downward**) |
| 8–9 | Right stick X |
| 10–11 | Right stick Y (grows **downward**) |
| 12+ | Vendor specific, ignored |

Here's a real idle report from a Lic Pro Controller (`0E6F:018C`):

```
3f 00 00 08 00 7a df 74 40 78 bf 8a 00 80 30 00 ...
   └─┬─┘ │  └─LX─┘ └─LY─┘ └─RX─┘ └─RY─┘
  buttons hat=released
```

The stick centres aren't exactly `0x8000` (here they're `0x7A00`, `0x74DF`, `0x7840` and `0x8ABF`), so the bridge measures the centre for half a second at startup instead of assuming it.

After a handshake, controllers switch to the "full" `0x30` report, which has 12-bit packed sticks plus IMU data. The bridge doesn't decode `0x30`. It detects it and tells you to close the program that sent the handshake.

## Calibration and deadzone

`sticks.Axis` works like this for each axis:

1. It uses the average of the resting samples as the centre.
2. It assumes a half-range of `0x5800` on each side, and widens that whenever the stick goes further. Each side is tracked separately, because centres are often off-middle.
3. It applies a deadzone (default 10%) and rescales the remaining travel, so motion still starts smoothly from 0 at the edge of the deadzone.

The Y axes are inverted at the end, because XInput uses "up = positive".

## Virtual Xbox pad

[ViGEmBus](https://github.com/nefarius/ViGEmBus) is a kernel driver that creates virtual Xbox 360 or DualShock 4 controllers. These are indistinguishable from real ones to games. The bridge creates one virtual Xbox 360 pad per physical controller and sends it a new XInput report every time a HID report arrives.

**Quirk worked around:** a newly plugged ViGEm Xbox 360 target can report leftover non-zero stick values. The driver also skips updates that are identical to the report it last received. As a result, sending an all-neutral report first does nothing, and games see the sticks drift until the first real input. The bridge sends a tiny non-zero report before the first neutral one, which forces a real update (`bridge.VirtualPad.__init__`).

## Connection handling

- A scanner thread looks for supported controllers every 2 seconds and starts one worker per device, so reconnects and multiple controllers are handled automatically.
- If a controller sends nothing for 5 seconds, the worker resets its virtual pad to neutral (so no button gets stuck down) and warns that the link has probably dropped. When reports come back, it recalibrates the sticks.
- When the HID device goes away, the worker unplugs its virtual pad.
