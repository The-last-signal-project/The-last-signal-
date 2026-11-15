//! Zone du trésor : enceinte fermée, porte, clé et trésor.
//!
//! Le serveur est l'autorité :
//! - il tire la position de la clé,
//! - il décide qui la ramasse (premier joueur qui la touche),
//! - il ne laisse entrer dans l'enceinte que le porteur de la clé,
//! - il valide le ramassage du trésor.
//!
//! La géométrie doit rester identique à celle du client (`game.py`).

use rand::RngExt;
use uuid::Uuid;

use crate::network::packet::{Packet, PacketType};
use crate::world::world::Position;

// =============================================================
// CONSTANTES (identiques au client)
// =============================================================

pub const WORLD_WIDTH: i32 = 1000;
pub const WORLD_HEIGHT: i32 = 700;
pub const PLAYER_SIZE: i32 = 30;

/// Déplacement maximal accepté entre deux MOVE, par axe.
/// Le client avance de 5 px par image ; la marge absorbe la latence et
/// les MOVE déjà en vol après une correction. Doit rester < épaisseur d'un
/// mur + taille du joueur (60) pour qu'on ne puisse pas « sauter » un mur.
pub const MAX_STEP: i32 = 50;

pub const KEY_SIZE: i32 = 20;
/// La clé apparaît à plus de cette distance du joueur (en x ET en y).
pub const KEY_MIN_DISTANCE: i32 = 10;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Rect {
    pub x: i32,
    pub y: i32,
    pub w: i32,
    pub h: i32,
}

impl Rect {
    pub const fn new(x: i32, y: i32, w: i32, h: i32) -> Self {
        Self { x, y, w, h }
    }

    /// Vrai s'il existe une aire de recouvrement (les bords qui se touchent
    /// ne comptent pas, comme `QRectF.intersects` côté client).
    pub fn intersects(&self, other: &Rect) -> bool {
        self.x < other.x + other.w
            && other.x < self.x + self.w
            && self.y < other.y + other.h
            && other.y < self.y + self.h
    }

    pub fn player(position: Position) -> Self {
        Self::new(position.x, position.y, PLAYER_SIZE, PLAYER_SIZE)
    }
}

/// Emprise totale de l'enceinte (murs compris).
pub const ENCLOSURE: Rect = Rect::new(250, 150, 500, 400);

/// Porte dans le mur du haut (x 470 -> 530).
pub const DOOR: Rect = Rect::new(470, 150, 60, 30);

/// Murs de l'enceinte (le mur du haut est interrompu par la porte).
pub const WALLS: [Rect; 5] = [
    Rect::new(250, 150, 220, 30), // haut, à gauche de la porte
    Rect::new(530, 150, 220, 30), // haut, à droite de la porte
    Rect::new(250, 520, 500, 30), // bas
    Rect::new(250, 180, 30, 340), // gauche
    Rect::new(720, 180, 30, 340), // droite
];

/// Trésor : 30x30, centré sur le centre de l'enceinte (500, 350).
pub const TREASURE: Rect = Rect::new(485, 335, 30, 30);

/// Niveau du trésor (= niveau de coffre de `Tresor::ouvrir`), tiré à chaque manche.
pub const TREASURE_LEVEL_MIN: u32 = 1;
pub const TREASURE_LEVEL_MAX: u32 = 5;

// =============================================================
// ÉTAT
// =============================================================

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KeyState {
    /// Au sol, visible de tous.
    OnGround { x: i32, y: i32 },
    /// Portée par un joueur.
    Held(Uuid),
    /// Utilisée : le trésor a été pris, la manche se termine.
    Consumed,
}

#[derive(Debug, Clone)]
pub struct ZoneState {
    pub key: KeyState,
    /// Joueur qui a pris le trésor (garde le droit de sortir de l'enceinte).
    pub treasure_taker: Option<Uuid>,
    /// Niveau du trésor de la manche (1 à 5) : détermine le contenu du coffre.
    pub treasure_level: u32,
}

/// Résultat d'un déplacement validé sur la zone.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct MoveEffect {
    /// L'état de la zone a changé : à diffuser.
    pub changed: bool,
    /// Le joueur vient de prendre le trésor : niveau du coffre à ouvrir.
    pub treasure_won: Option<u32>,
}

impl ZoneState {
    pub fn new() -> Self {
        let (x, y) = random_key_position(None);

        Self {
            key: KeyState::OnGround { x, y },
            treasure_taker: None,
            treasure_level: random_treasure_level(),
        }
    }

    /// Nouvelle manche : nouvelle clé, trésor de nouveau disponible.
    pub fn reset(&mut self, avoid: Option<Position>) {
        let (x, y) = random_key_position(avoid);

        self.key = KeyState::OnGround { x, y };
        self.treasure_taker = None;
        self.treasure_level = random_treasure_level();
    }

    /// Un joueur peut franchir la porte / être dans l'enceinte
    /// s'il porte la clé, ou s'il vient de prendre le trésor (pour sortir).
    pub fn can_pass(&self, player_id: Uuid) -> bool {
        self.key == KeyState::Held(player_id) || self.treasure_taker == Some(player_id)
    }

    /// Applique les ramassages liés à une position VALIDÉE.
    pub fn apply_move(&mut self, player_id: Uuid, rect: Rect, position: Position) -> MoveEffect {
        let mut effect = MoveEffect::default();

        // Ramassage de la clé (le premier arrivé la prend)
        if let KeyState::OnGround { x, y } = self.key {
            if rect.intersects(&Rect::new(x, y, KEY_SIZE, KEY_SIZE)) {
                self.key = KeyState::Held(player_id);
                effect.changed = true;
            }
        }

        // Ramassage du trésor : uniquement avec la clé
        if self.key == KeyState::Held(player_id)
            && self.treasure_taker.is_none()
            && rect.intersects(&TREASURE)
        {
            self.treasure_taker = Some(player_id);
            self.key = KeyState::Consumed;
            effect.changed = true;
            effect.treasure_won = Some(self.treasure_level);
        }

        // Le vainqueur est ressorti : nouvelle manche
        if self.treasure_taker == Some(player_id) && !rect.intersects(&ENCLOSURE) {
            self.reset(Some(position));
            effect.changed = true;
        }

        effect
    }

    /// Un joueur quitte le monde. Retourne vrai si l'état a changé.
    pub fn on_player_left(&mut self, player_id: Uuid) -> bool {
        if self.key == KeyState::Held(player_id) || self.treasure_taker == Some(player_id) {
            self.reset(None);
            return true;
        }

        false
    }

    /// Payload ZONE_STATE (43 octets) :
    ///
    /// ```text
    ///  1 octet  : état de la clé (0 = au sol, 1 = portée, 2 = utilisée)
    ///  4 octets : x de la clé (i32), 0 si pas au sol
    ///  4 octets : y de la clé (i32), 0 si pas au sol
    /// 16 octets : UUID du porteur, nul si personne
    ///  1 octet  : trésor pris (0 = disponible, 1 = pris)
    /// 16 octets : UUID de celui qui l'a pris, nul sinon
    ///  1 octet  : niveau du trésor (1 à 5)
    /// ```
    pub fn encode(&self) -> Vec<u8> {
        let (state, x, y, holder) = match self.key {
            KeyState::OnGround { x, y } => (0u8, x, y, Uuid::nil()),
            KeyState::Held(id) => (1u8, 0, 0, id),
            KeyState::Consumed => (2u8, 0, 0, Uuid::nil()),
        };

        let mut payload = Vec::with_capacity(43);

        payload.push(state);
        payload.extend_from_slice(&x.to_be_bytes());
        payload.extend_from_slice(&y.to_be_bytes());
        payload.extend_from_slice(holder.as_bytes());
        payload.push(u8::from(self.treasure_taker.is_some()));
        payload.extend_from_slice(self.treasure_taker.unwrap_or_else(Uuid::nil).as_bytes());
        payload.push(self.treasure_level as u8);

        debug_assert_eq!(payload.len(), 43);

        payload
    }

    pub fn packet(&self) -> Packet {
        Packet::new(PacketType::ZoneState, self.encode())
    }
}

impl Default for ZoneState {
    fn default() -> Self {
        Self::new()
    }
}

// =============================================================
// VALIDATION D'UN DÉPLACEMENT
// =============================================================

/// Vrai si le joueur peut se trouver en `requested` en venant de `previous`.
pub fn move_allowed(
    zone: &ZoneState,
    player_id: Uuid,
    previous: Option<Position>,
    requested: Position,
) -> bool {
    // Limites du monde
    if requested.x < 0
        || requested.y < 0
        || requested.x > WORLD_WIDTH - PLAYER_SIZE
        || requested.y > WORLD_HEIGHT - PLAYER_SIZE
    {
        return false;
    }

    // Pas de téléportation
    if let Some(previous) = previous {
        if (requested.x - previous.x).abs() > MAX_STEP
            || (requested.y - previous.y).abs() > MAX_STEP
        {
            return false;
        }
    }

    let rect = Rect::player(requested);

    // Murs : infranchissables pour tout le monde
    if WALLS.iter().any(|wall| rect.intersects(wall)) {
        return false;
    }

    // Porte et intérieur : réservés au porteur de la clé
    if !zone.can_pass(player_id) && rect.intersects(&ENCLOSURE) {
        return false;
    }

    true
}

// =============================================================
// NIVEAU ALÉATOIRE DU TRÉSOR
// =============================================================

fn random_treasure_level() -> u32 {
    rand::rng().random_range(TREASURE_LEVEL_MIN..=TREASURE_LEVEL_MAX)
}

// =============================================================
// POSITION ALÉATOIRE DE LA CLÉ
// =============================================================

/// Position aléatoire pour la clé : hors de l'enceinte et, si `avoid` est
/// donné, à plus de `KEY_MIN_DISTANCE` de ce joueur en x ET en y.
fn random_key_position(avoid: Option<Position>) -> (i32, i32) {
    let mut rng = rand::rng();

    for _ in 0..1000 {
        let x = rng.random_range(0..=(WORLD_WIDTH - KEY_SIZE));
        let y = rng.random_range(0..=(WORLD_HEIGHT - KEY_SIZE));

        if Rect::new(x, y, KEY_SIZE, KEY_SIZE).intersects(&ENCLOSURE) {
            continue;
        }

        if let Some(player) = avoid {
            if (x - player.x).abs() <= KEY_MIN_DISTANCE
                || (y - player.y).abs() <= KEY_MIN_DISTANCE
            {
                continue;
            }
        }

        return (x, y);
    }

    // Repli (ne devrait jamais arriver) : coin bas-droit, hors enceinte.
    (WORLD_WIDTH - KEY_SIZE - 10, WORLD_HEIGHT - KEY_SIZE - 10)
}

// =============================================================
// TESTS
// =============================================================

#[cfg(test)]
mod tests {
    use super::*;

    fn pos(x: i32, y: i32) -> Position {
        Position::new(x, y, 0)
    }

    fn zone_with_key_on_ground() -> ZoneState {
        ZoneState {
            key: KeyState::OnGround { x: 10, y: 10 },
            treasure_taker: None,
            treasure_level: 3,
        }
    }

    #[test]
    fn random_key_never_in_enclosure_nor_close_to_player() {
        let player = pos(100, 100);

        for _ in 0..2000 {
            let (x, y) = random_key_position(Some(player));

            assert!(!Rect::new(x, y, KEY_SIZE, KEY_SIZE).intersects(&ENCLOSURE));
            assert!((x - player.x).abs() > KEY_MIN_DISTANCE);
            assert!((y - player.y).abs() > KEY_MIN_DISTANCE);
        }
    }

    #[test]
    fn server_spawn_area_is_outside_enclosure() {
        // Client::spawn tire x, y dans 0..100
        assert!(!Rect::player(pos(99, 99)).intersects(&ENCLOSURE));
    }

    #[test]
    fn player_without_key_cannot_enter_door_or_interior() {
        let zone = zone_with_key_on_ground();
        let id = Uuid::new_v4();

        // devant la porte, puis dans la porte
        assert!(move_allowed(&zone, id, Some(pos(490, 100)), pos(490, 120)));
        assert!(!move_allowed(&zone, id, Some(pos(490, 120)), pos(490, 140)));
        // intérieur (téléportation refusée aussi)
        assert!(!move_allowed(&zone, id, Some(pos(490, 120)), pos(490, 200)));
    }

    #[test]
    fn player_with_key_can_pass_the_door_but_not_walls() {
        let id = Uuid::new_v4();
        let zone = ZoneState {
            key: KeyState::Held(id),
            treasure_taker: None,
            treasure_level: 3,
        };

        assert!(move_allowed(&zone, id, Some(pos(490, 140)), pos(490, 150)));
        assert!(move_allowed(&zone, id, Some(pos(490, 190)), pos(490, 200)));
        // mur gauche
        assert!(!move_allowed(&zone, id, Some(pos(300, 200)), pos(260, 200)));
    }

    #[test]
    fn walls_block_everyone_and_teleport_is_refused() {
        let id = Uuid::new_v4();
        let zone = ZoneState {
            key: KeyState::Held(id),
            treasure_taker: None,
            treasure_level: 3,
        };

        assert!(!move_allowed(&zone, id, Some(pos(230, 300)), pos(251, 300)));
        assert!(!move_allowed(&zone, id, Some(pos(0, 0)), pos(300, 300)));
    }

    #[test]
    fn world_bounds_are_enforced() {
        let zone = zone_with_key_on_ground();
        let id = Uuid::new_v4();

        assert!(!move_allowed(&zone, id, Some(pos(0, 0)), pos(-5, 0)));
        assert!(!move_allowed(&zone, id, Some(pos(970, 0)), pos(975, 0)));
    }

    #[test]
    fn key_pickup_then_treasure_then_new_round() {
        let id = Uuid::new_v4();
        let mut zone = zone_with_key_on_ground();

        // ramasser la clé
        let on_key = pos(5, 5);
        assert!(zone.apply_move(id, Rect::player(on_key), on_key).changed);
        assert_eq!(zone.key, KeyState::Held(id));

        // prendre le trésor
        let on_treasure = pos(485, 335);
        let effect = zone.apply_move(id, Rect::player(on_treasure), on_treasure);
        assert!(effect.changed);
        assert_eq!(effect.treasure_won, Some(3));
        assert_eq!(zone.treasure_taker, Some(id));
        assert_eq!(zone.key, KeyState::Consumed);
        // le vainqueur peut encore circuler pour sortir
        assert!(zone.can_pass(id));

        // sortie de l'enceinte : nouvelle manche
        let outside = pos(100, 100);
        assert!(zone.apply_move(id, Rect::player(outside), outside).changed);
        assert!(matches!(zone.key, KeyState::OnGround { .. }));
        assert_eq!(zone.treasure_taker, None);
        assert!(!zone.can_pass(id));
    }

    #[test]
    fn treasure_requires_the_key() {
        let id = Uuid::new_v4();
        let mut zone = zone_with_key_on_ground();

        let on_treasure = pos(485, 335);
        let effect = zone.apply_move(id, Rect::player(on_treasure), on_treasure);
        assert!(!effect.changed);
        assert_eq!(effect.treasure_won, None);
        assert_eq!(zone.treasure_taker, None);
    }

    #[test]
    fn first_player_to_touch_the_key_gets_it() {
        let a = Uuid::new_v4();
        let b = Uuid::new_v4();
        let mut zone = zone_with_key_on_ground();

        let on_key = pos(5, 5);
        assert!(zone.apply_move(a, Rect::player(on_key), on_key).changed);
        assert!(!zone.apply_move(b, Rect::player(on_key), on_key).changed);
        assert_eq!(zone.key, KeyState::Held(a));
    }

    #[test]
    fn key_holder_leaving_resets_the_round() {
        let id = Uuid::new_v4();
        let mut zone = ZoneState {
            key: KeyState::Held(id),
            treasure_taker: None,
            treasure_level: 3,
        };

        assert!(zone.on_player_left(id));
        assert!(matches!(zone.key, KeyState::OnGround { .. }));
        assert!(!zone.on_player_left(Uuid::new_v4()));
    }

    #[test]
    fn encoded_state_is_43_bytes() {
        assert_eq!(ZoneState::new().encode().len(), 43);
    }

    #[test]
    fn treasure_level_is_always_between_1_and_5() {
        let mut seen = [false; 6];

        for _ in 0..2000 {
            let level = ZoneState::new().treasure_level;
            assert!((TREASURE_LEVEL_MIN..=TREASURE_LEVEL_MAX).contains(&level));
            seen[level as usize] = true;
        }

        // sur 2000 tirages, les 5 niveaux sortent (proba d'échec ~ 1e-193)
        assert!(seen[1..=5].iter().all(|&v| v));
    }

    #[test]
    fn encoded_level_is_the_last_byte() {
        let zone = ZoneState {
            key: KeyState::Consumed,
            treasure_taker: None,
            treasure_level: 4,
        };

        assert_eq!(*zone.encode().last().unwrap(), 4);
    }

    #[test]
    fn new_round_draws_a_new_valid_level() {
        let mut zone = zone_with_key_on_ground();

        for _ in 0..200 {
            zone.reset(None);
            assert!((TREASURE_LEVEL_MIN..=TREASURE_LEVEL_MAX).contains(&zone.treasure_level));
        }
    }
}
