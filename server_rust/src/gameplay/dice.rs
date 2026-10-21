use rand::RngExt;

pub fn jet_de_des(face: u32, nb: u32) -> u32 {
    let mut rng = rand::rng();

    (0..nb)
        .map(|_| rng.random_range(1..=face))
        .sum()
}
