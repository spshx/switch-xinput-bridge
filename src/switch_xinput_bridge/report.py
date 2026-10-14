"""Parsing of Nintendo Switch "simple HID" input reports (report ID 0x3F).

When a Switch Pro-style controller connects over Bluetooth it starts out in a
basic HID mode and streams 0x3F reports until a host sends it a handshake. Most
third-party "Switch / Switch 2 Pro" controllers stay in this mode on a PC:

    byte 0      report ID (0x3F)
    byte 1      buttons: B A Y X L R ZL ZR            (bit 0 .. bit 7)
    byte 2      buttons: - + LStick RStick Home Capture (bit 0 .. bit 5)
    byte 3      hat (D-pad): 0 = up, clockwise to 7 = up-left, 8 = released
    bytes 4-11  left X, left Y, right X, right Y as little-endian uint16,
                centred near 0x8000, Y growing downward

If another program (usually Steam) has sent the handshake, the controller
switches to "full" 0x30 reports instead, which this module does not decode.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

SIMPLE_REPORT_ID = 0x3F
FULL_REPORT_ID = 0x30
SIMPLE_REPORT_MIN_LEN = 12
HAT_RELEASED = 8

BYTE1_BUTTONS = {0x01: "B", 0x02: "A", 0x04: "Y", 0x08: "X",
                 0x10: "L", 0x20: "R", 0x40: "ZL", 0x80: "ZR"}
BYTE2_BUTTONS = {0x01: "MINUS", 0x02: "PLUS", 0x04: "LSTICK",
                 0x08: "RSTICK", 0x10: "HOME", 0x20: "CAPTURE"}
ALL_BUTTONS = tuple(BYTE1_BUTTONS.values()) + tuple(BYTE2_BUTTONS.values())

HAT_NAMES = ("UP", "UP_RIGHT", "RIGHT", "DOWN_RIGHT",
             "DOWN", "DOWN_LEFT", "LEFT", "UP_LEFT")


@dataclass(frozen=True)
class ControllerState:
    buttons: frozenset
    hat: int
    axes: tuple  # raw (left_x, left_y, right_x, right_y)

    @property
    def hat_name(self) -> Optional[str]:
        return HAT_NAMES[self.hat] if self.hat < HAT_RELEASED else None


def parse_simple_report(report: Sequence[int]) -> Optional[ControllerState]:
    """Decode a 0x3F report, or return None if it is anything else."""
    if len(report) < SIMPLE_REPORT_MIN_LEN or report[0] != SIMPLE_REPORT_ID:
        return None
    buttons = frozenset(
        [name for bit, name in BYTE1_BUTTONS.items() if report[1] & bit]
        + [name for bit, name in BYTE2_BUTTONS.items() if report[2] & bit])
    hat = report[3] if report[3] <= HAT_RELEASED else HAT_RELEASED
    axes = tuple(report[i] | report[i + 1] << 8 for i in (4, 6, 8, 10))
    return ControllerState(buttons, hat, axes)


def is_full_report(report: Sequence[int]) -> bool:
    return bool(report) and report[0] == FULL_REPORT_ID
