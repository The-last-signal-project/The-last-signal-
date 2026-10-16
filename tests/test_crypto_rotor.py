import pytest
from client_python.crypto import (
    SplitMix64,
    derive_rotor_seed,
    generate_rotor,
    generate_rotors,
    rotor_forward,
    rotor_inverse,
)


# ============================================================
# FIXTURE
# ============================================================
MASK_64 = 0xFFFFFFFFFFFFFFFF
@pytest.fixture
def communication_key():

    return bytes(
        range(64)
    )


# ============================================================
# TESTS SPLITMIX64
# ============================================================

def test_splitmix64_deterministic():

    generator1 = SplitMix64(123456789)
    generator2 = SplitMix64(123456789)

    value1 = generator1.next()
    value2 = generator2.next()

    assert value1 == value2
    assert generator1.state == generator2.state


def test_splitmix64_different_seeds():

    generator1 = SplitMix64(1)
    generator2 = SplitMix64(2)

    value1 = generator1.next()
    value2 = generator2.next()

    assert value1 != value2


def test_splitmix64_is_u64():

    generator = SplitMix64(MASK_64)

    value = generator.next()

    assert 0 <= value <= MASK_64







# ============================================================
# TESTS DES SEEDS
# ============================================================

def test_rotor_seed_deterministic(
    communication_key,
):

    seed1 = derive_rotor_seed(
        communication_key,
        1,
    )

    seed2 = derive_rotor_seed(
        communication_key,
        1,
    )

    assert seed1 == seed2


def test_rotor_seeds_are_different(
    communication_key,
):

    seeds = [
        derive_rotor_seed(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(1, 17)
    ]

    assert len(set(seeds)) == 16


def test_rotor_seed_is_u64(
    communication_key,
):

    for rotor_id in range(1, 17):

        seed = derive_rotor_seed(
            communication_key,
            rotor_id,
        )

        assert 0 <= seed <= MASK_64


# ============================================================
# TESTS DES ROTORS
# ============================================================

def test_rotor_has_256_values(
    communication_key,
):

    rotor = generate_rotor(
        communication_key,
        1,
    )

    assert len(rotor) == 256


def test_rotor_is_permutation(
    communication_key,
):

    rotor = generate_rotor(
        communication_key,
        1,
    )

    assert sorted(rotor) == list(
        range(256)
    )


def test_all_16_rotors_are_valid(
    communication_key,
):

    for rotor_id in range(1, 17):

        rotor = generate_rotor(
            communication_key,
            rotor_id,
        )

        assert len(rotor) == 256

        assert sorted(rotor) == list(
            range(256)
        )


def test_rotor_is_deterministic(
    communication_key,
):

    rotor1 = generate_rotor(
        communication_key,
        1,
    )

    rotor2 = generate_rotor(
        communication_key,
        1,
    )

    assert rotor1 == rotor2


def test_rotors_are_different(
    communication_key,
):

    rotors = [
        generate_rotor(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(1, 17)
    ]

    for i in range(16):

        for j in range(i + 1, 16):

            assert rotors[i] != rotors[j]


# ============================================================
# TEST FORWARD / INVERSE
# ============================================================

@pytest.mark.parametrize(
    "value",
    range(256),
)
@pytest.mark.parametrize(
    "position",
    [
        0,
        1,
        2,
        127,
        128,
        254,
        255,
    ],
)
def test_rotor_forward_inverse(
    communication_key,
    value,
    position,
):

    rotor = generate_rotor(
        communication_key,
        1,
    )

    encrypted = rotor_forward(
        value,
        position,
        rotor,
    )

    decrypted = rotor_inverse(
        encrypted,
        position,
        rotor,
    )

    assert decrypted == value


# ============================================================
# TEST DES 16 ROTORS
# ============================================================

@pytest.mark.parametrize(
    "value",
    range(256),
)
def test_all_16_rotors_forward_inverse(
    communication_key,
    value,
):

    for rotor_id in range(1, 17):

        rotor = generate_rotor(
            communication_key,
            rotor_id,
        )

        position = (
            rotor_id * 17
        ) & 0xFF

        encrypted = rotor_forward(
            value,
            position,
            rotor,
        )

        decrypted = rotor_inverse(
            encrypted,
            position,
            rotor,
        )

        assert decrypted == value
def test_rotors_are_valid_permutations(
    communication_key,
):

    rotors = [
        generate_rotor(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(1, 17)
    ]

    for rotor in rotors:

        assert len(rotor) == 256
        assert sorted(rotor) == list(range(256))
def test_rotors_are_deterministic(
    communication_key,
):

    rotors1 = [
        generate_rotor(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(1, 17)
    ]

    rotors2 = [
        generate_rotor(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(1, 17)
    ]

    assert rotors1 == rotors2
def test_rotors_depend_on_key():

    key1 = bytes(range(64))
    key2 = bytes([255] * 64)

    for rotor_id in range(1, 17):

        rotor1 = generate_rotor(
            key1,
            rotor_id,
        )

        rotor2 = generate_rotor(
            key2,
            rotor_id,
        )

        assert rotor1 != rotor2
@pytest.mark.parametrize(
    "value",
    range(256),
)
def test_all_16_rotors_round_trip(
    communication_key,
    value,
):

    rotors = [
        generate_rotor(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(1, 17)
    ]

    positions = [
        (rotor_id * 17) & 0xFF
        for rotor_id in range(1, 17)
    ]

    original = value

    # Forward : R1 -> R16
    for rotor, position in zip(
        rotors,
        positions,
    ):
        value = rotor_forward(
            value,
            position,
            rotor,
        )

    # Inverse : R16 -> R1
    for rotor, position in reversed(
        list(zip(rotors, positions))
    ):
        value = rotor_inverse(
            value,
            position,
            rotor,
        )

    assert value == original
def test_invalid_communication_key():

    with pytest.raises(ValueError):
        generate_rotors(b"too-short")
