import hashlib
MASK_64 = 0xFFFFFFFFFFFFFFFF

ROTOR_COUNT = 16
ROTOR_SIZE = 256
COMMUNICATION_KEY_SIZE = 64

ROTOR_DOMAIN = b"TheLastSignal-Rotor-v1"


'''
============================================================
                   SPLITMIX64
============================================================
'''
class SplitMix64:

    def __init__(self, seed):
        self.state = seed & MASK_64

    def next(self):

        self.state = (
            self.state
            + 0x9E3779B97F4A7C15
        ) & MASK_64

        z = self.state

        z = (
            (z ^ (z >> 30))
            * 0xBF58476D1CE4E5B9
        ) & MASK_64

        z = (
            (z ^ (z >> 27))
            * 0x94D049BB133111EB
        ) & MASK_64

        z ^= z >> 31

        return z & MASK_64



'''
============================================================
                   DERIVATION DES SEEDS
============================================================
'''


def derive_rotor_seed(
    communication_key,
    rotor_id,
):

    if len(communication_key) != COMMUNICATION_KEY_SIZE:
        raise ValueError(
            "Communication_key must be exactly 64 bytes"
        )

    if not 1 <= rotor_id <= ROTOR_COUNT:
        raise ValueError(
            "rotor_id must be between 1 and 16"
        )

    rotor_id_bytes = rotor_id.to_bytes(
        4,
        "big",
    )

    data = (
        communication_key
        + ROTOR_DOMAIN
        + rotor_id_bytes
    )

    digest = hashlib.sha256(data).digest()

    return int.from_bytes(
        digest[:8],
        "big",
    )

'''
============================================================
                   FISHER-YATES
============================================================
'''


def fisher_yates(seed):

    rotor = list(range(ROTOR_SIZE))

    rng = SplitMix64(seed)

    for i in range(
        ROTOR_SIZE - 1,
        0,
        -1,
    ):

        j = rng.next() % (i + 1)

        rotor[i], rotor[j] = (
            rotor[j],
            rotor[i],
        )

    return rotor

'''
============================================================
                   GÉNÉRATION D'UN ROTOR
============================================================
'''


def generate_rotor(
    communication_key,
    rotor_id,
):

    seed = derive_rotor_seed(
        communication_key,
        rotor_id,
    )

    return fisher_yates(seed)

'''
============================================================
                   GÉNÉRATION DES 16 ROTORS
============================================================
'''


def generate_rotors(
    communication_key,
):

    if len(communication_key) != COMMUNICATION_KEY_SIZE:
        raise ValueError(
            "Communication_key must be exactly 64 bytes"
        )

    return [
        generate_rotor(
            communication_key,
            rotor_id,
        )
        for rotor_id in range(
            1,
            ROTOR_COUNT + 1,
        )
    ]

'''
============================================================
                   PERMUTATION INVERSE
============================================================
'''


def inverse_permutation(permutation):

    if len(permutation) != ROTOR_SIZE:
        raise ValueError(
            "A rotor must contain exactly 256 values"
        )

    inverse = [0] * ROTOR_SIZE

    for index, value in enumerate(permutation):
        inverse[value] = index

    return inverse

'''
============================================================
                   ROTOR FORWARD
============================================================
'''


def rotor_forward(
    value,
    position,
    permutation,
):

    value = (
        value + position
    ) & 0xFF

    value = permutation[value]

    value = (
        value - position
    ) & 0xFF

    return value

'''
============================================================
                   ROTOR INVERSE
============================================================
'''


def rotor_inverse(
    value,
    position,
    permutation,
):

    inverse = inverse_permutation(
        permutation
    )

    value = (
        value + position
    ) & 0xFF

    value = inverse[value]

    value = (
        value - position
    ) & 0xFF

    return value

class RotorState:

    def __init__(self, communication_key, packet_type):
        if len(communication_key) != 64:
            raise ValueError(
                "Communication_key must be exactly 64 bytes"
            )

        self.communication_key = communication_key
        self.packet_type = packet_type

        self.positions = [0] * 16
        self.byte_counter = 0
        self.rotor_6_seed = derive_rotor_seed(
    communication_key,
    6,
) & 0xFF
    def update(self):
        
        # R1
        

        previous_r1 = self.positions[0]

        self.positions[0] = (
                self.positions[0] + 1
               ) & 0xFF

        r1_completed_rotation = (
            previous_r1 == 255
            and self.positions[0] == 0
        )

        # R4
        if r1_completed_rotation:
                self.positions[3] = (
                self.positions[3] + 8
                ) & 0xFF

      
        # R2
      

        key_value = self.communication_key[0]

        previous_r2 = self.positions[1]

        self.positions[1] = (
            self.positions[1] + key_value
        ) & 0xFF

        # Détection d'un tour complet de R2
        r2_completed_rotation = (
            previous_r2 + key_value >= 256
        )

  
        # R5 
        

        if r2_completed_rotation:
            self.positions[4] = (self.positions[4] - 5) & 0xFF
        
        # R3

        self.positions[2] = (self.positions[2] - self.packet_type) & 0xFF
        # R6
        if (self.byte_counter + 1) % 2 == 0:
            self.positions[5] = (
                        self.positions[5]
                        + self.rotor_6_seed) & 0xFF
        # R7
        self.positions[6] = (
                 self.positions[6] - 20
                  ) & 0xFF
      
                # R8
        r8_value = (
            self.positions[0]
            ^ self.positions[2]
            ^ self.positions[5]
            ^ self.positions[6]
        )

        r8_value ^= self.byte_counter & 0xFF

        r8_value = (
            r8_value
            + (
                self.positions[3]
                & self.positions[7]
            )
        ) & 0xFF

        r8_value ^= (
            (self.positions[4] * 3)
            & 0xFF
        )

        r8_value ^= (
            (r8_value << 3)
            & 0xFF
        )

        self.positions[7] = (
            self.positions[7] + r8_value
        ) & 0xFF

        # R9
        r9_value = (
            self.positions[1]
            ^ self.positions[3]
            ^ self.positions[4]
            ^ self.positions[6]
        )

        r9_value ^= (
            self.byte_counter * 3
        ) & 0xFF

        r9_value = (
            r9_value
            + (
                self.positions[5]
                & self.positions[8]
            )
        ) & 0xFF

        r9_value ^= (
            (self.positions[0] * 5)
            & 0xFF
        )

        r9_value ^= (
            r9_value >> 3
        )

        self.positions[8] = (
            self.positions[8] - r9_value
        ) & 0xFF

        
        # ========================================================
        # Compteur d'octets
        # ========================================================
                # R8
        ...

        # R9
        ...

        # R10
        r10_value = (
            self.positions[0]
            ^ self.positions[3]
            ^ self.positions[6]
        )

        r10_value ^= (
            self.positions[1] >> 2
        )

        r10_value = (
            r10_value
            + (
                self.positions[4]
                & self.positions[8]
                & self.positions[9]
            )
        ) & 0xFF

        r10_value ^= (
            (self.positions[2] * 7)
            & 0xFF
        )

        r10_value ^= (
            (r10_value << 2)
            & 0xFF
        )

        self.positions[9] = (
            self.positions[9] + r10_value
        ) & 0xFF
        # R11
        r11_value = (
            self.positions[1]
            ^ self.positions[4]
            ^ self.positions[7]
        )

        r11_value = (
            r11_value
            + (
                self.positions[2]
                & self.positions[9]
            )
        ) & 0xFF

        r11_value ^= (
            (self.positions[3] * 9)
            & 0xFF
        )

        r11_value = (
            ((r11_value << 3) & 0xFF)
            | (r11_value >> 5)
        )

        r11_value = (
            r11_value
            + self.positions[5]
        ) & 0xFF

        self.positions[10] = (
            self.positions[10] + r11_value
        ) & 0xFF
        # R12
        r12_value = (
            self.positions[0]
            ^ self.positions[5]
            ^ self.positions[8]
            ^ self.positions[10]
        )

        r12_value ^= (
            self.positions[2] >> 3
        )

        r12_value = (
            r12_value
            + (
                self.positions[6]
                & self.positions[9]
                & self.positions[11]
            )
        ) & 0xFF

        r12_value ^= (
            (self.positions[3] * 11)
            & 0xFF
        )

        r12_value = (
            ((r12_value << 2) & 0xFF)
            | (r12_value >> 6)
        )

        self.positions[11] = (
            self.positions[11] - r12_value
        ) & 0xFF
                # R13
        r13_value = (
            self.positions[0]
            ^ self.positions[2]
            ^ self.positions[5]
            ^ self.positions[7]
            ^ self.positions[11]
        )

        r13_value ^= (
            self.positions[2] >> 2
        )

        r13_value = (
            r13_value
            + (
                self.positions[1]
                & self.positions[4]
                & self.positions[8]
            )
        ) & 0xFF

        r13_value ^= (
            (self.positions[5] * 13)
            & 0xFF
        )

        r13_value = (
            r13_value
            + self.positions[3]
            + self.positions[6]
            + self.positions[9]
        ) & 0xFF

        r13_value ^= (
            (self.positions[10] << 3)
            & 0xFF
        )

        r13_value = (
            ((r13_value << 5) & 0xFF)
            | (r13_value >> 3)
        )

        self.positions[12] = (
            self.positions[12] + r13_value
        ) & 0xFF
        # R14
        r14_value = (
          self.positions[0]
          ^ self.positions[3]
          ^ self.positions[6]
          ^ self.positions[9]
          ^ self.positions[12])
        r14_value ^= (
            self.positions[1] >> 3)
        r14_value = ( r14_value +
        (
        self.positions[4]
        & self.positions[7]
        & self.positions[10]
        )
        ) & 0xFF
        r14_value ^= (
            (self.positions[2] * 17)
            & 0xFF)
        r14_value = ( r14_value +
               + self.positions[5]
               + self.positions[8]
               + self.positions[11]
              ) & 0xFF
        r14_value ^= (
            (self.positions[12] << 2)
            & 0xFF)
        r14_value = (
            ((r14_value << 4) & 0xFF)
            | (r14_value >> 4))
        self.positions[13] = (
          self.positions[13] - r14_value
          ) & 0xFF
        # R15
        r15_value = (
          self.positions[1]
          ^ self.positions[4]
          ^ self.positions[7]
          ^ self.positions[10]
          ^ self.positions[13])
        r15_value ^= (
            self.positions[2] >> 2)
        r15_value = (
            r15_value
            + (
            self.positions[5]
            & self.positions[8]
            & self.positions[11])
            ) & 0xFF
        r15_value ^= (
          (self.positions[3] * 19)
          & 0xFF)
        r15_value = (
          r15_value
          + self.positions[0]
          + self.positions[6]
          + self.positions[9]
          + self.positions[12]) & 0xFF
        r15_value ^= (
          (self.positions[13] << 3)
          & 0xFF)
        # Rotation gauche de 6 bits
        r15_value = (
            ((r15_value << 6) & 0xFF)
            | (r15_value >> 2))
        self.positions[14] = (
            self.positions[14] + r15_value
            ) & 0xFF
        # R16
        r16_value = (
            self.positions[0]
            ^ self.positions[4]
            ^ self.positions[8]
            ^ self.positions[12]
            ^ self.positions[14])
        r16_value ^= (
            self.positions[1] >> 4)
        r16_value = (
            r16_value
            + (
                self.positions[3]
                & self.positions[6]
                & self.positions[10])
             ) & 0xFF
        r16_value ^= (
            (self.positions[5] * 23)& 0xFF)
        r16_value = (
            r16_value
            + self.positions[2]
            + self.positions[7]
            + self.positions[11]
            + self.positions[13]) & 0xFF
        r16_value ^= (
            (self.positions[14] << 2)
            & 0xFF)
        # Rotation gauche de 7 bits
        r16_value = (
            ((r16_value << 7) & 0xFF)
            | (r16_value >> 1))
        self.positions[15] = (
            self.positions[15] - r16_value
            ) & 0xFF
        # Compteur d'octets
        self.byte_counter += 1
        
def rotl8(value, shift):
    value &= 0xFF
    shift &= 7

    if shift == 0:
        return value

    return (
        ((value << shift) & 0xFF)
        | (value >> (8 - shift))
    )


def rotr8(value, shift):
    value &= 0xFF
    shift &= 7

    if shift == 0:
        return value

    return (
        (value >> shift)
        | ((value << (8 - shift)) & 0xFF)
      )
def rotor_groups(rotor_positions):
    return (
        rotor_positions[0]
        ^ rotor_positions[4]
        ^ rotor_positions[8]
        ^ rotor_positions[12],
        rotor_positions[1]
        ^ rotor_positions[5]
        ^ rotor_positions[9]
        ^ rotor_positions[13],
        rotor_positions[2]
        ^ rotor_positions[6]
        ^ rotor_positions[10]
        ^ rotor_positions[14],
        rotor_positions[3]
        ^ rotor_positions[7]
        ^ rotor_positions[11]
        ^ rotor_positions[15],
    )
def mix_before(
    value,
    communication_key,
    rotor_positions,
    byte_counter,
    previous_ciphertext,
):
    if len(communication_key) != 64:
        raise ValueError(
            "Communication_key must be exactly 64 bytes"
        )

    if len(rotor_positions) != 16:
        raise ValueError(
            "rotor_positions must contain exactly 16 values"
        )

    value &= 0xFF
    byte_counter &= 0xFF
    previous_ciphertext &= 0xFF

    k0 = communication_key[0]
    k1 = communication_key[1]

    g1, g2, _, _ = rotor_groups(rotor_positions)

    value ^= k0
    value = (value + rotor_positions[3]) & 0xFF

    shift = (
        communication_key[11]
        ^ byte_counter
        ^ rotor_positions[7]
    ) & 7
    value = rotl8(value, shift)

    value ^= previous_ciphertext

    value = (value - g1) & 0xFF

    shift = (
        communication_key[27]
        ^ byte_counter
        ^ rotor_positions[8]
    ) & 7
    value = rotl8(value, shift)

    value = (value + g2) & 0xFF
    value ^= k1

    return value & 0xFF
def inverse_mix_before(
    value,
    communication_key,
    rotor_positions,
    byte_counter,
    previous_ciphertext,
):
    if len(communication_key) != 64:
        raise ValueError(
            "Communication_key must be exactly 64 bytes"
        )

    if len(rotor_positions) != 16:
        raise ValueError(
            "rotor_positions must contain exactly 16 values"
        )

    value &= 0xFF
    byte_counter &= 0xFF
    previous_ciphertext &= 0xFF

    k0 = communication_key[0]
    k1 = communication_key[1]

    g1, g2, _, _ = rotor_groups(rotor_positions)

    value ^= k1

    value = (value - g2) & 0xFF

    shift = (
        communication_key[27]
        ^ byte_counter
        ^ rotor_positions[8]
    ) & 7
    value = rotr8(value, shift)

    value = (value + g1) & 0xFF

    value ^= previous_ciphertext

    shift = (
        communication_key[11]
        ^ byte_counter
        ^ rotor_positions[7]
    ) & 7
    value = rotr8(value, shift)

    value = (value - rotor_positions[3]) & 0xFF

    value ^= k0

    return value & 0xFF
def mix_final(
    value,
    communication_key,
    rotor_positions,
    byte_counter,
    previous_ciphertext,
    packet_type,
):
    if len(communication_key) != 64:
        raise ValueError(
            "Communication_key must be exactly 64 bytes"
        )

    if len(rotor_positions) != 16:
        raise ValueError(
            "rotor_positions must contain exactly 16 values"
        )

    value &= 0xFF
    byte_counter &= 0xFF
    previous_ciphertext &= 0xFF
    packet_type &= 0xFF

    k0 = communication_key[0]
    k2 = communication_key[2]

    _, _, g3, g4 = rotor_groups(rotor_positions)

    value ^= g3

    value = (value + k2) & 0xFF

    shift = (
        communication_key[19]
        ^ byte_counter
        ^ rotor_positions[7]
        ^ packet_type
    ) & 7
    value = rotl8(value, shift)

    value ^= previous_ciphertext

    value = (value + communication_key[42]) & 0xFF

    shift = (
        communication_key[47]
        ^ byte_counter
        ^ rotor_positions[8]
    ) & 7
    value = rotl8(value, shift)

    value = (value - g4) & 0xFF

    value ^= k0

    return value & 0xFF
def inverse_mix_final(
    value,
    communication_key,
    rotor_positions,
    byte_counter,
    previous_ciphertext,
    packet_type,
):
    if len(communication_key) != 64:
        raise ValueError(
            "Communication_key must be exactly 64 bytes"
        )

    if len(rotor_positions) != 16:
        raise ValueError(
            "rotor_positions must contain exactly 16 values"
        )

    value &= 0xFF
    byte_counter &= 0xFF
    previous_ciphertext &= 0xFF
    packet_type &= 0xFF

    k0 = communication_key[0]
    k2 = communication_key[2]

    _, _, g3, g4 = rotor_groups(rotor_positions)

    value ^= k0

    value = (value + g4) & 0xFF

    shift = (
        communication_key[47]
        ^ byte_counter
        ^ rotor_positions[8]
    ) & 7
    value = rotr8(value, shift)

    value = (value - communication_key[42]) & 0xFF

    value ^= previous_ciphertext

    shift = (
        communication_key[19]
        ^ byte_counter
        ^ rotor_positions[7]
        ^ packet_type
    ) & 7
    value = rotr8(value, shift)

    value = (value - k2) & 0xFF

    value ^= g3

    return value & 0xFF
