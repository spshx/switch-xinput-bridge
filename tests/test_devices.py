import pytest

from switch_xinput_bridge.devices import (KNOWN_CONTROLLERS, find_controllers, format_id,
                                          list_gamepads, parse_id)


class FakeHid:
    def __init__(self, devices):
        self.devices = devices

    def enumerate(self, vid=0, pid=0):
        return list(self.devices)


def dev(vid, pid, path, usage_page=1, usage=5):
    return {"vendor_id": vid, "product_id": pid, "path": path,
            "usage_page": usage_page, "usage": usage, "product_string": "x"}


def test_id_round_trip():
    assert parse_id("0e6f:018c") == (0x0E6F, 0x018C)
    assert format_id(0x0E6F, 0x018C) == "0E6F:018C"
    with pytest.raises(ValueError):
        parse_id("nonsense")


def test_lic_controller_is_known():
    assert any(c.id == "0E6F:018C" and c.status == "verified" for c in KNOWN_CONTROLLERS)


def test_find_known_and_extra_controllers():
    hid = FakeHid([
        dev(0x0E6F, 0x018C, b"lic"),
        dev(0x0E6F, 0x018C, b"lic"),       # duplicate path
        dev(0x045E, 0x0B20, b"xbox"),      # unrelated gamepad
        dev(0x1234, 0x5678, b"custom"),
    ])
    assert [d["path"] for d in find_controllers(hid)] == [b"lic"]
    assert [d["path"] for d in find_controllers(hid, [(0x1234, 0x5678)])] == [b"lic", b"custom"]


def test_list_gamepads_filters_by_usage():
    hid = FakeHid([dev(1, 1, b"pad"), dev(2, 2, b"kbd", usage=6), dev(3, 3, b"joy", usage=4)])
    assert [d["path"] for d in list_gamepads(hid)] == [b"pad", b"joy"]
