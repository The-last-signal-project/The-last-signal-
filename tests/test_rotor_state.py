from client_python.crypto import RotorState,derive_rotor_seed


# ============================================================
# INITIALISATION
# ============================================================

def test_rotor_state_has_16_positions():

    state = RotorState(
        communication_key=bytes(range(64)),
        packet_type=1,
    )

    assert len(state.positions) == 16


def test_rotor_state_starts_at_zero():

    state = RotorState(
        communication_key=bytes(range(64)),
        packet_type=1,
    )

    assert state.positions == [0] * 16


# ============================================================
# ROTOR 1
# ============================================================

def test_rotor_1_rotates_by_one_each_byte():

    state = RotorState(
        communication_key=bytes(range(64)),
        packet_type=1,
    )

    state.update()

    assert state.positions[0] == 1

    state.update()

    assert state.positions[0] == 2


def test_rotor_1_wraps():

    state = RotorState(
        communication_key=bytes(range(64)),
        packet_type=1,
    )

    state.positions[0] = 255

    state.update()

    assert state.positions[0] == 0


# ============================================================
# TOURS COMPLETS
# ============================================================

def test_rotor_1_full_rotation():

    state = RotorState(
        communication_key=bytes(range(64)),
        packet_type=1,
    )

    for _ in range(256):
        state.update()

    assert state.positions[0] == 0


def test_rotor_4_reacts_to_rotor_1_full_rotation():

    state = RotorState(
        communication_key=bytes(range(64)),
        packet_type=1,
    )

    for _ in range(256):
        state.update()

    assert state.positions[3] == 8
# ============================================================
# ROTOR 2
# ============================================================

def test_rotor_2_rotates_by_key_each_byte():

    key = bytes(range(64))

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    # Pour le test, on utilise le premier octet de la clé.
    key_value = key[0]

    state.update()

    assert state.positions[1] == key_value

    state.update()

    assert state.positions[1] == (
        key_value * 2
    ) & 0xFF


def test_rotor_2_wraps():

    key = bytes([7] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state.positions[1] = 250

    state.update()

    assert state.positions[1] == 1
# ============================================================
# ROTOR 5
# ============================================================

def test_rotor_5_reacts_to_rotor_2_full_rotation():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(256):
        state.update()

    assert state.positions[1] == 0
    assert state.positions[4] == 251
# ============================================================
# ROTOR 3
# ============================================================

def test_rotor_3_rotates_by_packet_type():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=7,
    )

    state.update()

    assert state.positions[2] == 249

    state.update()

    assert state.positions[2] == 242


def test_rotor_3_wraps():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=7,
    )

    state.positions[2] = 3

    state.update()

    assert state.positions[2] == 252
# ============================================================
# ROTOR 6
# ============================================================

def test_rotor_6_rotates_by_seed_every_two_bytes():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    seed = derive_rotor_seed(key, 6)
    seed_value = seed & 0xFF

    # 1er octet : pas de rotation
    state.update()

    assert state.positions[5] == 0

    # 2e octet : + seed
    state.update()

    assert state.positions[5] == seed_value

    # 3e octet : pas de rotation
    state.update()

    assert state.positions[5] == seed_value

    # 4e octet : + seed
    state.update()

    assert state.positions[5] == (
        seed_value * 2
    ) & 0xFF
    def test_rotor_6_wraps():
        key = bytes([1] * 64)
        state = RotorState(communication_key=key,
           packet_type=1,
           )
        seed = derive_rotor_seed(key, 6)
        seed_value = seed & 0xFF
        state.positions[5] = (
           256 - seed_value
           ) & 0xFF
        state.update()
        state.update()
        assert state.positions[5] == 0
def test_rotor_7_rotation():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state.update()

    assert state.positions[6] == 236

    state.update()

    assert state.positions[6] == 216


def test_rotor_7_wraps():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state.positions[6] = 10

    state.update()

    assert state.positions[6] == 246
# ============================================================
# ROTOR 8
# ============================================================

def test_rotor_8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[7]

    state.update()

    assert state.positions[7] != initial_position


def test_rotor_8_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[7] <= 255


# ============================================================
# ROTOR 9
# ============================================================

def test_rotor_9():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[8]

    state.update()

    assert state.positions[8] != initial_position


def test_rotor_9_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[8] <= 255
def test_rotor_8_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2.positions[0] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[7] != state2.positions[7]


def test_rotor_9_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2.positions[1] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[8] != state2.positions[8]
def test_rotor_8_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2.positions[0] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[7] != state2.positions[7]


def test_rotor_9_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2.positions[1] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[8] != state2.positions[8]
def test_rotor_state_reference_r1_r16():

    key = bytes(range(64))

    state = RotorState(
        communication_key=key,
        packet_type=3,
    )

    for _ in range(10):
        state.update()

    assert state.byte_counter == 10
    assert state.positions == [
        10,
        0,
        226,
        0,
        0,
        139,
        56,
        230,
        64,
        66,
        41,
        161,
        34,
        172,
        72,
        91,
    ]
# ============================================================
# ROTOR 10
# ============================================================

def test_rotor_10_changes():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[9]

    state.update()

    assert state.positions[9] != initial_position


def test_rotor_10_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[9] <= 255


def test_rotor_10_is_deterministic():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    for _ in range(100):
        state1.update()
        state2.update()

        assert state1.positions[9] == state2.positions[9]


def test_rotor_10_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2.positions[0] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[9] != state2.positions[9]
# ============================================================
# ROTOR 11
# ============================================================

def test_rotor_11_changes_each_update():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[10]

    state.update()

    assert state.positions[10] != initial_position


def test_rotor_11_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[10] <= 255


def test_rotor_11_is_deterministic():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    for _ in range(100):
        state1.update()
        state2.update()

        assert state1.positions[10] == state2.positions[10]


def test_rotor_11_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2.positions[1] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[10] != state2.positions[10]
# ============================================================
# ROTOR 12
# ============================================================

def test_rotor_12_changes_each_update():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[11]

    state.update()

    assert state.positions[11] != initial_position


def test_rotor_12_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[11] <= 255


def test_rotor_12_is_deterministic():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    for _ in range(100):
        state1.update()
        state2.update()

        assert state1.positions[11] == state2.positions[11]


def test_rotor_12_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2.positions[0] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[11] != state2.positions[11]
# ============================================================
# ROTOR 13
# ============================================================

def test_rotor_13_changes_each_update():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[12]

    state.update()

    assert state.positions[12] != initial_position


def test_rotor_13_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[12] <= 255


def test_rotor_13_is_deterministic():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    for _ in range(100):
        state1.update()
        state2.update()

        assert state1.positions[12] == state2.positions[12]


def test_rotor_13_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    # R2 est utilisé plusieurs fois dans la formule R13.
    state2.positions[1] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[12] != state2.positions[12]
# ============================================================
# ROTOR 14
# ============================================================

def test_rotor_14_changes_each_update():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[13]

    state.update()

    assert state.positions[13] != initial_position


def test_rotor_14_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[13] <= 255


def test_rotor_14_is_deterministic():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    for _ in range(100):
        state1.update()
        state2.update()

        assert state1.positions[13] == state2.positions[13]


def test_rotor_14_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    # R4 intervient directement dans le calcul de R14.
    state2.positions[3] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[13] != state2.positions[13]
# ============================================================
# ROTOR 15
# ============================================================

def test_rotor_15_changes_each_update():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[14]

    state.update()

    assert state.positions[14] != initial_position


def test_rotor_15_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[14] <= 255


def test_rotor_15_is_deterministic():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    for _ in range(100):
        state1.update()
        state2.update()

        assert state1.positions[14] == state2.positions[14]


def test_rotor_15_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    # R10 intervient directement dans le calcul de R15.
    state2.positions[9] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[14] != state2.positions[14]
# ============================================================
# ROTOR 16
# ============================================================

def test_rotor_16_changes_each_update():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    initial_position = state.positions[15]

    state.update()

    assert state.positions[15] != initial_position


def test_rotor_16_stays_in_u8():

    key = bytes([1] * 64)

    state = RotorState(
        communication_key=key,
        packet_type=1,
    )

    for _ in range(1000):
        state.update()

        assert 0 <= state.positions[15] <= 255


def test_rotor_16_is_deterministic():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=3,
    )

    for _ in range(100):
        state1.update()
        state2.update()

        assert state1.positions[15] == state2.positions[15]


def test_rotor_16_depends_on_state():

    key = bytes(range(64))

    state1 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    state2 = RotorState(
        communication_key=key,
        packet_type=1,
    )

    # R15 intervient directement dans le calcul de R16.
    state2.positions[14] ^= 0x55

    state1.update()
    state2.update()

    assert state1.positions[15] != state2.positions[15]
