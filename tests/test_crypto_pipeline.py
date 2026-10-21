import pytest

from client_python.crypto import (
    RotorState,
    generate_rotor,
    inverse_mix_before,
    inverse_mix_final,
    mix_before,
    mix_final,
    rotor_forward,
    rotor_inverse,
)


@pytest.mark.parametrize("packet_type", range(1, 10))
def test_full_crypto_pipeline(packet_type):
    communication_key = bytes(range(64))

    encrypt_state = RotorState(
        communication_key=communication_key,
        packet_type=packet_type,
    )

    decrypt_state = RotorState(
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

    plaintext = bytes(
        (i * 37 + 11) & 0xFF
        for i in range(1000)
    )

    ciphertext = []
    previous_ciphertext = 0

    # ========================================================
    # CHIFFREMENT
    # ========================================================

    for byte_counter, value in enumerate(plaintext):

        encrypt_state.update()

        positions = encrypt_state.positions.copy()

        value = mix_before(
            value,
            communication_key,
            positions,
            byte_counter,
            previous_ciphertext,
        )

        for rotor, position in zip(rotors, positions):
            value = rotor_forward(
                value,
                position,
                rotor,
            )

        value = mix_final(
            value,
            communication_key,
            positions,
            byte_counter,
            previous_ciphertext,
            packet_type,
        )

        ciphertext.append(value)
        previous_ciphertext = value

    # ========================================================
    # DÉCHIFFREMENT
    # ========================================================

    decrypted = []
    previous_ciphertext = 0

    for byte_counter, value in enumerate(ciphertext):

        decrypt_state.update()

        positions = decrypt_state.positions.copy()

        value = inverse_mix_final(
            value,
            communication_key,
            positions,
            byte_counter,
            previous_ciphertext,
            packet_type,
        )

        for rotor, position in reversed(
            list(zip(rotors, positions))
        ):
            value = rotor_inverse(
                value,
                position,
                rotor,
            )

        value = inverse_mix_before(
            value,
            communication_key,
            positions,
            byte_counter,
            previous_ciphertext,
        )

        decrypted.append(value)
        previous_ciphertext = ciphertext[byte_counter]

    assert bytes(decrypted) == plaintext
