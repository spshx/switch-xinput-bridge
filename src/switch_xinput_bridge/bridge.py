"""Device workers: one thread and one virtual Xbox 360 pad per connected controller."""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

from .devices import find_controllers, format_id, known_name
from .mapping import LAYOUT_POSITION, XInputReport, to_xinput
from .report import is_full_report, parse_simple_report
from .sticks import DEFAULT_DEADZONE, calibrate

log = logging.getLogger(__name__)

READ_TIMEOUT_MS = 200
CALIBRATION_SECONDS = 0.5
# These controllers stream constantly (stick noise), so this much silence means
# the Bluetooth link died even though Windows may still show "Connected".
SILENCE_SECONDS = 5.0
SCAN_INTERVAL_SECONDS = 2.0
OPEN_RETRY_SECONDS = 15.0


@dataclass
class Options:
    layout: str = LAYOUT_POSITION
    deadzone: float = DEFAULT_DEADZONE
    test: bool = False
    raw: bool = False
    extra_ids: tuple = ()


class VirtualPad:
    """Thin wrapper over vgamepad's Xbox 360 target."""

    def __init__(self, vg):
        self._pad = vg.VX360Gamepad()
        # A freshly plugged ViGEm pad can report leftover stick values, and the
        # driver drops updates identical to its last state, so send a nudge
        # before going neutral or games see drift until the first real input.
        time.sleep(0.2)
        self._pad.left_joystick(1, 1)
        self._pad.update()
        self.send(XInputReport())

    def send(self, r: XInputReport):
        p = self._pad
        p.reset()
        p.press_button(r.buttons)
        p.left_trigger(r.left_trigger)
        p.right_trigger(r.right_trigger)
        p.left_joystick_float(r.left_x, r.left_y)
        p.right_joystick_float(r.right_x, r.right_y)
        p.update()

    def close(self):
        try:
            self.send(XInputReport())
        except Exception:
            pass
        del self._pad  # vgamepad unplugs the target in __del__


def describe(state, xr: XInputReport) -> str:
    pressed = sorted(state.buttons) + ([f"DPAD_{state.hat_name}"] if state.hat_name else [])
    return (f"buttons: {' '.join(pressed) or '-':42s} "
            f"L({xr.left_x:+.2f},{xr.left_y:+.2f}) R({xr.right_x:+.2f},{xr.right_y:+.2f})")


class ControllerWorker(threading.Thread):
    def __init__(self, hid, vg, info: dict, options: Options, stop: threading.Event):
        super().__init__(daemon=True)
        self.hid, self.vg, self.info, self.options, self.stop = hid, vg, info, options, stop
        vid, pid = info["vendor_id"], info["product_id"]
        product = info.get("product_string") or "controller"
        self.label = f"{known_name(vid, pid) or product} [{format_id(vid, pid)}]"
        self.open_failed = False

    def run(self):
        dev = self.hid.device()
        try:
            dev.open_path(self.info["path"])
        except OSError as e:
            self.open_failed = True
            log.warning("%s: could not open (%s). Is another program using it?", self.label, e)
            return
        pad = None
        try:
            log.info("%s: connected, waiting for input...", self.label)
            sticks = self._calibrate(dev)
            if sticks is None:
                return
            if not self.options.test:
                pad = VirtualPad(self.vg)
                log.info("%s: ready -> virtual Xbox 360 controller (%s layout)",
                         self.label, self.options.layout)
            else:
                log.info("%s: ready (test mode, press buttons to see them)", self.label)
            self._loop(dev, pad, sticks)
        except OSError:
            log.info("%s: disconnected", self.label)
        finally:
            if pad:
                pad.close()
            dev.close()

    def _wait_for_simple_report(self, dev):
        warned_full = warned_silent = False
        start = time.time()
        while not self.stop.is_set():
            r = dev.read(64, READ_TIMEOUT_MS)
            if parse_simple_report(r):
                return r
            if is_full_report(r) and not warned_full:
                warned_full = True
                log.warning("%s: controller is in Switch full mode (0x30). Another program, "
                            "usually Steam, has taken it over. Close it, then turn the "
                            "controller off and on.", self.label)
            if not warned_silent and time.time() - start > SILENCE_SECONDS:
                warned_silent = True
                log.warning("%s: no input yet. Press a button; if nothing happens, remove "
                            "it in Bluetooth settings and pair again.", self.label)
        return None

    def _calibrate(self, dev):
        if self._wait_for_simple_report(dev) is None:
            return None
        samples, end = [], time.time() + CALIBRATION_SECONDS
        while time.time() < end:
            state = parse_simple_report(dev.read(64, READ_TIMEOUT_MS))
            if state:
                samples.append(state.axes)
        return calibrate(samples, self.options.deadzone)

    def _loop(self, dev, pad, sticks):
        last_data, last_line, silent, warned_full = time.time(), None, False, False
        while not self.stop.is_set():
            r = dev.read(64, READ_TIMEOUT_MS)
            state = parse_simple_report(r)
            if state is None:
                if not silent and time.time() - last_data > SILENCE_SECONDS:
                    silent = True
                    log.warning("%s: input stopped (controller asleep or link dropped). "
                                "Press a button; if nothing happens, remove it in Bluetooth "
                                "settings and pair again.", self.label)
                    if pad:
                        pad.send(XInputReport())
                if silent and not warned_full and is_full_report(r):
                    warned_full = True
                    log.warning("%s: controller switched to full mode (0x30), probably by "
                                "Steam. Close it and reconnect the controller.", self.label)
                continue
            last_data = time.time()
            if silent:
                silent = warned_full = False
                log.info("%s: input is back, recalibrating (keep sticks still)", self.label)
                sticks = self._calibrate(dev)
                if sticks is None:
                    return
                continue
            xr = to_xinput(state, sticks, self.options.layout)
            if pad:
                pad.send(xr)
            else:
                line = describe(state, xr)
                if self.options.raw:
                    line = f"{bytes(r[:16]).hex(' ')}  {line}"
                if line != last_line:
                    print(f"{self.label}: {line}", flush=True)
                    last_line = line


def run(options: Options):
    """Bridge every supported controller until Ctrl+C, picking up reconnects."""
    import hid

    vg = None
    if not options.test:
        try:
            import vgamepad as vg
        except Exception as e:  # vgamepad connects to ViGEmBus on import
            raise SystemExit(
                "Could not connect to the ViGEmBus driver. Install it from "
                "https://github.com/nefarius/ViGEmBus/releases and try again.\n"
                f"Details: {e}") from None

    stop = threading.Event()
    workers, retry_after = {}, {}
    announced_waiting = False
    try:
        while True:
            now = time.time()
            for path in [p for p, w in workers.items() if not w.is_alive()]:
                if workers.pop(path).open_failed:
                    retry_after[path] = now + OPEN_RETRY_SECONDS
            for info in find_controllers(hid, options.extra_ids):
                path = info["path"]
                if path not in workers and retry_after.get(path, 0) <= now:
                    w = ControllerWorker(hid, vg, info, options, stop)
                    workers[path] = w
                    w.start()
            if not workers and not announced_waiting:
                log.info("Waiting for a supported controller. Turn it on or pair it in "
                         "Bluetooth settings. (Run with --list to see detected gamepads.)")
            announced_waiting = not workers
            time.sleep(SCAN_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        log.info("Stopping...")
    finally:
        stop.set()
        for w in workers.values():
            w.join(timeout=2)
