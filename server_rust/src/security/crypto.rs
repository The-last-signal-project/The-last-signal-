use sha2::{Digest, Sha256};
const MASK_64: u64 = 0xFFFF_FFFF_FFFF_FFFF;
const COMMUNICATION_KEY_SIZE: usize = 64;
const ROTOR_COUNT: usize = 16;
const ROTOR_DOMAIN: &[u8] = b"TheLastSignal-Rotor-v1";
const ROTOR_SIZE: usize = 256;


pub struct SplitMix64 {
    state: u64,
}

impl SplitMix64 {
    pub fn new(seed: u64) -> Self {
        Self {
            state: seed & MASK_64,
        }
    }

    pub fn next(&mut self) -> u64 {
        self.state = self
            .state
            .wrapping_add(0x9E37_79B9_7F4A_7C15);

        let mut z = self.state;

        z = (z ^ (z >> 30))
            .wrapping_mul(0xBF58_476D_1CE4_E5B9);

        z = (z ^ (z >> 27))
            .wrapping_mul(0x94D0_49BB_1331_11EB);

        z ^= z >> 31;

        z & MASK_64
    }
}


pub fn derive_rotor_seed(
    communication_key: &[u8],
    rotor_id: u8,
) -> Result<u64, &'static str> {
    if communication_key.len() != COMMUNICATION_KEY_SIZE {
        return Err("Communication_key must be exactly 64 bytes");
    }

    if !(1..=ROTOR_COUNT as u8).contains(&rotor_id) {
        return Err("rotor_id must be between 1 and 16");
    }

    let mut hasher = Sha256::new();

    hasher.update(communication_key);
    hasher.update(ROTOR_DOMAIN);
    hasher.update((rotor_id as u32).to_be_bytes());

    let digest = hasher.finalize();

    let seed = u64::from_be_bytes(
        digest[..8]
            .try_into()
            .expect("SHA-256 digest is at least 8 bytes"),
    );

    Ok(seed)
}

pub fn fisher_yates(seed: u64) -> [u8; ROTOR_SIZE] {
    let mut rotor = [0u8; ROTOR_SIZE];

    for (index, value) in rotor.iter_mut().enumerate() {
        *value = index as u8;
    }

    let mut rng = SplitMix64::new(seed);

    for i in (1..ROTOR_SIZE).rev() {
        let j = (rng.next() % (i as u64 + 1)) as usize;

        rotor.swap(i, j);
    }

    rotor
}


pub fn generate_rotor(
    communication_key: &[u8],
    rotor_id: u8,
) -> Result<[u8; ROTOR_SIZE], &'static str> {
    let seed = derive_rotor_seed(communication_key, rotor_id)?;

    Ok(fisher_yates(seed))
}

pub fn generate_rotors(
    communication_key: &[u8],
) -> Result<[[u8; ROTOR_SIZE]; ROTOR_COUNT], &'static str> {
    if communication_key.len() != COMMUNICATION_KEY_SIZE {
        return Err("Communication_key must be exactly 64 bytes");
    }

    let mut rotors = [[0u8; ROTOR_SIZE]; ROTOR_COUNT];

    for rotor_id in 1..=ROTOR_COUNT {
        rotors[rotor_id - 1] =
            generate_rotor(communication_key, rotor_id as u8)?;
    }

    Ok(rotors)
}
pub fn rotor_forward(
    value: u8,
    position: u8,
    permutation: &[u8; ROTOR_SIZE],
) -> u8 {
    let shifted = value.wrapping_add(position);
    let permuted = permutation[shifted as usize];
    permuted.wrapping_sub(position)
}

pub fn inverse_permutation(
    permutation: &[u8; ROTOR_SIZE],
) -> [u8; ROTOR_SIZE] {
    let mut inverse = [0u8; ROTOR_SIZE];

    for (index, &value) in permutation.iter().enumerate() {
        inverse[value as usize] = index as u8;
    }

    inverse
}

pub fn rotor_inverse(
    value: u8,
    position: u8,
    permutation: &[u8; ROTOR_SIZE],
) -> u8 {
    let inverse = inverse_permutation(permutation);
    let shifted = value.wrapping_add(position);
    let permuted = inverse[shifted as usize];

    permuted.wrapping_sub(position)
}

#[derive(Debug, Clone)]
pub struct RotorState {
    communication_key: [u8; COMMUNICATION_KEY_SIZE],
    packet_type: u8,
    positions: [u8; ROTOR_COUNT],
    byte_counter: u64,
    rotor_6_seed: u8,
}

impl RotorState {
    pub fn new(
        communication_key: &[u8],
        packet_type: u8,
    ) -> Result<Self, &'static str> {
        let key: [u8; COMMUNICATION_KEY_SIZE] =
            communication_key
                .try_into()
                .map_err(|_| "Communication_key must be exactly 64 bytes")?;

        let rotor_6_seed = derive_rotor_seed(&key, 6)? as u8;

        Ok(Self {
            communication_key: key,
            packet_type,
            positions: [0; ROTOR_COUNT],
            byte_counter: 0,
            rotor_6_seed,
        })
    }

    pub fn positions(&self) -> &[u8; ROTOR_COUNT] {
        &self.positions
    }

    pub fn byte_counter(&self) -> u64 {
        self.byte_counter
    }

    pub fn update(&mut self) {
        // R1
        let previous_r1 = self.positions[0];
        self.positions[0] = self.positions[0].wrapping_add(1);

        let r1_completed_rotation =
            previous_r1 == 255 && self.positions[0] == 0;

        // R4
        if r1_completed_rotation {
            self.positions[3] = self.positions[3].wrapping_add(8);
        }

        // R2
        let key_value = self.communication_key[0];
        let previous_r2 = self.positions[1];

        self.positions[1] = self.positions[1].wrapping_add(key_value);

        let r2_completed_rotation =
            (previous_r2 as u16 + key_value as u16) >= 256;

        // R5
        if r2_completed_rotation {
            self.positions[4] = self.positions[4].wrapping_sub(5);
        }

        // R3
        self.positions[2] =
            self.positions[2].wrapping_sub(self.packet_type);

        // R6
        if self.byte_counter.wrapping_add(1) % 2 == 0 {
            self.positions[5] =
                self.positions[5].wrapping_add(self.rotor_6_seed);
        }

        // R7
        self.positions[6] = self.positions[6].wrapping_sub(20);

        // R8
        let mut r8_value =
            self.positions[0]
            ^ self.positions[2]
            ^ self.positions[5]
            ^ self.positions[6];

        r8_value ^= self.byte_counter as u8;
        r8_value = r8_value.wrapping_add(
            self.positions[3] & self.positions[7],
        );
        r8_value ^= self.positions[4].wrapping_mul(3);
        r8_value ^= r8_value.wrapping_shl(3);

        self.positions[7] = self.positions[7].wrapping_add(r8_value);

        // R9
        let mut r9_value =
            self.positions[1]
            ^ self.positions[3]
            ^ self.positions[4]
            ^ self.positions[6];

        r9_value ^= (self.byte_counter as u8).wrapping_mul(3);
        r9_value = r9_value.wrapping_add(
            self.positions[5] & self.positions[8],
        );
        r9_value ^= self.positions[0].wrapping_mul(5);
        r9_value ^= r9_value >> 3;

        self.positions[8] = self.positions[8].wrapping_sub(r9_value);

        // R10
        let mut r10_value =
            self.positions[0]
            ^ self.positions[3]
            ^ self.positions[6];

        r10_value ^= self.positions[1] >> 2;
        r10_value = r10_value.wrapping_add(
            self.positions[4] & self.positions[8] & self.positions[9],
        );
        r10_value ^= self.positions[2].wrapping_mul(7);
        r10_value ^= r10_value.wrapping_shl(2);

        self.positions[9] = self.positions[9].wrapping_add(r10_value);

        // R11
        let mut r11_value =
            self.positions[1]
            ^ self.positions[4]
            ^ self.positions[7];

        r11_value = r11_value.wrapping_add(
            self.positions[2] & self.positions[9],
        );
        r11_value ^= self.positions[3].wrapping_mul(9);

        r11_value = r11_value.rotate_left(3);
        r11_value = r11_value.wrapping_add(self.positions[5]);

        self.positions[10] =
            self.positions[10].wrapping_add(r11_value);

        // R12
        let mut r12_value =
            self.positions[0]
            ^ self.positions[5]
            ^ self.positions[8]
            ^ self.positions[10];

        r12_value ^= self.positions[2] >> 3;
        r12_value = r12_value.wrapping_add(
            self.positions[6] & self.positions[9] & self.positions[11],
        );
        r12_value ^= self.positions[3].wrapping_mul(11);

        r12_value = r12_value.rotate_left(2);

        self.positions[11] =
            self.positions[11].wrapping_sub(r12_value);

        // R13
        let mut r13_value =
            self.positions[0]
            ^ self.positions[2]
            ^ self.positions[5]
            ^ self.positions[7]
            ^ self.positions[11];

        r13_value ^= self.positions[2] >> 2;
        r13_value = r13_value.wrapping_add(
            self.positions[1] & self.positions[4] & self.positions[8],
        );
        r13_value ^= self.positions[5].wrapping_mul(13);

        r13_value = r13_value
            .wrapping_add(self.positions[3])
            .wrapping_add(self.positions[6])
            .wrapping_add(self.positions[9]);

        r13_value ^= self.positions[10].wrapping_shl(3);
        r13_value = r13_value.rotate_left(5);

        self.positions[12] =
            self.positions[12].wrapping_add(r13_value);

        // R14
        let mut r14_value =
            self.positions[0]
            ^ self.positions[3]
            ^ self.positions[6]
            ^ self.positions[9]
            ^ self.positions[12];

        r14_value ^= self.positions[1] >> 3;
        r14_value = r14_value.wrapping_add(
            self.positions[4] & self.positions[7] & self.positions[10],
        );
        r14_value ^= self.positions[2].wrapping_mul(17);

        r14_value = r14_value
            .wrapping_add(self.positions[5])
            .wrapping_add(self.positions[8])
            .wrapping_add(self.positions[11]);

        r14_value ^= self.positions[12].wrapping_shl(2);
        r14_value = r14_value.rotate_left(4);

        self.positions[13] =
            self.positions[13].wrapping_sub(r14_value);

        // R15
        let mut r15_value =
            self.positions[1]
            ^ self.positions[4]
            ^ self.positions[7]
            ^ self.positions[10]
            ^ self.positions[13];

        r15_value ^= self.positions[2] >> 2;
        r15_value = r15_value.wrapping_add(
            self.positions[5] & self.positions[8] & self.positions[11],
        );
        r15_value ^= self.positions[3].wrapping_mul(19);

        r15_value = r15_value
            .wrapping_add(self.positions[0])
            .wrapping_add(self.positions[6])
            .wrapping_add(self.positions[9])
            .wrapping_add(self.positions[12]);

        r15_value ^= self.positions[13].wrapping_shl(3);
        r15_value = r15_value.rotate_left(6);

        self.positions[14] =
            self.positions[14].wrapping_add(r15_value);

        // R16
        let mut r16_value =
            self.positions[0]
            ^ self.positions[4]
            ^ self.positions[8]
            ^ self.positions[12]
            ^ self.positions[14];

        r16_value ^= self.positions[1] >> 4;
        r16_value = r16_value.wrapping_add(
            self.positions[3] & self.positions[6] & self.positions[10],
        );
        r16_value ^= self.positions[5].wrapping_mul(23);

        r16_value = r16_value
            .wrapping_add(self.positions[2])
            .wrapping_add(self.positions[7])
            .wrapping_add(self.positions[11])
            .wrapping_add(self.positions[13]);

        r16_value ^= self.positions[14].wrapping_shl(2);
        r16_value = r16_value.rotate_left(7);

        self.positions[15] =
            self.positions[15].wrapping_sub(r16_value);

        // Le compteur avance après toutes les mises à jour.
        self.byte_counter = self.byte_counter.wrapping_add(1);
    }
}

pub fn rotl8(value: u8, shift: u32) -> u8 {
    value.rotate_left(shift % 8)
}

pub fn rotr8(value: u8, shift: u32) -> u8 {
    value.rotate_right(shift % 8)
}

/// Calcule les quatre groupes de rotors selon l'implémentation Python.
pub fn rotor_groups(
    positions: &[u8; ROTOR_COUNT],
) -> (u8, u8, u8, u8) {
    let g1 = positions[0] ^ positions[4] ^ positions[8] ^ positions[12];
    let g2 = positions[1] ^ positions[5] ^ positions[9] ^ positions[13];
    let g3 = positions[2] ^ positions[6] ^ positions[10] ^ positions[14];
    let g4 = positions[3] ^ positions[7] ^ positions[11] ^ positions[15];

    (g1, g2, g3, g4)
}
/// Mélange un octet avant son passage dans les rotors.
pub fn mix_before(
    mut value: u8,
    communication_key: &[u8],
    positions: &[u8; ROTOR_COUNT],
    byte_counter: u64,
    previous_ciphertext: u8,
) -> Result<u8, &'static str> {
    if communication_key.len() != COMMUNICATION_KEY_SIZE {
        return Err("Communication_key must be exactly 64 bytes");
    }

    let counter = byte_counter as u8;
    let k0 = communication_key[0];
    let k1 = communication_key[1];
    let (g1, g2, _, _) = rotor_groups(positions);

    value ^= k0;
    value = value.wrapping_add(positions[3]);

    let shift = (
        communication_key[11] ^ counter ^ positions[7]
    ) & 7;
    value = rotl8(value, shift as u32);

    value ^= previous_ciphertext;
    value = value.wrapping_sub(g1);

    let shift = (
        communication_key[27] ^ counter ^ positions[8]
    ) & 7;
    value = rotl8(value, shift as u32);

    value = value.wrapping_add(g2);
    value ^= k1;

    Ok(value)
}

/// Annule exactement mix_before().
pub fn inverse_mix_before(
    mut value: u8,
    communication_key: &[u8],
    positions: &[u8; ROTOR_COUNT],
    byte_counter: u64,
    previous_ciphertext: u8,
) -> Result<u8, &'static str> {
    if communication_key.len() != COMMUNICATION_KEY_SIZE {
        return Err("Communication_key must be exactly 64 bytes");
    }

    let counter = byte_counter as u8;
    let k0 = communication_key[0];
    let k1 = communication_key[1];
    let (g1, g2, _, _) = rotor_groups(positions);

    value ^= k1;
    value = value.wrapping_sub(g2);

    let shift = (
        communication_key[27] ^ counter ^ positions[8]
    ) & 7;
    value = rotr8(value, shift as u32);

    value = value.wrapping_add(g1);
    value ^= previous_ciphertext;

    let shift = (
        communication_key[11] ^ counter ^ positions[7]
    ) & 7;
    value = rotr8(value, shift as u32);

    value = value.wrapping_sub(positions[3]);
    value ^= k0;

    Ok(value)
}

/// Mélange un octet après son passage dans les rotors.
pub fn mix_final(
    mut value: u8,
    communication_key: &[u8],
    positions: &[u8; ROTOR_COUNT],
    byte_counter: u64,
    previous_ciphertext: u8,
    packet_type: u8,
) -> Result<u8, &'static str> {
    if communication_key.len() != COMMUNICATION_KEY_SIZE {
        return Err("Communication_key must be exactly 64 bytes");
    }

    let counter = byte_counter as u8;
    let k0 = communication_key[0];
    let k2 = communication_key[2];
    let (_, _, g3, g4) = rotor_groups(positions);

    value ^= g3;
    value = value.wrapping_add(k2);

    let shift = (
        communication_key[19]
            ^ counter
            ^ positions[7]
            ^ packet_type
    ) & 7;
    value = rotl8(value, shift as u32);

    value ^= previous_ciphertext;
    value = value.wrapping_add(communication_key[42]);

    let shift = (
        communication_key[47] ^ counter ^ positions[8]
    ) & 7;
    value = rotl8(value, shift as u32);

    value = value.wrapping_sub(g4);
    value ^= k0;

    Ok(value)
}

/// Annule exactement mix_final().
pub fn inverse_mix_final(
    mut value: u8,
    communication_key: &[u8],
    positions: &[u8; ROTOR_COUNT],
    byte_counter: u64,
    previous_ciphertext: u8,
    packet_type: u8,
) -> Result<u8, &'static str> {
    if communication_key.len() != COMMUNICATION_KEY_SIZE {
        return Err("Communication_key must be exactly 64 bytes");
    }

    let counter = byte_counter as u8;
    let k0 = communication_key[0];
    let k2 = communication_key[2];
    let (_, _, g3, g4) = rotor_groups(positions);

    value ^= k0;
    value = value.wrapping_add(g4);

    let shift = (
        communication_key[47] ^ counter ^ positions[8]
    ) & 7;
    value = rotr8(value, shift as u32);

    value = value.wrapping_sub(communication_key[42]);
    value ^= previous_ciphertext;

    let shift = (
        communication_key[19]
            ^ counter
            ^ positions[7]
            ^ packet_type
    ) & 7;
    value = rotr8(value, shift as u32);

    value = value.wrapping_sub(k2);
    value ^= g3;

    Ok(value)
}
/// Chiffre un message octet par octet.
///
/// L'ordre des opérations correspond au pipeline Python :
/// update -> mix_before -> 16 rotors -> mix_final.
pub fn encrypt(
    communication_key: &[u8],
    packet_type: u8,
    plaintext: &[u8],
) -> Result<Vec<u8>, &'static str> {
    let rotors = generate_rotors(communication_key)?;
    let mut state = RotorState::new(communication_key, packet_type)?;

    let mut ciphertext = Vec::with_capacity(plaintext.len());
    let mut previous_ciphertext = 0u8;

    for (byte_counter, &plain_byte) in plaintext.iter().enumerate() {
        state.update();

        // Copier l'état après la mise à jour, comme en Python.
        let positions = *state.positions();

        let mut value = mix_before(
            plain_byte,
            communication_key,
            &positions,
            byte_counter as u64,
            previous_ciphertext,
        )?;

        // Les rotors sont appliqués dans l'ordre R1 -> R16.
        for rotor_index in 0..ROTOR_COUNT {
            value = rotor_forward(
                value,
                positions[rotor_index],
                &rotors[rotor_index],
            );
        }

        value = mix_final(
            value,
            communication_key,
            &positions,
            byte_counter as u64,
            previous_ciphertext,
            packet_type,
        )?;

        ciphertext.push(value);

        // Toujours conserver l'octet chiffré, pas l'octet clair.
        previous_ciphertext = value;
    }

    Ok(ciphertext)
}

/// Déchiffre un message produit par encrypt().
///
/// Les opérations sont inversées dans l'ordre inverse.
pub fn decrypt(
    communication_key: &[u8],
    packet_type: u8,
    ciphertext: &[u8],
) -> Result<Vec<u8>, &'static str> {
    let rotors = generate_rotors(communication_key)?;
    let inverse_rotors: [[u8; ROTOR_SIZE]; ROTOR_COUNT] =
        std::array::from_fn(|i| inverse_permutation(&rotors[i]));

    let mut state = RotorState::new(communication_key, packet_type)?;

    let mut plaintext = Vec::with_capacity(ciphertext.len());
    let mut previous_ciphertext = 0u8;

    for (byte_counter, &cipher_byte) in ciphertext.iter().enumerate() {
        state.update();

        let positions = *state.positions();

        // Annuler le dernier mélange.
        let mut value = inverse_mix_final(
            cipher_byte,
            communication_key,
            &positions,
            byte_counter as u64,
            previous_ciphertext,
            packet_type,
        )?;

        // Inverser les rotors dans l'ordre R16 -> R1.
        for rotor_index in (0..ROTOR_COUNT).rev() {
            value = rotor_inverse(
                value,
                positions[rotor_index],
                &rotors[rotor_index],
            );
        }

        // Annuler le premier mélange.
        value = inverse_mix_before(
            value,
            communication_key,
            &positions,
            byte_counter as u64,
            previous_ciphertext,
        )?;

        plaintext.push(value);

        // L'octet chiffré d'origine est nécessaire au prochain octet.
        previous_ciphertext = cipher_byte;
    }

    Ok(plaintext)
}
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splitmix64_same_seed_same_sequence() {
        let mut rng1 = SplitMix64::new(0);
        let mut rng2 = SplitMix64::new(0);

        for _ in 0..100 {
            assert_eq!(rng1.next(), rng2.next());
        }
    }

    #[test]
    fn splitmix64_different_seed_different_sequence() {
        let mut rng1 = SplitMix64::new(0);
        let mut rng2 = SplitMix64::new(1);

        let sequence1: Vec<u64> = (0..100).map(|_| rng1.next()).collect();
        let sequence2: Vec<u64> = (0..100).map(|_| rng2.next()).collect();

        assert_ne!(sequence1, sequence2);
    }

    #[test]
    fn splitmix64_state_changes() {
        let mut rng = SplitMix64::new(0);

        let first = rng.next();
        let second = rng.next();

        assert_ne!(first, second);
    }

    #[test]
    fn splitmix64_zero_seed() {
        let mut rng = SplitMix64::new(0);

        assert_eq!(
            rng.next(),
            0xE220_A839_7B1D_CDAFu64
        );
    }

    #[test]
    fn splitmix64_max_seed() {
        let mut rng = SplitMix64::new(u64::MAX);

        let first = rng.next();
        let second = rng.next();

        assert_ne!(first, second);
    }
    #[test]
fn derive_rotor_seed_rejects_invalid_key_length() {
    let key = [0u8; 63];

    assert!(
        derive_rotor_seed(&key, 1).is_err()
    );
}

#[test]
fn derive_rotor_seed_rejects_invalid_rotor_id() {
    let key = [0u8; 64];

    assert!(
        derive_rotor_seed(&key, 0).is_err()
    );

    assert!(
        derive_rotor_seed(&key, 17).is_err()
    );
}

#[test]
fn derive_rotor_seed_is_deterministic() {
    let key = [0u8; 64];

    let seed1 = derive_rotor_seed(&key, 1).unwrap();
    let seed2 = derive_rotor_seed(&key, 1).unwrap();

    assert_eq!(seed1, seed2);
}

#[test]
fn derive_rotor_seed_differs_between_rotors() {
    let key = [0u8; 64];

    let seed1 = derive_rotor_seed(&key, 1).unwrap();
    let seed2 = derive_rotor_seed(&key, 2).unwrap();

    assert_ne!(seed1, seed2);
}
    #[test]
fn fisher_yates_contains_all_values() {
    let rotor = fisher_yates(0);

    let mut sorted = rotor;

    sorted.sort_unstable();

    let expected: [u8; ROTOR_SIZE] =
        core::array::from_fn(|i| i as u8);

    assert_eq!(sorted, expected);
}

#[test]
fn fisher_yates_is_deterministic() {
    let rotor1 = fisher_yates(123456789);
    let rotor2 = fisher_yates(123456789);

    assert_eq!(rotor1, rotor2);
}

#[test]
fn fisher_yates_changes_with_seed() {
    let rotor1 = fisher_yates(0);
    let rotor2 = fisher_yates(1);

    assert_ne!(rotor1, rotor2);
}
#[test]
fn generate_rotor_is_deterministic() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];

    let rotor1 = generate_rotor(&key, 1).unwrap();
    let rotor2 = generate_rotor(&key, 1).unwrap();

    assert_eq!(rotor1, rotor2);
}

#[test]
fn generate_rotors_creates_sixteen_rotors() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];

    let rotors = generate_rotors(&key).unwrap();

    assert_eq!(rotors.len(), ROTOR_COUNT);
}

#[test]
fn generate_rotors_are_permutations() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];

    let rotors = generate_rotors(&key).unwrap();

    for rotor in rotors {
        let mut sorted = rotor;

        sorted.sort_unstable();

        let expected: [u8; ROTOR_SIZE] =
            core::array::from_fn(|i| i as u8);

        assert_eq!(sorted, expected);
    }
}

#[test]
fn generate_rotors_are_different() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];

    let rotors = generate_rotors(&key).unwrap();

    for i in 0..ROTOR_COUNT {
        for j in (i + 1)..ROTOR_COUNT {
            assert_ne!(rotors[i], rotors[j]);
        }
    }
}
#[test]
fn rotor_forward_inverse_round_trip_all_values_and_positions() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];
    let rotor = generate_rotor(&key, 1).unwrap();

    for position in 0..=u8::MAX {
        for value in 0..=u8::MAX {
            let encrypted = rotor_forward(value, position, &rotor);
            let decrypted = rotor_inverse(encrypted, position, &rotor);

            assert_eq!(
                decrypted, value,
                "Échec pour value={value}, position={position}"
            );
        }
    }
}

#[test]
fn inverse_permutation_restores_original_values() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];
    let rotor = generate_rotor(&key, 1).unwrap();
    let inverse = inverse_permutation(&rotor);

    for value in 0..=u8::MAX {
        assert_eq!(inverse[rotor[value as usize] as usize], value);
    }
}

#[test]
fn rotor_state_starts_at_zero() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];
    let state = RotorState::new(&key, 1).unwrap();

    assert_eq!(state.positions(), &[0u8; ROTOR_COUNT]);
    assert_eq!(state.byte_counter(), 0);
}

#[test]
fn rotor_state_updates_all_positions() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];
    let mut state = RotorState::new(&key, 1).unwrap();

    state.update();

    assert_eq!(state.byte_counter(), 1);
    assert!(state.positions().iter().any(|&position| position != 0));
}

#[test]
fn rotor_state_is_deterministic() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];
    let mut state1 = RotorState::new(&key, 3).unwrap();
    let mut state2 = RotorState::new(&key, 3).unwrap();

    for _ in 0..100 {
        state1.update();
        state2.update();

        assert_eq!(state1.positions(), state2.positions());
    }
}

#[test]
fn rotor_state_supports_all_nine_packet_types() {
    let key = [0u8; COMMUNICATION_KEY_SIZE];

    for packet_type in 1..=9 {
        let mut state = RotorState::new(&key, packet_type).unwrap();

        for _ in 0..100 {
            state.update();
        }

        assert_eq!(state.byte_counter(), 100);
    }
}

#[test]
fn rotor_state_rejects_invalid_key_length() {
    let key = [0u8; 63];

    assert!(RotorState::new(&key, 1).is_err());
}

#[test]
fn rotl8_and_rotr8_are_inverses() {
    for value in 0..=u8::MAX {
        for shift in 0..8 {
            assert_eq!(
                rotr8(rotl8(value, shift), shift),
                value
            );
        }
    }
}

#[test]
fn rotor_groups_are_deterministic() {
    let positions: [u8; ROTOR_COUNT] =
        core::array::from_fn(|i| i as u8);

    assert_eq!(
        rotor_groups(&positions),
        rotor_groups(&positions)
    );
}
#[test]
fn rotor_groups_match_expected_xor_values() {
    let positions: [u8; ROTOR_COUNT] = std::array::from_fn(|i| i as u8);

    let (g1, g2, g3, g4) = rotor_groups(&positions);

    assert_eq!(g1, 0 ^ 4 ^ 8 ^ 12);
    assert_eq!(g2, 1 ^ 5 ^ 9 ^ 13);
    assert_eq!(g3, 2 ^ 6 ^ 10 ^ 14);
    assert_eq!(g4, 3 ^ 7 ^ 11 ^ 15);
}

#[test]
fn mix_before_round_trip_all_byte_values() {
    let key: [u8; 64] = std::array::from_fn(|i| i as u8);
    let positions: [u8; ROTOR_COUNT] =
        std::array::from_fn(|i| (i * 17) as u8);

    for value in 0u8..=u8::MAX {
        let mixed = mix_before(
            value, &key, &positions, 123, 0xA5,
        ).unwrap();

        let restored = inverse_mix_before(
            mixed, &key, &positions, 123, 0xA5,
        ).unwrap();

        assert_eq!(restored, value, "value={value}");
    }
}

#[test]
fn mix_final_round_trip_all_byte_values() {
    let key: [u8; 64] = std::array::from_fn(|i| i as u8);
    let positions: [u8; ROTOR_COUNT] =
        std::array::from_fn(|i| (i * 17) as u8);

    for packet_type in 1u8..=9 {
        for value in 0u8..=u8::MAX {
            let mixed = mix_final(
                value, &key, &positions, 123, 0xA5, packet_type,
            ).unwrap();

            let restored = inverse_mix_final(
                mixed, &key, &positions, 123, 0xA5, packet_type,
            ).unwrap();

            assert_eq!(
                restored, value,
                "value={value}, packet_type={packet_type}"
            );
        }
    }
}
#[test]
fn encrypt_decrypt_round_trip_all_packet_types() {
    let key: [u8; 64] = std::array::from_fn(|i| i as u8);

    let plaintext: Vec<u8> = (0..1024)
        .map(|i| (i * 37 + 11) as u8)
        .collect();

    for packet_type in 1u8..=9 {
        let ciphertext =
            encrypt(&key, packet_type, &plaintext).unwrap();

        assert_eq!(ciphertext.len(), plaintext.len());

        let decrypted =
            decrypt(&key, packet_type, &ciphertext).unwrap();

        assert_eq!(
            decrypted,
            plaintext,
            "Échec du round-trip pour packet_type={packet_type}"
        );
    }
}

#[test]
fn encrypt_empty_message() {
    let key = [0u8; 64];

    let ciphertext = encrypt(&key, 1, &[]).unwrap();
    let plaintext = decrypt(&key, 1, &ciphertext).unwrap();

    assert!(ciphertext.is_empty());
    assert!(plaintext.is_empty());
}

#[test]
fn encrypt_rejects_invalid_key_length() {
    let key = [0u8; 63];

    assert!(encrypt(&key, 1, b"test").is_err());
    assert!(decrypt(&key, 1, b"test").is_err());
}

#[test]
fn encrypt_is_deterministic_for_same_inputs() {
    let key: [u8; 64] = std::array::from_fn(|i| i as u8);
    let plaintext = b"The Last Signal";

    let first = encrypt(&key, 1, plaintext).unwrap();
    let second = encrypt(&key, 1, plaintext).unwrap();

    assert_eq!(first, second);
}
}

