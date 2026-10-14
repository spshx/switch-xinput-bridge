"""Known controllers and HID discovery."""
from __future__ import annotations

import time
from dataclasses import dataclass

from .report import is_full_report, parse_simple_report

# HID generic desktop usages for joysticks and gamepads
USAGE_PAGE_GENERIC = 0x01
GAMEPAD_USAGES = (0x04, 0x05)


@dataclass(frozen=True)
class KnownController:
    vid: int
    pid: int
    name: str
    status: str  # "verified" = confirmed by a real user, "expected" = same protocol, untested

    @property
    def id(self) -> str:
        return format_id(self.vid, self.pid)


# Add new entries via a pull request once someone has confirmed it works
# (see docs/ADDING_A_CONTROLLER.md).
KNOWN_CONTROLLERS = (
    KnownController(0x0E6F, 0x018C, "Lic Pro Controller (Switch / Switch 2 style)", "verified"),
    KnownController(0x057E, 0x2009, "Nintendo Switch Pro Controller", "expected"),
)


def format_id(vid: int, pid: int) -> str:
    return f"{vid:04X}:{pid:04X}"


def parse_id(text: str) -> tuple:
    """'0E6F:018C' -> (0x0E6F, 0x018C)"""
    try:
        vid, pid = text.split(":")
        return int(vid, 16), int(pid, 16)
    except ValueError:
        raise ValueError(f"expected VID:PID in hex, like 0E6F:018C, got {text!r}") from None


def known_name(vid: int, pid: int) -> str | None:
    for c in KNOWN_CONTROLLERS:
        if (c.vid, c.pid) == (vid, pid):
            return c.name
    return None


def find_controllers(hid, extra_ids=()) -> list:
    """HID device dicts for every connected controller we should bridge."""
    wanted = {(c.vid, c.pid) for c in KNOWN_CONTROLLERS} | set(extra_ids)
    found, seen = [], set()
    for info in hid.enumerate():
        if (info["vendor_id"], info["product_id"]) in wanted and info["path"] not in seen:
            seen.add(info["path"])
            found.append(info)
    return found


def list_gamepads(hid) -> list:
    """Every HID joystick/gamepad Windows exposes, known or not."""
    pads, seen = [], set()
    for info in hid.enumerate():
        if (info["usage_page"] == USAGE_PAGE_GENERIC and info["usage"] in GAMEPAD_USAGES
                and info["path"] not in seen):
            seen.add(info["path"])
            pads.append(info)
    return pads


def probe(hid, path: bytes, seconds: float = 1.5) -> str:
    """Read briefly from a device and classify what it sends."""
    dev = hid.device()
    try:
        dev.open_path(path)
    except OSError:
        return "could not open (in use or disconnected)"
    try:
        end = time.time() + seconds
        saw_other = None
        while time.time() < end:
            r = dev.read(64, 200)
            if not r:
                continue
            if parse_simple_report(r):
                return "compatible (Switch simple HID 0x3F reports)"
            if is_full_report(r):
                return "Switch full-mode 0x30 reports (close Steam / other tools and reconnect)"
            saw_other = r[0]
        if saw_other is not None:
            return f"not compatible (report ID 0x{saw_other:02X})"
        return "no data (press a button while probing, or re-pair the controller)"
    finally:
        dev.close()
