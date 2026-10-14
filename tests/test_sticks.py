import pytest

from switch_xinput_bridge.sticks import INITIAL_HALF_RANGE, Axis, calibrate


def test_centre_and_noise_are_zero():
    a = Axis(0x7A00)
    for raw in (0x7A00, 0x79E0, 0x7A10, 0x7A30):
        assert a.value(raw) == 0.0


def test_full_deflection_both_ways():
    a = Axis(0x8000)
    assert a.value(0x8000 + INITIAL_HALF_RANGE) == pytest.approx(1.0)
    assert a.value(0x8000 - INITIAL_HALF_RANGE) == pytest.approx(-1.0)


def test_deadzone_is_rescaled_not_clipped():
    a = Axis(0x8000, deadzone=0.1)
    just_outside = 0x8000 + int(INITIAL_HALF_RANGE * 0.11)
    assert 0.0 < a.value(just_outside) < 0.05


def test_range_grows_and_output_is_clamped():
    a = Axis(0x8000)
    far = 0x8000 + INITIAL_HALF_RANGE + 0x1000
    assert a.value(far) == pytest.approx(1.0)
    # after learning the larger range, the old "full" point is no longer full
    assert a.value(0x8000 + INITIAL_HALF_RANGE) < 1.0


def test_invalid_deadzone():
    with pytest.raises(ValueError):
        Axis(0x8000, deadzone=1.0)


def test_calibrate_averages_samples():
    axes = calibrate([(100, 200, 300, 400), (300, 400, 500, 600)])
    assert [a.centre for a in axes] == [200, 300, 400, 500]


def test_calibrate_without_samples_uses_midpoint():
    assert all(a.centre == 0x8000 for a in calibrate([]))
