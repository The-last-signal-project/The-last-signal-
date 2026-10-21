import pytest


from client_python.crypto import (
    mix_before,
    inverse_mix_before,
    rotl8,
    rotr8,
    rotor_groups,
)


# ============================================================
# ROTATION GAUCHE
# ============================================================

@pytest.mark.parametrize("value", range(256))
@pytest.mark.parametrize("shift", range(8))
def test_rotl8_rotr8_round_trip(value, shift):
    rotated = rotl8(value, shift)
    restored = rotr8(rotated, shift)

    assert restored == value


# ============================================================
# ROTATION DROITE
# ============================================================

@pytest.mark.parametrize("value", range(256))
@pytest.mark.parametrize("shift", range(8))
def test_rotr8_rotl8_round_trip(value, shift):
    rotated = rotr8(value, shift)
    restored = rotl8(rotated, shift)

    assert restored == value


# ============================================================
# VALEUR U8
# ============================================================

@pytest.mark.parametrize("value", range(256))
@pytest.mark.parametrize("shift", range(8))
def test_rotations_stay_u8(value, shift):
    assert 0 <= rotl8(value, shift) <= 255
    assert 0 <= rotr8(value, shift) <= 255


# ============================================================
# ROTOR GROUPS
# ============================================================

def test_rotor_groups():
    positions = list(range(16))

    g1, g2, g3, g4 = rotor_groups(positions)

    assert g1 == (0 ^ 4 ^ 8 ^ 12)
    assert g2 == (1 ^ 5 ^ 9 ^ 13)
    assert g3 == (2 ^ 6 ^ 10 ^ 14)
    assert g4 == (3 ^ 7 ^ 11 ^ 15)
@pytest.mark.parametrize("value", range(256))
def test_mix_before_round_trip(value):
    communication_key = bytes(range(64))
    rotor_positions = list(range(16))

    mixed = mix_before(
        value,
        communication_key,
        rotor_positions,
        42,
        123,
    )

    restored = inverse_mix_before(
        mixed,
        communication_key,
        rotor_positions,
        42,
        123,
    )

    assert restored == value
