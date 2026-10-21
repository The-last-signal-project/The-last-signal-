import pytest

from client_python.crypto import (
    RotorState,
    generate_rotor,
    mix_before,
    mix_final,
    rotor_forward,
)


def encrypt_reference(
    communication_key,
    packet_type,
    plaintext,
):
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

    ciphertext = []
    previous_ciphertext = 0

    for byte_counter, value in enumerate(plaintext):
        state.update()

        positions = state.positions.copy()

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

    return bytes(ciphertext)


@pytest.mark.parametrize(
    "packet_type, expected",
    [
        (1, "e2d0c4f302ea3da12ce8af9b852460d4"),
        (2, "7fabeba06378b7008931bb28552e9c54"),
        (3, "0bd95e008752e01024d66fc1e2927d9a"),
        (4, "8169db319e9d65941cb6712d06c7f9e5"),
        (5, "95997b1d3274ba5b25f2a747337b06e3"),
        (6, "0a79ca20d68373815974a73c4e39db8e"),
        (7, "c746f799a8d46175cbfc50cd80fe7c85"),
        (8, "3cef509235062d02e5c7856d666ccc35"),
        (9, "696106774cfcaffd46d70629e4b00e1c"),
    ],
)
def test_reference_vectors_all_packet_types(
    packet_type,
    expected,
):
    communication_key = bytes(range(64))
    plaintext = bytes(range(16))

    ciphertext = encrypt_reference(
        communication_key,
        packet_type,
        plaintext,
    )

    assert ciphertext == bytes.fromhex(expected)
    EXPECTED_CIPHERTEXT_1024 = (
    "d94bb5ebf56b877384fa33309b859170d7b887159f7a96c4a1dc6f8a4bef3b14"
    "ec10e44d6abf163f846dc2815185c08bfcc6aa20ec168ef2d8cd06d25b3499a6"
    "5a28d3094496452ddab5c128ab9e929fef7b4207f2932bc0ab7f58b63dc44ece"
    "9265ab03e0b0c80bba69405f018e0d808b7c98790b417ed792b09e9b425b8cc1"
    "a64f51843a61fad33df6cb5709f829faac82f6f4560bac42ee041ce01c17685c"
    "b543adf256a0234d6b320b04ed377a20d4551ae82c190dc7e50572ea9b3fd399"
    "38ae6d35fb6e8f1aa3092c3f06e72d9c0c06c05823e4169a947dab2db6b68c62"
    "c037ffd1877be6ab5300e405d0b87889f57cd6e57fc4e76750317f6197747094"
    "c0d9c31b94cce01c3dafe8506f9593dd066a02cec6c7def00211608336c2140c"
    "9082999e6ebe468ff8cebcceb3fe25bfc89f38e22cd2e4e5a98dd44274bbfd19"
    "ee400f3c0369b28a2d7d35b0db418723290eb23ec473790cdab6aa52f9956d22"
    "26078bd1c7a6c1d90aaebb5b0b2feda1392c026afdceac378c435a6da87555f2"
    "d1acf84dded60d2217f63ca87c26fb21ea077e1a186e6434c651be42cd732cd8"
    "537cbc65c30aa0cee33a66cbab217c49d3cc3fa5bb04db38e951c38c6390f43e"
    "c19c2ab54f70ff8075835476bfa425fcad4fcfe6d5e73d165a9442a68a580026"
    "a327f9a5c452dc74431a120a4b29b470e17d7a6a6d0eba5e95b433c694ad0192"
    "8be0663cf6f45e05b82d36edf3662e2aacff49d865e31a09ea3c724f67619214"
    "6818bd17c57f2d9fcaf69db8ee96618318b1b77185879e0adb90ad18104ea59e"
    "cddddfc8ee3d3729be651c58c8356373b34ac9ca7b351cb093947dcfffc4d4cd"
    "f5cf06026df360637c6dcd15c7708509a1f18a50eb2b5910462fbe5b21e500df"
    "18908dea245fb3db36fd7f15ccd09d01258095f7edac842b1f07113b3524847e"
    "faa4a3e19fa9ace04a3568e34a277fc91f8376d14361783ccac17a5c7708b35d"
    "e6eadecee9b3b97d79aa8c21e6630ac28401149ef3e0150714e9cf4ea6446610"
    "47c1fee6a58869117b0e32e7c59bd6cf583a47ebdbd728f1cdc4d0455394b6a0"
    "8ca4d2341ddf3fb4cf55cbec5fef48b8aa64120a9c8bbadaeecac5e492190d76"
    "c3be9dce001fd9858392a6898c38cb803f97c5a668d063e822439b2a4c8e2cf2"
    "4ba65a584026c540b70547d381172963f9f0d2938fc3bd6fc6361dd577a0989d"
    "dde66f41e062efebc81e6b66f2fdce7de3526f868c24f6b359a482c826b7fbfc"
    "2b7f62ad9e4ff1d3569818c87e334459f8b6f46c2e1dcde0893e6206711d99ea"
    "6f8b1956399988295d52e49a956b9925403601ce967fc6146259a0f93b0bb7d0"
    "15e408e3fa8a54c49c8dae242a5bf19007133597a8b4ae81753c15836a3a2fa4"
    "fee898c72f5bda8cd03e568f51f7254b41fad7159b84a0cb9d3d2c4f1ef27f9e"
    )
    def test_reference_vector_1024_bytes():
        communication_key = bytes(range(64))
        packet_type = 1
        plaintext = bytes(
            (i * 37 + 11) & 0xFF
            for i in range(1024))
        ciphertext = encrypt_reference(
            communication_key,
            packet_type,
            plaintext,)
        assert ciphertext == bytes.fromhex(
            EXPECTED_CIPHERTEXT_1024)
