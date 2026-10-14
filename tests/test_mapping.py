import pytest

from switch_xinput_bridge import mapping as m
from switch_xinput_bridge.report import HAT_RELEASED, ControllerState
from switch_xinput_bridge.sticks import INITIAL_HALF_RANGE, calibrate

CENTRE = (0x8000,) * 4


def state(buttons=(), hat=HAT_RELEASED, axes=CENTRE):
    return ControllerState(frozenset(buttons), hat, axes)


def sticks():
    return calibrate([CENTRE])


def test_neutral():
    assert m.to_xinput(state(), sticks()) == m.XInputReport()


@pytest.mark.parametrize("switch, xbox", [("B", m.A), ("A", m.B), ("Y", m.X), ("X", m.Y)])
def test_position_layout(switch, xbox):
    assert m.to_xinput(state([switch]), sticks(), m.LAYOUT_POSITION).buttons == xbox


@pytest.mark.parametrize("switch, xbox", [("A", m.A), ("B", m.B), ("X", m.X), ("Y", m.Y)])
def test_label_layout(switch, xbox):
    assert m.to_xinput(state([switch]), sticks(), m.LAYOUT_LABEL).buttons == xbox


def test_shoulders_menu_and_sticks():
    r = m.to_xinput(state(["L", "R", "PLUS", "MINUS", "HOME", "LSTICK", "RSTICK"]), sticks())
    assert r.buttons == (m.LEFT_SHOULDER | m.RIGHT_SHOULDER | m.START | m.BACK
                         | m.GUIDE | m.LEFT_THUMB | m.RIGHT_THUMB)


def test_triggers_are_digital():
    r = m.to_xinput(state(["ZL", "ZR"]), sticks())
    assert (r.left_trigger, r.right_trigger, r.buttons) == (255, 255, 0)


@pytest.mark.parametrize("hat, expected", [
    (0, m.DPAD_UP), (1, m.DPAD_UP | m.DPAD_RIGHT), (2, m.DPAD_RIGHT),
    (4, m.DPAD_DOWN), (6, m.DPAD_LEFT), (7, m.DPAD_UP | m.DPAD_LEFT),
])
def test_dpad(hat, expected):
    assert m.to_xinput(state(hat=hat), sticks()).buttons == expected


def test_stick_y_is_inverted_for_xinput():
    down_right = (0x8000 + INITIAL_HALF_RANGE, 0x8000 + INITIAL_HALF_RANGE, 0x8000, 0x8000)
    r = m.to_xinput(state(axes=down_right), sticks())
    assert r.left_x == pytest.approx(1.0)
    assert r.left_y == pytest.approx(-1.0)  # HID down -> XInput negative
