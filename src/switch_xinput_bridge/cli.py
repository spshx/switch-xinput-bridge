"""Command line entry point."""
from __future__ import annotations

import argparse
import logging
import sys

from . import __version__
from .bridge import Options, run
from .devices import KNOWN_CONTROLLERS, format_id, known_name, list_gamepads, parse_id, probe
from .mapping import LAYOUT_POSITION, LAYOUTS
from .sticks import DEFAULT_DEADZONE


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="switch-xinput-bridge",
        description="Make Switch-style Bluetooth controllers (e.g. the Lic Pro Controller) "
                    "show up as Xbox 360 controllers so XInput-only PC games accept them.")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--test", action="store_true",
                      help="print what the controller sends instead of creating a virtual pad")
    mode.add_argument("--raw", action="store_true",
                      help="like --test, but also print the raw report bytes (for bug reports)")
    mode.add_argument("--list", action="store_true",
                      help="list connected gamepads and whether they are compatible, then exit")
    p.add_argument("--layout", choices=LAYOUTS, default=LAYOUT_POSITION,
                   help="'position' (default): bottom face button = Xbox A, like the on-screen "
                        "prompts; 'label': Switch A = Xbox A by printed letter")
    p.add_argument("--deadzone", type=float, default=DEFAULT_DEADZONE, metavar="0.0-0.9",
                   help=f"stick deadzone as a fraction of full tilt (default {DEFAULT_DEADZONE})")
    p.add_argument("--device", action="append", default=[], metavar="VID:PID",
                   help="also bridge this controller, e.g. --device 0E6F:018C (repeatable)")
    p.add_argument("--verbose", action="store_true", help="debug logging")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def list_command() -> int:
    import hid

    print("Supported out of the box:")
    for c in KNOWN_CONTROLLERS:
        print(f"  {c.id}  {c.name} ({c.status})")
    pads = list_gamepads(hid)
    print("\nGamepads connected now (probing each for ~1.5 s, press a button if it shows 'no data'):")
    if not pads:
        print("  none found. Is the controller paired and turned on?")
    for info in pads:
        vid, pid = info["vendor_id"], info["product_id"]
        name = known_name(vid, pid) or info.get("product_string") or "unknown"
        print(f"  {format_id(vid, pid)}  {name}: {probe(hid, info['path'])}")
    print("\nA 'compatible' device that isn't in the supported list can be used with "
          "--device VID:PID. Please report it so it can be added (see README).")
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
    if not 0.0 <= args.deadzone < 0.9:
        print("--deadzone must be between 0.0 and 0.9", file=sys.stderr)
        return 2
    try:
        extra = tuple(parse_id(d) for d in args.device)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    if args.list:
        return list_command()
    print(f"switch-xinput-bridge {__version__}. Keep this window open while playing; "
          "Ctrl+C to quit.", flush=True)
    run(Options(layout=args.layout, deadzone=args.deadzone, test=args.test or args.raw,
                raw=args.raw, extra_ids=extra))
    return 0


if __name__ == "__main__":
    sys.exit(main())
