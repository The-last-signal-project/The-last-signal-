use the_last_signal_server::player::{PlayerState, PlayerStateError};
use uuid::Uuid;

#[test]
fn new_player_starts_at_maximum_health() {
    let id = Uuid::new_v4();
    let player = PlayerState::new(id, 100).unwrap();

    assert_eq!(player.player_id(), id);
    assert_eq!(player.hp(), 100);
    assert_eq!(player.max_hp(), 100);
    assert!(player.is_alive());
}

#[test]
fn new_rejects_zero_or_negative_maximum_health() {
    assert_eq!(
        PlayerState::new(Uuid::nil(), 0).unwrap_err(),
        PlayerStateError::InvalidMaxHealth
    );
    assert_eq!(
        PlayerState::new(Uuid::nil(), -1).unwrap_err(),
        PlayerStateError::InvalidMaxHealth
    );
}

#[test]
fn damage_reduces_health_and_never_goes_below_zero() {
    let mut player = PlayerState::new(Uuid::nil(), 100).unwrap();

    player.take_damage(30);
    assert_eq!(player.hp(), 70);

    player.take_damage(150);
    assert_eq!(player.hp(), 0);
    assert!(!player.is_alive());

    player.take_damage(1);
    assert_eq!(player.hp(), 0);
}

#[test]
fn healing_restores_health_and_never_exceeds_maximum() {
    let mut player = PlayerState::new(Uuid::nil(), 100).unwrap();

    player.take_damage(50);
    player.heal(20);
    assert_eq!(player.hp(), 70);

    player.heal(1000);
    assert_eq!(player.hp(), 100);
    assert!(player.is_alive());
}

#[test]
fn negative_damage_and_healing_are_ignored() {
    let mut player = PlayerState::new(Uuid::nil(), 100).unwrap();

    player.take_damage(-10);
    assert_eq!(player.hp(), 100);

    player.take_damage(50);
    player.heal(-20);
    assert_eq!(player.hp(), 50);
}

#[test]
fn extreme_amounts_do_not_overflow() {
    let mut player = PlayerState::new(Uuid::nil(), i32::MAX).unwrap();

    player.take_damage(i32::MAX);
    assert_eq!(player.hp(), 0);

    player.heal(i32::MAX);
    assert_eq!(player.hp(), i32::MAX);

    player.heal(i32::MAX);
    assert_eq!(player.hp(), i32::MAX);
}

#[test]
fn healing_at_maximum_does_not_overflow_before_clamping() {
    let mut player = PlayerState::new(Uuid::nil(), i32::MAX).unwrap();

    player.take_damage(1);
    assert_eq!(player.hp(), i32::MAX - 1);

    player.heal(2);
    assert_eq!(player.hp(), i32::MAX);
}
