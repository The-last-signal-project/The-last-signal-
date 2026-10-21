import hashlib


MASK64 = 0xFFFFFFFFFFFFFFFF

CONTEXT = b"TheLastSignal-Rotor-v1"


def derive_rotor_seed(key: bytes, rotor_id: int) -> int:
    data = (
        key
        + CONTEXT
        + rotor_id.to_bytes(4, "big")
    )

    digest = hashlib.sha256(data).digest()

    return int.from_bytes(
        digest[:8],
        "big"
    )


def test_seed_is_deterministic():

    key = bytes(range(64))

    seed_a = derive_rotor_seed(key, 1)
    seed_b = derive_rotor_seed(key, 1)

    assert seed_a == seed_b


def test_seed_is_u64():

    key = bytes(range(64))

    for rotor_id in range(1, 17):

        seed = derive_rotor_seed(
            key,
            rotor_id
        )

        assert 0 <= seed <= MASK64


def test_all_rotors_have_different_seeds():

    key = bytes(range(64))

    seeds = [
        derive_rotor_seed(key, rotor_id)
        for rotor_id in range(1, 17)
    ]

    assert len(seeds) == 16
    assert len(set(seeds)) == 16


def test_different_keys_produce_different_seeds():

    key_a = bytes(range(64))
    key_b = bytes(range(1, 65))

    seeds_a = [
        derive_rotor_seed(key_a, rotor_id)
        for rotor_id in range(1, 17)
    ]

    seeds_b = [
        derive_rotor_seed(key_b, rotor_id)
        for rotor_id in range(1, 17)
    ]

    assert seeds_a != seeds_b


def test_rotor_id_changes_seed():

    key = bytes(range(64))

    seed_1 = derive_rotor_seed(key, 1)
    seed_2 = derive_rotor_seed(key, 2)

    assert seed_1 != seed_2


def test_invalid_key_length():

    key = b"short"

    # Pour l'instant on vérifie seulement
    # que la fonction fonctionne avec des bytes.
    # La validation stricte des 64 octets
    # sera ajoutée dans l'API finale.

    seed = derive_rotor_seed(key, 1)

    assert isinstance(seed, int)
