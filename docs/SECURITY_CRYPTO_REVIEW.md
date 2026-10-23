# Cryptographic Design Review

**Review date:** 2026-10-23  
**Scope:** Current Python/Rust cryptographic modules, vault key handling, and the packet transport call paths.  
**Method:** Static source review of the code paths listed below. This is not a cryptanalysis, penetration test, or certification.

## Executive summary

**Do not treat the custom rotor implementation as production cryptography.** The repository contains custom byte-level permutation/mixing primitives, but the inspected runtime packet paths do not call those primitives. The active Python client sends the result of `Packet.encode()` directly, and the server packet code serializes/parses the protocol framing directly. The current transport path therefore does not gain confidentiality or integrity from these modules.

The local Fernet vault uses a standard authenticated-encryption library, but its default on-disk key handling and command-line interface need hardening.

## Findings

### CR-01 — High: Runtime packet transport is not protected by the custom crypto module

**Evidence**

- `client_python/client.py`: `Client.send_packet()` sends `packet.encode()` directly; `Client.receive_packet()` passes the body to `Packet.decode()`.
- `client_python/packet.py`: `Packet.encode()` constructs the length/type/payload frame without calling the crypto module.
- `server_rust/src/network/packet.rs`, `server_rust/src/network/client.rs`, and `server_rust/src/network/handler.rs`: the inspected packet and client handling paths do not call `security::crypto`.
- `client_python/crypto.py` and `server_rust/src/security/crypto.rs` contain byte-level transformation primitives, not a complete authenticated transport layer.

**Impact**

The custom routines do not currently protect the inspected client/server packet stream. Anyone evaluating this prototype should assume the local TCP transport has no application-layer encryption or message-authentication guarantee from these modules. This is especially important before exposing the server on an untrusted network.

**Recommendation**

If transport confidentiality and integrity are required, use a standard authenticated channel such as TLS with certificate/identity verification. Do not attempt to retrofit the current rotor routines into a production protocol.

**Confidence:** High for the inspected call paths; the finding is about the current runtime usage, not a claim that every possible module in the repository was exhaustively traced.

### CR-02 — High: The custom rotor/mixing primitives are not a substitute for a vetted authenticated cipher

**Evidence**

- `RotorState::new()` in both `client_python/crypto.py` and `server_rust/src/security/crypto.rs` initializes every rotor position and the byte counter to zero; its state depends on the communication key and packet type, with no per-message nonce/unique context parameter.
- The modules implement custom deterministic permutation, rotation, XOR, and arithmetic-mixing operations.
- The public API inspected contains no ciphertext authentication tag or MAC verification step.
- Existing tests exercise deterministic behavior and inverse/round-trip properties. Those tests do not establish resistance to known-plaintext, chosen-plaintext, replay, tampering, or key-recovery attacks.

**Impact**

Reversibility and test-vector correctness do not demonstrate cryptographic security. If these primitives are later used as a message cipher, repeated initialization with the same key and packet type may repeat internal starting state, and ciphertext tampering would not be detected by an authentication tag in this API. The risk is conditional on future integration; the inspected runtime transport currently does not call these functions.

**Recommendation**

Keep this code explicitly experimental and out of production security boundaries. If message-level encryption is ever required independently of TLS, adopt a vetted AEAD construction such as AES-GCM or ChaCha20-Poly1305 through a maintained library, with an agreed key-establishment protocol, unique nonces, replay policy, and cross-language test vectors. Do not write a custom cipher.

**Confidence:** High that the implementation is custom and lacks an authentication API; no cryptanalytic testing was performed.

### CR-03 — Medium: The default vault master-key file may be readable by other local users

**Evidence**

- `security/vault.py:create_key()` creates `security/master.key` with `open(KEY_FILE, "wb")` when no environment-provided key is present.
- The file is ignored by Git, which helps prevent accidental commits, but the code does not explicitly restrict its filesystem permissions.
- On common Unix configurations with a permissive default umask such as `022`, a newly created file can be mode `0644`.

**Impact**

On a shared machine, a local user who can read the file can decrypt the Fernet vault. Actual permissions depend on the operating system, directory permissions, and process umask, so this is a configuration-dependent risk rather than a claim about every installation.

**Recommendation**

Create the key with owner-only permissions (for example `0600` on POSIX), verify existing key-file permissions on load, keep the containing directory private, and document the separate responsibility for backing up and rotating the key.

**Confidence:** High for the missing explicit permission restriction; exposure depends on the host's effective umask and directory permissions.

### CR-04 — Medium: The vault CLI accepts secret values as command-line arguments

**Evidence**

The `security/vault.py` command-line interface requires `--value` and reads the secret directly from `argparse`.

**Impact**

Secrets passed as command-line arguments may be retained in shell history or exposed to process-inspection tools, depending on the shell and operating system.

**Recommendation**

Prefer a hidden interactive prompt (for example, `getpass`) or standard input. Avoid requiring secrets in command-line arguments and provide a migration path that does not echo or log the secret.

**Confidence:** High that the CLI accepts the secret in argv; actual exposure depends on invocation and host behavior.

## Positive controls observed

- The vault uses `cryptography.fernet.Fernet`, which provides authenticated encryption for vault contents when used with a secret key.
- The default generated communication key uses `os.urandom(64)`.
- `security/master.key` is listed in `.gitignore`.
- Rust password verification uses Argon2 through the `argon2` crate in `server_rust/src/auth/password.rs`.

These controls do not resolve the findings above; in particular, an encrypted vault still depends on protecting its key.

## Scope and limitations

- This was a source-level review, not a full dependency audit, live penetration test, side-channel review, or formal cryptographic analysis.
- No secrets or key material were copied into this report.
- The custom crypto modules were checked alongside the primary packet transport call sites; no runtime use of those primitives was found in the inspected path.
- Before a public/internet-facing release, commission a dedicated threat model and security review, and replace the experimental transport design with a standard authenticated channel rather than expanding the custom cipher.

## Suggested priority

1. Treat the current transport as unauthenticated/plaintext for threat modeling; do not expose it to untrusted networks.
2. Do not enable the rotor/mixing code as production encryption.
3. Restrict master-key file permissions and remove secrets from command-line arguments.
4. Add security tests and deployment documentation after the design has been changed to use a standard, authenticated channel.
