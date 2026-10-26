use uuid::Uuid;

/// The current and maximum health of a player.
///
/// Health is always constrained to the inclusive range 0..=max_hp. Damage and healing
/// amounts below zero are ignored so callers cannot use a negative amount to reverse an action.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlayerState {
    player_id: Uuid,
    hp: i32,
    max_hp: i32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PlayerStateError {
    InvalidMaxHealth,
}

impl std::fmt::Display for PlayerStateError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidMaxHealth => write!(f, "max_hp must be greater than zero"),
        }
    }
}

impl std::error::Error for PlayerStateError {}

impl PlayerState {
    /// Creates a player at full health.
    ///
    /// max_hp must be strictly positive.
    pub fn new(player_id: Uuid, max_hp: i32) -> Result<Self, PlayerStateError> {
        if max_hp <= 0 {
            return Err(PlayerStateError::InvalidMaxHealth);
        }

        Ok(Self {
            player_id,
            hp: max_hp,
            max_hp,
        })
    }

    pub fn player_id(&self) -> Uuid {
        self.player_id
    }

    pub fn hp(&self) -> i32 {
        self.hp
    }

    pub fn max_hp(&self) -> i32 {
        self.max_hp
    }

    /// Applies non-negative damage, saturating at zero.
    /// Negative amounts are ignored.
    pub fn take_damage(&mut self, amount: i32) {
        self.hp = self.hp.saturating_sub(amount.max(0)).max(0);
    }

    /// Restores non-negative health, saturating at max_hp.
    /// Negative amounts are ignored.
    pub fn heal(&mut self, amount: i32) {
        self.hp = self.hp.saturating_add(amount.max(0)).min(self.max_hp);
    }

    pub fn is_alive(&self) -> bool {
        self.hp > 0
    }
}
