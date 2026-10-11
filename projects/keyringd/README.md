# Keyringd

**A GNOME-free Secret Service daemon for Linux, built in Rust.**

> **Status: Planning and design.** Keyringd is not yet implemented or suitable for storing real credentials. The project name is provisional, and the architecture and dependency choices below are proposals pending a feasibility review.

## Overview

Keyringd aims to provide secure, local credential storage for Linux desktops without requiring GNOME libraries or services. It will implement the [freedesktop.org Secret Service API](https://specifications.freedesktop.org/secret-service/latest/) so existing applications can store and retrieve secrets through the familiar `org.freedesktop.secrets` D-Bus service.

The initial target is a minimal, headless-first daemon for **Arch Linux, Omarchy, Wayland sessions, and systemd user environments**. Other Linux distributions may be supported later.

This is a replacement for **GNOME Keyring's Secret Service functionality**, not an attempt to clone every historical GNOME Keyring feature. Compatibility with existing clients matters more than compatibility with GNOME internals.

## Why this project?

Credential storage is foundational desktop infrastructure. A replacement should be able to run in a non-GNOME environment without pulling in GLib, GObject, GIO, GCR, GCK, GTK, or other GNOME runtime and build dependencies.

Keyringd is guided by five principles:

1. **Standards over frameworks.** Implement the Secret Service protocol rather than GNOME-specific APIs.
2. **Small security boundary.** Keep the daemon, cryptography, and persistence narrow and auditable.
3. **Compatibility first.** Work with existing Secret Service clients, including applications that use `libsecret`, without linking against `libsecret` ourselves.
4. **Headless by default.** Separate credential storage from prompting, UI, and session integration.
5. **Verify before building.** Evaluate existing Rust implementations—especially [`oo7-daemon`](https://github.com/linux-credentials/oo7)—before deciding to build from scratch or fork.

## Project scope

### Planned core features

- Own the session D-Bus name `org.freedesktop.secrets`.
- Implement the Secret Service `Service`, `Collection`, `Item`, `Session`, and `Prompt` interfaces.
- Create, find, update, and delete secrets and collections.
- Support collection aliases, search attributes, D-Bus properties, signals, and locking semantics.
- Support the session-negotiation methods required for practical client interoperability.
- Encrypt secrets at rest using established, authenticated cryptography.
- Support vault initialization, unlocking, locking, and clean restart/recovery behavior.
- Integrate with D-Bus activation and systemd user services.
- Offer a CLI and an optional external prompt frontend without introducing GUI dependencies into the daemon.

### Intentionally outside the initial scope

- SSH-agent replacement; use OpenSSH's `ssh-agent`.
- PKCS#11 provider or certificate-management application.
- Secret synchronization or cloud accounts.
- A GTK, Qt, or other graphical management application.
- Hardware-backed credentials and automatic passwordless-login unlocking.
- Full compatibility with GNOME Keyring's private on-disk storage format.

PAM-assisted unlock, Secret portal interoperability, migration tooling, and additional frontends may be considered after the core service is functional and tested.

## Proposed architecture

The daemon is intended to consist of small, independently testable Rust components:

```text
Applications (libsecret, CLI clients, native D-Bus clients)
                         |
              session D-Bus / Secret Service
                         |
                  keyringd daemon
              +----------+----------+
              |          |          |
        protocol/API  collections  sessions
              |          |          |
              +------ domain -------+
                         |
                vault + crypto layer
                         |
                 encrypted storage

      Optional, separate components:
      prompt frontend / PAM helper / CLI
```

A possible workspace layout is:

```text
crates/
  keyringd/          # D-Bus daemon and lifecycle
  keyring-core/      # Collections, items, and service semantics
  keyring-crypto/    # Encryption and key management
  keyring-store/     # Persistence and recovery
  keyring-cli/       # Management commands
integration/
  pam/               # Optional, separately assessed PAM integration
docs/                # Specifications, threat model, ADRs, roadmap
tests/               # Protocol and integration tests
```

Crate boundaries are illustrative. The design review may consolidate modules to avoid unnecessary abstraction.

## Proposed technology stack

| Area | Candidate | Status |
| --- | --- | --- |
| Implementation | Rust (stable) | Preferred |
| D-Bus | `zbus` | Preferred |
| Async runtime | `tokio` | Under evaluation |
| Serialization | `serde` | Preferred |
| Encryption at rest | RustCrypto / XChaCha20-Poly1305 | Under security review |
| Password-based key derivation | Argon2id | Under security review |
| Sensitive memory handling | `secrecy`, `zeroize` | Defense in depth |
| Linux interfaces | `rustix` | Under evaluation |
| Diagnostics | `tracing` | Preferred |
| Service activation | D-Bus / systemd user services | Target integration |

GNOME libraries are excluded from the daemon's direct and transitive build/runtime dependencies. Third-party applications may still use GNOME libraries independently to talk to the standard Secret Service API.

## Compatibility

Keyringd will target the [Secret Service specification](https://specifications.freedesktop.org/secret-service/latest/), including these D-Bus interfaces:

- `org.freedesktop.Secret.Service`
- `org.freedesktop.Secret.Collection`
- `org.freedesktop.Secret.Item`
- `org.freedesktop.Secret.Session`
- `org.freedesktop.Secret.Prompt`

Passing an interface-level test is not sufficient. Compatibility will also be verified with real Secret Service clients and against behavior that applications rely on in practice.

Only one service should own `org.freedesktop.secrets` on a given session bus. Packaging and installation must account for conflicts with an existing GNOME Keyring or other Secret Service daemon.

## Security model

The project is security-sensitive. Design and implementation must explicitly address:

- Local threat actors, including other processes running as the same user.
- Credential exposure through D-Bus, prompts, logs, crash dumps, and memory.
- Authenticated vault encryption, password derivation, and key lifecycle management.
- File ownership and permissions, symlink attacks, atomic writes, and crash recovery.
- Malformed D-Bus messages, race conditions, and untrusted client input.
- Versioned data formats, migration, backup, and recovery.

**Important limitation:** The Secret Service API does not inherently provide strong isolation among applications running in the same user session. Encryption at rest does not prevent an already-authorized or compromised process from requesting accessible secrets while the vault is unlocked. Keyringd will document precisely what it protects—and what it does not.

No custom cryptographic primitives will be introduced. Production readiness requires interoperability testing, fuzzing, review of the cryptographic design, and independent security assessment. Rust memory safety is beneficial but is not itself a security guarantee.

## Roadmap

| Phase | Milestone | Exit criterion |
| --- | --- | --- |
| 0 | Feasibility and specification audit | Build-vs-fork decision and documented requirements |
| 1 | In-memory Secret Service daemon | Core D-Bus operations pass integration tests |
| 2 | Encrypted vault | Secure persistence, unlock/lock, and recovery tests |
| 3 | Client interoperability | Protocol edge cases and real-client tests pass |
| 4 | Linux desktop integration | D-Bus activation, systemd unit, and Arch package verified |
| 5 | Security hardening | Threat-model mitigations, fuzzing, and security review completed |

Feature scope and milestones may change after Phase 0. An MVP is **not** considered ready for production credential storage merely because it can save and retrieve secrets.

## Building and running

There is no supported build or installation procedure yet; implementation has not started. Once the first executable is available, this section will document toolchain requirements, local development, isolated D-Bus test sessions, installation, and rollback.

Do not replace an existing credential service on a primary workstation with an experimental build.

## Documentation

Planned design materials include:

- Requirements and scope
- Research and dependency audit
- Secret Service interoperability matrix
- Architecture decisions (ADRs)
- Security threat model and key lifecycle
- Storage format and recovery design
- Linux integration and packaging
- Testing strategy and implementation backlog

## Contributing

During planning, contributions are most useful as concrete specification clarifications, interoperability findings, threat-model improvements, dependency audits, and design reviews. Implementation contributions should follow the approved architecture and security requirements once those are established.

Please do not submit real passwords, vault contents, or other credentials in bug reports or test fixtures.

## License

Keyringd is released under the [MIT License](https://opensource.org/licenses/MIT).

## References

- [freedesktop.org Secret Service specification](https://specifications.freedesktop.org/secret-service/latest/)
- [GNOME Keyring](https://gitlab.gnome.org/GNOME/gnome-keyring)
- [zbus](https://github.com/dbus2/zbus)
