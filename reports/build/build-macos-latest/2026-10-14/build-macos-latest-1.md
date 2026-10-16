# Build Report

Run : 2431
OS : macos-latest
Branch : main
Commit : d9d88af77321b7e3de2e689935583f67033c6a33
Date : Wed Oct 14 04:08:45 UTC 2026


## Python
Listing 'client_python'...
Compiling 'client_python/__init__.py'...
Compiling 'client_python/client.py'...
Compiling 'client_python/crypto.py'...
Compiling 'client_python/game.py'...
Compiling 'client_python/logs.py'...
Compiling 'client_python/main.py'...
Compiling 'client_python/packet.py'...
Listing 'client_python/packets'...
Compiling 'client_python/packets/Deco.py'...
Compiling 'client_python/packets/__init__.py'...
Compiling 'client_python/packets/ban.py'...
Compiling 'client_python/packets/chat.py'...
Compiling 'client_python/packets/log.py'...
Compiling 'client_python/packets/login.py'...
Compiling 'client_python/packets/move.py'...
Compiling 'client_python/packets/ping.py'...
Compiling 'client_python/packets/player_remove.py'...
Compiling 'client_python/packets/player_state.py'...
Compiling 'client_python/packets/session.py'...
Compiling 'client_python/packets/singup.py'...
Listing 'tests'...
Compiling 'tests/__init__.py'...
Listing 'tests/security'...
Compiling 'tests/security/test_fuzzing.py'...
Compiling 'tests/security/test_load.py'...
Compiling 'tests/security/test_sql_injection.py'...
Compiling 'tests/test_client_class.py'...
Compiling 'tests/test_crypto_mix.py'...
Compiling 'tests/test_crypto_pipeline.py'...
Compiling 'tests/test_crypto_rotor.py'...
Compiling 'tests/test_fisher_yates.py'...
Compiling 'tests/test_packet.py'...
Compiling 'tests/test_rotor_integration.py'...
Compiling 'tests/test_rotor_seeds.py'...
Compiling 'tests/test_rotor_state.py'...
Compiling 'tests/test_rotor_vectors.py'...
Compiling 'tests/test_sessionpacket.py'...
Compiling 'tests/test_splitmix64.py'...

## Rust
[1m[92m    Updating[0m crates.io index
[1m[92m Downloading[0m crates ...
[1m[92m  Downloaded[0m block-buffer v0.12.1
[1m[92m  Downloaded[0m cpufeatures v0.3.1
[1m[92m  Downloaded[0m crypto-common v0.1.6
[1m[92m  Downloaded[0m hashlink v0.11.1
[1m[92m  Downloaded[0m itoa v1.0.18
[1m[92m  Downloaded[0m litemap v0.8.3
[1m[92m  Downloaded[0m openssl-macros v0.1.1
[1m[92m  Downloaded[0m parking_lot v0.12.5
[1m[92m  Downloaded[0m percent-encoding v2.3.2
[1m[92m  Downloaded[0m autocfg v1.5.1
[1m[92m  Downloaded[0m bitflags v2.13.2
[1m[92m  Downloaded[0m byteorder v1.5.0
[1m[92m  Downloaded[0m bytes v1.12.1
[1m[92m  Downloaded[0m chacha20 v0.10.2
[1m[92m  Downloaded[0m const-oid v0.10.2
[1m[92m  Downloaded[0m crc32fast v1.5.2
[1m[92m  Downloaded[0m digest v0.10.7
[1m[92m  Downloaded[0m displaydoc v0.2.7
[1m[92m  Downloaded[0m fernet v0.2.2
[1m[92m  Downloaded[0m foreign-types v0.3.2
[1m[92m  Downloaded[0m futures-channel v0.3.34
[1m[92m  Downloaded[0m futures-sink v0.3.34
[1m[92m  Downloaded[0m allocator-api2 v0.2.21
[1m[92m  Downloaded[0m crypto-common v0.2.2
[1m[92m  Downloaded[0m ctutils v0.4.3
[1m[92m  Downloaded[0m either v1.19.0
[1m[92m  Downloaded[0m generic-array v0.14.9
[1m[92m  Downloaded[0m getrandom v0.4.3
[1m[92m  Downloaded[0m md-5 v0.11.0
[1m[92m  Downloaded[0m once_cell v1.21.4
[1m[92m  Downloaded[0m regex v1.13.1
[1m[92m  Downloaded[0m iana-time-zone v0.1.65
[1m[92m  Downloaded[0m digest v0.11.3
[1m[92m  Downloaded[0m dotenvy v0.15.7
[1m[92m  Downloaded[0m form_urlencoded v1.2.2
[1m[92m  Downloaded[0m futures-intrusive v0.5.0
[1m[92m  Downloaded[0m icu_properties v2.3.0
[1m[92m  Downloaded[0m mio v1.2.4
[1m[92m  Downloaded[0m cc v1.8.0
[1m[92m  Downloaded[0m block-buffer v0.10.4
[1m[92m  Downloaded[0m idna_adapter v1.2.2
[1m[92m  Downloaded[0m openssl-sys v0.9.117
[1m[92m  Downloaded[0m potential_utf v0.1.6
[1m[92m  Downloaded[0m tinyvec v1.13.3
[1m[92m  Downloaded[0m cmov v0.5.4
[1m[92m  Downloaded[0m event-listener v5.4.2
[1m[92m  Downloaded[0m flexi_logger v0.31.10
[1m[92m  Downloaded[0m foreign-types-shared v0.1.1
[1m[92m  Downloaded[0m futures-core v0.3.34
[1m[92m  Downloaded[0m hex v0.4.3
[1m[92m  Downloaded[0m hkdf v0.13.0
[1m[92m  Downloaded[0m icu_collections v2.3.0
[1m[92m  Downloaded[0m icu_normalizer v2.3.0
[1m[92m  Downloaded[0m idna v1.1.0
[1m[92m  Downloaded[0m lock_api v0.4.14
[1m[92m  Downloaded[0m pin-project-lite v0.2.17
[1m[92m  Downloaded[0m proc-macro2 v1.0.107
[1m[92m  Downloaded[0m serde_core v1.0.229
[1m[92m  Downloaded[0m tracing-core v0.1.36
[1m[92m  Downloaded[0m writeable v0.6.4
[1m[92m  Downloaded[0m atoi v2.0.0
[1m[92m  Downloaded[0m crc-catalog v2.5.0
[1m[92m  Downloaded[0m equivalent v1.0.3
[1m[92m  Downloaded[0m find-msvc-tools v0.1.14
[1m[92m  Downloaded[0m foldhash v0.2.0
[1m[92m  Downloaded[0m futures-io v0.3.34
[1m[92m  Downloaded[0m futures-util v0.3.34
[1m[92m  Downloaded[0m hashbrown v0.17.1
[1m[92m  Downloaded[0m heck v0.5.0
[1m[92m  Downloaded[0m icu_locale_core v2.3.0
[1m[92m  Downloaded[0m icu_normalizer_data v2.3.0
[1m[92m  Downloaded[0m parking_lot_core v0.9.12
[1m[92m  Downloaded[0m password-hash v0.6.1
[1m[92m  Downloaded[0m sqlx-macros v0.9.0
[1m[92m  Downloaded[0m stable_deref_trait v1.2.1
[1m[92m  Downloaded[0m thiserror v2.0.21
[1m[92m  Downloaded[0m url v2.5.8
[1m[92m  Downloaded[0m zeroize_derive v1.5.0
[1m[92m  Downloaded[0m aho-corasick v1.1.5
[1m[92m  Downloaded[0m base64 v0.22.1
[1m[92m  Downloaded[0m crossbeam-queue v0.3.14
[1m[92m  Downloaded[0m icu_properties_data v2.3.0
[1m[92m  Downloaded[0m argon2 v0.6.0
[1m[92m  Downloaded[0m crc v3.4.0
[1m[92m  Downloaded[0m crossbeam-utils v0.8.23
[1m[92m  Downloaded[0m futures-task v0.3.34
[1m[92m  Downloaded[0m hybrid-array v0.4.15
[1m[92m  Downloaded[0m miniz_oxide v0.9.1
[1m[92m  Downloaded[0m nu-ansi-term v0.50.3
[1m[92m  Downloaded[0m parking v2.2.1
[1m[92m  Downloaded[0m phc v0.6.1
[1m[92m  Downloaded[0m sha1 v0.11.0
[1m[92m  Downloaded[0m thiserror-impl v2.0.21
[1m[92m  Downloaded[0m tokio-stream v0.1.19
[1m[92m  Downloaded[0m version_check v0.9.5
[1m[92m  Downloaded[0m zerovec-derive v0.11.6
[1m[92m  Downloaded[0m base64ct v1.8.3
[1m[92m  Downloaded[0m blake2 v0.11.0
[1m[92m  Downloaded[0m icu_provider v2.3.1
[1m[92m  Downloaded[0m log v0.4.34
[1m[92m  Downloaded[0m memchr v2.8.3
[1m[92m  Downloaded[0m cfg-if v1.0.5
[1m[92m  Downloaded[0m cpufeatures v0.2.17
[1m[92m  Downloaded[0m futures-executor v0.3.34
[1m[92m  Downloaded[0m getrandom v0.2.17
[1m[92m  Downloaded[0m indexmap v2.14.2
[1m[92m  Downloaded[0m adler2 v2.0.1
[1m[92m  Downloaded[0m core-foundation-sys v0.8.7
[1m[92m  Downloaded[0m flume v0.12.0
[1m[92m  Downloaded[0m hmac v0.13.0
[1m[92m  Downloaded[0m num-traits v0.2.19
[1m[92m  Downloaded[0m yoke-derive v0.8.4
[1m[92m  Downloaded[0m rand_core v0.10.1
[1m[92m  Downloaded[0m spin v0.9.9
[1m[92m  Downloaded[0m unicode-ident v1.0.27
[1m[92m  Downloaded[0m hashbrown v0.16.1
[1m[92m  Downloaded[0m flate2 v1.1.10
[1m[92m  Downloaded[0m openssl v0.10.81
[1m[92m  Downloaded[0m chrono v0.4.45
[1m[92m  Downloaded[0m tokio-macros v2.7.2
[1m[92m  Downloaded[0m zerofrom v0.1.8
[1m[92m  Downloaded[0m simd-adler32 v0.3.10
[1m[92m  Downloaded[0m slab v0.4.12
[1m[92m  Downloaded[0m libc v0.2.190
[1m[92m  Downloaded[0m serde_json v1.0.154
[1m[92m  Downloaded[0m synstructure v0.14.0
[1m[92m  Downloaded[0m tinystr v0.8.4
[1m[92m  Downloaded[0m tracing-attributes v0.1.31
[1m[92m  Downloaded[0m scopeguard v1.2.0
[1m[92m  Downloaded[0m stringprep v0.1.5
[1m[92m  Downloaded[0m zerofrom-derive v0.1.8
[1m[92m  Downloaded[0m utf8_iter v1.0.4
[1m[92m  Downloaded[0m quote v1.0.47
[1m[92m  Downloaded[0m shlex v2.0.1
[1m[92m  Downloaded[0m whoami v2.1.3
[1m[92m  Downloaded[0m sha2 v0.10.9
[1m[92m  Downloaded[0m zeroize v1.9.1
[1m[92m  Downloaded[0m zmij v1.0.23
[1m[92m  Downloaded[0m sha2 v0.11.1
[1m[92m  Downloaded[0m sqlx-macros-core v0.9.0
[1m[92m  Downloaded[0m unicode-properties v0.1.4
[1m[92m  Downloaded[0m yoke v0.8.3
[1m[92m  Downloaded[0m pkg-config v0.3.34
[1m[92m  Downloaded[0m socket2 v0.6.5
[1m[92m  Downloaded[0m sqlx-sqlite v0.9.0
[1m[92m  Downloaded[0m unicode-bidi v0.3.18
[1m[92m  Downloaded[0m smallvec v1.16.3
[1m[92m  Downloaded[0m serde_derive v1.0.229
[1m[92m  Downloaded[0m uuid v1.28.0
[1m[92m  Downloaded[0m sqlx-mysql v0.9.0
[1m[92m  Downloaded[0m zerotrie v0.2.5
[1m[92m  Downloaded[0m sqlx-postgres v0.9.0
[1m[92m  Downloaded[0m rand v0.10.3
[1m[92m  Downloaded[0m libsqlite3-sys v0.37.0
[1m[92m  Downloaded[0m serde v1.0.229
[1m[92m  Downloaded[0m typenum v1.20.1
[1m[92m  Downloaded[0m zerovec v0.11.8
[1m[92m  Downloaded[0m unicode-normalization v0.1.25
[1m[92m  Downloaded[0m sqlx-core v0.9.0
[1m[92m  Downloaded[0m zlib-rs v0.6.8
[1m[92m  Downloaded[0m vcpkg v0.2.15
[1m[92m  Downloaded[0m sqlx v0.9.0
[1m[92m  Downloaded[0m syn v2.0.119
[1m[92m  Downloaded[0m syn v3.0.9
[1m[92m  Downloaded[0m tracing v0.1.44
[1m[92m  Downloaded[0m regex-syntax v0.8.11
[1m[92m  Downloaded[0m regex-automata v0.4.18
[1m[92m  Downloaded[0m tokio v1.53.3
[1m[92m   Compiling[0m proc-macro2 v1.0.107
[1m[92m   Compiling[0m quote v1.0.47
[1m[92m   Compiling[0m unicode-ident v1.0.27
[1m[92m   Compiling[0m libc v0.2.190
[1m[92m   Compiling[0m version_check v0.9.5
[1m[92m   Compiling[0m cfg-if v1.0.5
[1m[92m   Compiling[0m generic-array v0.14.9
[1m[92m   Compiling[0m syn v3.0.9
[1m[92m   Compiling[0m icu_normalizer_data v2.3.0
[1m[92m   Compiling[0m icu_properties_data v2.3.0
[1m[92m   Compiling[0m find-msvc-tools v0.1.14
[1m[92m   Compiling[0m stable_deref_trait v1.2.1
[1m[92m   Compiling[0m shlex v2.0.1
[1m[92m   Compiling[0m vcpkg v0.2.15
[1m[92m   Compiling[0m cc v1.8.0
[1m[92m   Compiling[0m serde_core v1.0.229
[1m[92m   Compiling[0m pkg-config v0.3.34
[1m[92m   Compiling[0m syn v2.0.119
[1m[92m   Compiling[0m typenum v1.20.1
[1m[92m   Compiling[0m parking_lot_core v0.9.12
[1m[92m   Compiling[0m synstructure v0.14.0
[1m[92m   Compiling[0m autocfg v1.5.1
[1m[92m   Compiling[0m zerofrom-derive v0.1.8
[1m[92m   Compiling[0m yoke-derive v0.8.4
[1m[92m   Compiling[0m zerovec-derive v0.11.6
[1m[92m   Compiling[0m displaydoc v0.2.7
[1m[92m   Compiling[0m zerofrom v0.1.8
[1m[92m   Compiling[0m yoke v0.8.3
[1m[92m   Compiling[0m num-traits v0.2.19
[1m[92m   Compiling[0m crossbeam-utils v0.8.23
[1m[92m   Compiling[0m serde v1.0.229
[1m[92m   Compiling[0m zerovec v0.11.8
[1m[92m   Compiling[0m zmij v1.0.23
[1m[92m   Compiling[0m writeable v0.6.4
[1m[92m   Compiling[0m litemap v0.8.3
[1m[92m   Compiling[0m tinystr v0.8.4
[1m[92m   Compiling[0m smallvec v1.16.3
[1m[92m   Compiling[0m icu_locale_core v2.3.0
[1m[92m   Compiling[0m potential_utf v0.1.6
[1m[92m   Compiling[0m zerotrie v0.2.5
[1m[92m   Compiling[0m serde_derive v1.0.229
[1m[92m   Compiling[0m serde_json v1.0.154
[1m[92m   Compiling[0m futures-core v0.3.34
[1m[92m   Compiling[0m pin-project-lite v0.2.17
[1m[92m   Compiling[0m utf8_iter v1.0.4
[1m[92m   Compiling[0m icu_collections v2.3.0
[1m[92m   Compiling[0m icu_provider v2.3.1
[1m[92m   Compiling[0m thiserror-impl v2.0.21
[1m[92m   Compiling[0m scopeguard v1.2.0
[1m[92m   Compiling[0m getrandom v0.4.3
[1m[92m   Compiling[0m memchr v2.8.3
[1m[92m   Compiling[0m rand_core v0.10.1
[1m[92m   Compiling[0m lock_api v0.4.14
[1m[92m   Compiling[0m tracing-attributes v0.1.31
[1m[92m   Compiling[0m futures-sink v0.3.34
[1m[92m   Compiling[0m icu_properties v2.3.0
[1m[92m   Compiling[0m icu_normalizer v2.3.0
[1m[92m   Compiling[0m equivalent v1.0.3
[1m[92m   Compiling[0m idna_adapter v1.2.2
[1m[92m   Compiling[0m crypto-common v0.1.6
[1m[92m   Compiling[0m block-buffer v0.10.4
[1m[92m   Compiling[0m mio v1.2.4
[1m[92m   Compiling[0m socket2 v0.6.5
[1m[92m   Compiling[0m percent-encoding v2.3.2
[1m[92m   Compiling[0m foldhash v0.2.0
[1m[92m   Compiling[0m allocator-api2 v0.2.21
[1m[92m   Compiling[0m once_cell v1.21.4
[1m[92m   Compiling[0m bytes v1.12.1
[1m[92m   Compiling[0m slab v0.4.12
[1m[92m   Compiling[0m futures-task v0.3.34
[1m[92m   Compiling[0m futures-io v0.3.34
[1m[92m   Compiling[0m thiserror v2.0.21
[1m[92m   Compiling[0m cmov v0.5.4
[1m[92m   Compiling[0m tokio v1.53.3
[1m[92m   Compiling[0m ctutils v0.4.3
[1m[92m   Compiling[0m futures-util v0.3.34
[1m[92m   Compiling[0m hashbrown v0.16.1
[1m[92m   Compiling[0m tracing-core v0.1.36
[1m[92m   Compiling[0m form_urlencoded v1.2.2
[1m[92m   Compiling[0m digest v0.10.7
[1m[92m   Compiling[0m parking_lot v0.12.5
[1m[92m   Compiling[0m idna v1.1.0
[1m[92m   Compiling[0m cpufeatures v0.2.17
[1m[92m   Compiling[0m hybrid-array v0.4.15
[1m[92m   Compiling[0m libsqlite3-sys v0.37.0
[1m[92m   Compiling[0m parking v2.2.1
[1m[92m   Compiling[0m crc-catalog v2.5.0
[1m[92m   Compiling[0m itoa v1.0.18
[1m[92m   Compiling[0m log v0.4.34
[1m[92m   Compiling[0m hashbrown v0.17.1
[1m[92m   Compiling[0m tracing v0.1.44
[1m[92m   Compiling[0m crc v3.4.0
[1m[92m   Compiling[0m indexmap v2.14.2
[1m[92m   Compiling[0m event-listener v5.4.2
[1m[92m   Compiling[0m sha2 v0.10.9
[1m[92m   Compiling[0m url v2.5.8
[1m[92m   Compiling[0m futures-intrusive v0.5.0
[1m[92m   Compiling[0m tokio-stream v0.1.19
[1m[92m   Compiling[0m crossbeam-queue v0.3.14
[1m[92m   Compiling[0m either v1.19.0
[1m[92m   Compiling[0m hashlink v0.11.1
[1m[92m   Compiling[0m spin v0.9.9
[1m[92m   Compiling[0m tokio-macros v2.7.2
[1m[92m   Compiling[0m openssl-sys v0.9.117
[1m[92m   Compiling[0m uuid v1.28.0
[1m[92m   Compiling[0m base64 v0.22.1
[1m[92m   Compiling[0m sqlx-core v0.9.0
[1m[92m   Compiling[0m flume v0.12.0
[1m[92m   Compiling[0m atoi v2.0.0
[1m[92m   Compiling[0m crypto-common v0.2.2
[1m[92m   Compiling[0m block-buffer v0.12.1
[1m[92m   Compiling[0m futures-executor v0.3.34
[1m[92m   Compiling[0m futures-channel v0.3.34
[1m[92m   Compiling[0m const-oid v0.10.2
[1m[92m   Compiling[0m digest v0.11.3
[1m[92m   Compiling[0m sqlx-sqlite v0.9.0
[1m[92m   Compiling[0m aho-corasick v1.1.5
[1m[92m   Compiling[0m regex-syntax v0.8.11
[1m[92m   Compiling[0m heck v0.5.0
[1m[92m   Compiling[0m crc32fast v1.5.2
[1m[92m   Compiling[0m core-foundation-sys v0.8.7
[1m[92m   Compiling[0m base64ct v1.8.3
[1m[92m   Compiling[0m foreign-types-shared v0.1.1
[1m[92m   Compiling[0m hex v0.4.3
[1m[92m   Compiling[0m dotenvy v0.15.7
[1m[92m   Compiling[0m openssl v0.10.81
[1m[92m   Compiling[0m sqlx-macros-core v0.9.0
[1m[92m   Compiling[0m foreign-types v0.3.2
[1m[92m   Compiling[0m phc v0.6.1
[1m[92m   Compiling[0m iana-time-zone v0.1.65
[1m[92m   Compiling[0m regex-automata v0.4.18
[1m[92m   Compiling[0m zeroize_derive v1.5.0
[1m[92m   Compiling[0m openssl-macros v0.1.1
[1m[92m   Compiling[0m simd-adler32 v0.3.10
[1m[92m   Compiling[0m adler2 v2.0.1
[1m[92m   Compiling[0m bitflags v2.13.2
[1m[92m   Compiling[0m miniz_oxide v0.9.1
[1m[92m   Compiling[0m zeroize v1.9.1
[1m[92m   Compiling[0m regex v1.13.1
[1m[92m   Compiling[0m chrono v0.4.45
[1m[92m   Compiling[0m password-hash v0.6.1
[1m[92m   Compiling[0m sqlx-macros v0.9.0
[1m[92m   Compiling[0m blake2 v0.11.0
[1m[92m   Compiling[0m chacha20 v0.10.2
[1m[92m   Compiling[0m getrandom v0.2.17
[1m[92m   Compiling[0m cpufeatures v0.3.1
[1m[92m   Compiling[0m byteorder v1.5.0
[1m[92m   Compiling[0m nu-ansi-term v0.50.3
[1m[92m   Compiling[0m fernet v0.2.2
[1m[92m   Compiling[0m flexi_logger v0.31.10
[1m[92m   Compiling[0m sha2 v0.11.1
[1m[92m   Compiling[0m rand v0.10.3
[1m[92m   Compiling[0m argon2 v0.6.0
[1m[92m   Compiling[0m sqlx v0.9.0
[1m[92m   Compiling[0m flate2 v1.1.10
[1m[92m   Compiling[0m the-last-signal-server v1.0.14 (/Users/runner/work/The-last-signal-/The-last-signal-/server_rust)
[1m[33mwarning[0m[1m: unused imports: `debug` and `info`[0m
 [1m[94m--> [0msrc/gameplay/tresor.rs:5:11
  [1m[94m|[0m
[1m[94m5[0m [1m[94m|[0m use log::{debug, error, info};
  [1m[94m|[0m           [1m[33m^^^^^[0m         [1m[33m^^^^[0m
  [1m[94m|[0m
  [1m[94m= [0m[1mnote[0m: `#[warn(unused_imports)]` (part of `#[warn(unused)]`) on by default

[1m[33mwarning[0m[1m: fields `user_id` and `password_hash` are never read[0m
  [1m[94m--> [0msrc/network/handler.rs:41:5
   [1m[94m|[0m
[1m[94m40[0m [1m[94m|[0m pub struct User {
   [1m[94m|[0m            [1m[94m----[0m [1m[94mfields in this struct[0m
[1m[94m41[0m [1m[94m|[0m     user_id: String,
   [1m[94m|[0m     [1m[33m^^^^^^^[0m
[1m[94m42[0m [1m[94m|[0m     password_hash: String,
   [1m[94m|[0m     [1m[33m^^^^^^^^^^^^^[0m
   [1m[94m|[0m
   [1m[94m= [0m[1mnote[0m: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

[1m[33mwarning[0m[1m: constant `PP` is never used[0m
 [1m[94m--> [0msrc/gameplay/tresor.rs:9:7
  [1m[94m|[0m
[1m[94m9[0m [1m[94m|[0m const PP: u32 = PO * 10;
  [1m[94m|[0m       [1m[33m^^[0m

[1m[33mwarning[0m: `the-last-signal-server` (lib) generated 3 warnings (run `cargo fix --lib -p the-last-signal-server` to apply 1 suggestion)
[1m[33mwarning[0m[1m: unused import: `sqlx::Row`[0m
 [1m[94m--> [0msrc/main.rs:6:5
  [1m[94m|[0m
[1m[94m6[0m [1m[94m|[0m use sqlx::Row;
  [1m[94m|[0m     [1m[33m^^^^^^^^^[0m
  [1m[94m|[0m
  [1m[94m= [0m[1mnote[0m: `#[warn(unused_imports)]` (part of `#[warn(unused)]`) on by default

[1m[33mwarning[0m[1m: unused imports: `stuff_manager::Inventaire` and `tresor::Tresor`[0m
  [1m[94m--> [0msrc/main.rs:10:5
   [1m[94m|[0m
[1m[94m10[0m [1m[94m|[0m     stuff_manager::Inventaire,
   [1m[94m|[0m     [1m[33m^^^^^^^^^^^^^^^^^^^^^^^^^[0m
[1m[94m11[0m [1m[94m|[0m     tresor::Tresor,
   [1m[94m|[0m     [1m[33m^^^^^^^^^^^^^^[0m

[1m[33mwarning[0m[1m: constant `NOMBRE_REPETITIONS` is never used[0m
  [1m[94m--> [0msrc/main.rs:16:7
   [1m[94m|[0m
[1m[94m16[0m [1m[94m|[0m const NOMBRE_REPETITIONS: u32 = 100;
   [1m[94m|[0m       [1m[33m^^^^^^^^^^^^^^^^^^[0m
   [1m[94m|[0m
   [1m[94m= [0m[1mnote[0m: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

[1m[33mwarning[0m[1m: constant `NOMBRE_CONFIGURATIONS` is never used[0m
  [1m[94m--> [0msrc/main.rs:17:7
   [1m[94m|[0m
[1m[94m17[0m [1m[94m|[0m const NOMBRE_CONFIGURATIONS: u32 = 12 * 2 * 2; // niveaux × admin × militaire
   [1m[94m|[0m       [1m[33m^^^^^^^^^^^^^^^^^^^^^[0m

[1m[33mwarning[0m: `the-last-signal-server` (bin "the-last-signal-server") generated 4 warnings (run `cargo fix --bin "the-last-signal-server" -p the-last-signal-server` to apply 2 suggestions)
[1m[92m    Finished[0m `release` profile [optimized] target(s) in 1m 51s

## Godot
No Godot project found.

## Summary

- Python build completed
- Rust build completed
- Godot build completed
