"""Translate a Switch controller state into an Xbox 360 (XInput) report."""
from __future__ import annotations

from dataclasses import dataclass

from .report import ControllerState

# XINPUT_GAMEPAD button bits (identical to vgamepad.XUSB_BUTTON values)
DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT = 0x0001, 0x0002, 0x0004, 0x0008
START, BACK, LEFT_THUMB, RIGHT_THUMB = 0x0010, 0x0020, 0x0040, 0x0080
LEFT_SHOULDER, RIGHT_SHOULDER, GUIDE = 0x0100, 0x0200, 0x0400
A, B, X, Y = 0x1000, 0x2000, 0x4000, 0x8000

LAYOUT_POSITION = "position"
LAYOUT_LABEL = "label"
LAYOUTS = (LAYOUT_POSITION, LAYOUT_LABEL)

# "position": the physical spot matches Xbox prompts (Switch B, bottom, = Xbox A).
# "label": the printed letter matches (Switch A = Xbox A, even though it sits right).
FACE_BUTTONS = {
    LAYOUT_POSITION: {"B": A, "A": B, "Y": X, "X": Y},
    LAYOUT_LABEL: {"A": A, "B": B, "X": X, "Y": Y},
}
OTHER_BUTTONS = {
    "L": LEFT_SHOULDER, "R": RIGHT_SHOULDER,
    "MINUS": BACK, "PLUS": START, "CAPTURE": BACK, "HOME": GUIDE,
    "LSTICK": LEFT_THUMB, "RSTICK": RIGHT_THUMB,
}
HAT_BUTTONS = (
    DPAD_UP, DPAD_UP | DPAD_RIGHT, DPAD_RIGHT, DPAD_DOWN | DPAD_RIGHT,
    DPAD_DOWN, DPAD_DOWN | DPAD_LEFT, DPAD_LEFT, DPAD_UP | DPAD_LEFT,
)


@dataclass(frozen=True)
class XInputReport:
    buttons: int = 0
    left_trigger: int = 0
    right_trigger: int = 0
    left_x: float = 0.0   # -1.0 .. 1.0, up/right positive
    left_y: float = 0.0
    right_x: float = 0.0
    right_y: float = 0.0


def to_xinput(state: ControllerState, sticks, layout: str = LAYOUT_POSITION) -> XInputReport:
    """`sticks` is four calibrated Axis objects (see sticks.calibrate)."""
    face = FACE_BUTTONS[layout]
    buttons = 0
    for name in state.buttons:
        buttons |= face.get(name, 0) | OTHER_BUTTONS.get(name, 0)
    if state.hat < len(HAT_BUTTONS):
        buttons |= HAT_BUTTONS[state.hat]
    lx, ly, rx, ry = (axis.value(raw) for axis, raw in zip(sticks, state.axes))
    return XInputReport(
        buttons=buttons,
        # ZL/ZR are digital on these controllers
        left_trigger=255 if "ZL" in state.buttons else 0,
        right_trigger=255 if "ZR" in state.buttons else 0,
        # HID Y grows downward, XInput Y grows upward
        left_x=lx, left_y=-ly, right_x=rx, right_y=-ry,
    )
