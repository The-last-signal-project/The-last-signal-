# Versioning — The Last Signal

## 1. Purpose

This document defines the versioning convention used by **The Last Signal**.

The project uses a custom versioning system with the following format:

`MAJOR.MINOR.PATCH`

This convention is used to track the project's evolution. A version number does not guarantee that the game is stable, complete, or publicly available.

## 2. Version Components

### MAJOR

Increased when a new major development cycle begins.

Example:

- `1.1.0` → `2.0.0`

### MINOR

Increased when a significant development milestone or a substantial set of new features is introduced.

The PATCH number resets to zero.

Example:

- `1.0.16` → `1.1.0`

### PATCH

Increased for minor improvements and bug fixes.

Example:

- `1.0.15` → `1.0.16`

## 3. Examples

| Version | Meaning |
|---|---|
| `1.0.0` | Project beginning |
| `1.0.1` | First evolution |
| `1.0.15` | Current development version |
| `1.1.0` | New major development milestone |
| `2.0.0` | New major development cycle |

## 4. Stability and Releases

The version number does not necessarily reflect the project's stability.

A `1.x.x` version may still be experimental, incomplete, or under active development.

Creating a new version does not automatically mean that a GitHub Release must be published.

## 5. Custom Convention

This convention is inspired by Semantic Versioning (SemVer), but its rules are adapted to the needs of The Last Signal.

The rules defined in this document take precedence for the project's internal version numbering.
