from client_python.crypto import fisher_yates


def test_is_permutation():

    rotor = fisher_yates(123456789)

    assert len(rotor) == 256
    assert sorted(rotor) == list(range(256))


def test_is_deterministic():

    rotor_a = fisher_yates(123456789)
    rotor_b = fisher_yates(123456789)

    assert rotor_a == rotor_b


def test_different_seeds_produce_different_permutations():

    rotor_a = fisher_yates(123456789)
    rotor_b = fisher_yates(987654321)

    assert rotor_a != rotor_b


def test_contains_every_value_once():

    rotor = fisher_yates(42)

    for value in range(256):
        assert rotor.count(value) == 1


def test_zero_seed():

    rotor = fisher_yates(0)

    assert len(rotor) == 256
    assert sorted(rotor) == list(range(256))


def test_max_seed():

    rotor = fisher_yates(0xFFFFFFFFFFFFFFFF)

    assert len(rotor) == 256
    assert sorted(rotor) == list(range(256))
