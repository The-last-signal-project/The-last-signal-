import pytest
from client_python.crypto import (
    rotor_forward,
    rotor_inverse,
    inverse_mix_final,
    mix_final,
    RotorState,generate_rotor
)

@pytest.mark.parametrize(
    "value",
    range(256),
)
def test_rotor_state_round_trip(
    value,
):

    communication_key = bytes(range(64))

    state = RotorState(
        communication_key=communication_key,
        packet_type=1,
    )

    rotors = [
        generate_rotor(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(1, 17)
    ]

    state.update()

    positions = state.positions.copy()

    original = value

    # Forward : R1 → R16
    for rotor, position in zip(
        rotors,
        positions,
    ):
        value = rotor_forward(
            value,
            position,
            rotor,
        )

    # Inverse : R16 → R1
    for rotor, position in reversed(
        list(zip(rotors, positions))
    ):
        value = rotor_inverse(
            value,
            position,
            rotor,
        )

    assert value == original
@pytest.mark.parametrize(
    "packet_type",
    range(1, 10),
)
@pytest.mark.parametrize(
    "value",
    range(256),
)
def test_rotor_state_multiple_updates(
    value,
    packet_type,
):

    communication_key = bytes(range(64))

    state = RotorState(
        communication_key=communication_key,
        packet_type=packet_type,
    )

    rotors = [
        generate_rotor(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(1, 17)
    ]

    original = value

    for _ in range(100):

        state.update()

        positions = state.positions.copy()

        encrypted = original

        # R1 → R16
        for rotor, position in zip(
            rotors,
            positions,
        ):
            encrypted = rotor_forward(
                encrypted,
                position,
                rotor,
            )

        decrypted = encrypted

        # R16 → R1
        for rotor, position in reversed(
            list(zip(rotors, positions))
        ):
            decrypted = rotor_inverse(
                decrypted,
                position,
                rotor,
            )

        assert decrypted == original



@pytest.mark.parametrize("packet_type", range(1, 10))
def test_rotor_stream_round_trip(packet_type):
    communication_key = bytes(range(64))

    state = RotorState(
        communication_key=communication_key,
        packet_type=packet_type,
    )

    rotors = [
        generate_rotor(communication_key, rotor_id)
        for rotor_id in range(1, 17)
    ]

    plaintext = bytes(
        (i * 37 + 11) & 0xFF
        for i in range(1000)
    )

    ciphertext = []

    # Chiffrement : un update par octet
    for value in plaintext:
        state.update()

        positions = state.positions.copy()

        encrypted = value

        for rotor, position in zip(rotors, positions):
            encrypted = rotor_forward(
                encrypted,
                position,
                rotor,
            )

        ciphertext.append(encrypted)

    # Nouveau RotorState pour le déchiffrement
    decrypt_state = RotorState(
        communication_key=communication_key,
        packet_type=packet_type,
    )

    decrypted = []

    for value in ciphertext:
        decrypt_state.update()

        positions = decrypt_state.positions.copy()

        decrypted_value = value

        for rotor, position in reversed(
            list(zip(rotors, positions))
        ):
            decrypted_value = rotor_inverse(
                decrypted_value,
                position,
                rotor,
            )

        decrypted.append(decrypted_value)

    assert bytes(decrypted) == plaintext
@pytest.mark.parametrize("value", range(256))
@pytest.mark.parametrize("packet_type", range(1, 10))
def test_mix_final_round_trip(value, packet_type):
    communication_key = bytes(range(64))
    rotor_positions = list(range(16))

    mixed = mix_final(
        value,
        communication_key,
        rotor_positions,
        42,
        123,
        packet_type,
    )

    restored = inverse_mix_final(
        mixed,
        communication_key,
        rotor_positions,
        42,
        123,
        packet_type,
    )

    assert restored == value
