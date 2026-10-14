from switch_xinput_bridge.report import (HAT_RELEASED, is_full_report,
                                         parse_simple_report)

# Real idle report captured from a Lic Pro Controller over Bluetooth
IDLE = bytes.fromhex("3f 00 00 08 00 7a df 74 40 78 bf 8a 00 80 30") + bytes(49)


def with_bytes(**changes):
    r = bytearray(IDLE)
    for index, value in changes.items():
        r[int(index[1:])] = value
    return list(r)


def test_idle_report():
    s = parse_simple_report(list(IDLE))
    assert s.buttons == frozenset()
    assert s.hat == HAT_RELEASED and s.hat_name is None
    assert s.axes == (0x7A00, 0x74DF, 0x7840, 0x8ABF)


def test_byte1_buttons():
    s = parse_simple_report(with_bytes(b1=0xFF))
    assert s.buttons == {"B", "A", "Y", "X", "L", "R", "ZL", "ZR"}
    assert parse_simple_report(with_bytes(b1=0x02)).buttons == {"A"}


def test_byte2_buttons():
    s = parse_simple_report(with_bytes(b2=0x3F))
    assert s.buttons == {"MINUS", "PLUS", "LSTICK", "RSTICK", "HOME", "CAPTURE"}


def test_hat():
    assert parse_simple_report(with_bytes(b3=0)).hat_name == "UP"
    assert parse_simple_report(with_bytes(b3=3)).hat_name == "DOWN_RIGHT"
    assert parse_simple_report(with_bytes(b3=7)).hat_name == "UP_LEFT"
    # out-of-range values are treated as released
    assert parse_simple_report(with_bytes(b3=0x0F)).hat == HAT_RELEASED


def test_rejects_other_reports():
    assert parse_simple_report([]) is None
    assert parse_simple_report([0x3F, 0, 0]) is None
    assert parse_simple_report([0x30] + [0] * 48) is None
    assert parse_simple_report([0x01] + [0] * 11) is None


def test_full_report_detection():
    assert is_full_report([0x30, 0, 0])
    assert not is_full_report(list(IDLE))
    assert not is_full_report([])
