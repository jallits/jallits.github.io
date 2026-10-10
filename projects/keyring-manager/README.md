# Keyring Manager

**A GNOME-independent credential and key manager for Linux, powered by Keyringd.**

> **Status: Planning and design.** Keyring Manager is a working name, not a released application. No implementation, security review, or production-ready build is available yet. Features and technology choices described here are proposed unless explicitly marked otherwise.

## Overview

Keyring Manager aims to provide a single native desktop interface for managing local application secrets, cryptographic keys, and external password vaults without depending on GNOME libraries or services.

It is intended to replace the *management experience* provided by Seahorse (Passwords and Keys) while expanding that experience with password-manager capabilities, beginning with **Bitwarden**.

**Keyring Manager is a companion to [Keyringd](#relationship-to-keyringd), not a replacement for it.** Keyringd provides the local encrypted vault and the standards-compatible Secret Service daemon. This project provides the desktop user interface and optional integrations with other credential systems. They remain separate projects and separate processes.

The initial target is **Linux**, with particular attention to **Arch Linux, Omarchy, Wayland, and lightweight desktop environments**. The application should not require GNOME Shell, GTK, GLib, GObject, GIO, libadwaita, GCR, or GCK as direct or transitive application dependencies. External applications, such as GnuPG or the official Bitwarden CLI, retain their own dependencies.

## Goals

1. **One interface, multiple providers.** Present credentials and keys consistently without forcing them into a single vault or data model.
2. **Keyringd-first local secrets.** Use the standard Secret Service protocol for local application passwords and collections; do not duplicate Keyringd's cryptography or persistence.
3. **GNOME independence.** Build a native, accessible Linux UI without GNOME framework dependencies.
4. **Provider isolation.** Keep local credentials, remote vaults, and cryptographic agents under separate authentication, storage, and authorization policies.
5. **Standards and interoperability.** Integrate with existing D-Bus, OpenSSH, and GnuPG interfaces rather than inventing replacements unnecessarily.
6. **Security before convenience.** Make sensitive actions explicit and observable; avoid silent credential export or synchronization.
7. **Incremental delivery.** Ship a useful Seahorse replacement before attempting to replace the entire Bitwarden client ecosystem.

## Planned capabilities

| Area | Intended functionality | Integration | Initial priority |
| --- | --- | --- | --- |
| Application secrets | Browse, search, create, edit, delete, lock, and unlock collections and items | **Keyringd**, via FreeDesktop Secret Service | MVP |
| SSH keys | List keys, inspect public metadata, generate/import keys, manage agent identities where supported | OpenSSH tools and SSH-agent protocol | Early |
| OpenPGP keys | Inspect keys and identities, import/export public keys, manage trust and expiration where supported | GnuPG | Early |
| Bitwarden vault | Unlock, list/search, view, create/edit items, and initiate sync with appropriate authorization | Official Bitwarden CLI initially | After local MVP |
| Secure notes and TOTP | Manage provider-supported item types without flattening their semantics | Provider-specific capabilities | Later |
| Certificates | Inspect and organize X.509 certificates and related metadata | Established certificate/PKCS#11 interfaces | Later |
| Hardware-backed keys | Display and use supported keys without exporting private material | Existing tokens and agents | Exploratory |
| Passkeys | Investigate platform and browser interoperability | Requires separate protocol and UX design | Exploratory |

These are **design targets, not claims of existing support**. Feature availability will vary by provider. A signing-only hardware key, for example, must not be represented as an exportable password.

## Relationship to Keyringd

Keyringd is the separate, GNOME-free Rust daemon currently being designed to implement the [FreeDesktop Secret Service API](https://specifications.freedesktop.org/secret-service/latest/). Its implementation approach—including whether to build from scratch or leverage `oo7-daemon`—has not yet been finalized.

The two repositories have different responsibilities:

| Keyringd owns | Keyring Manager owns |
| --- | --- |
| The `org.freedesktop.secrets` session D-Bus service | The graphical experience for local secrets and external providers |
| Secret Service collections, items, sessions, prompts, and aliases | Presentation, search, navigation, editing workflows, and user interactions |
| Local encrypted vault storage and key lifecycle | Provider connections and provider-specific UI workflows |
| Local vault lock/unlock and persistence semantics | User-driven authorization for cross-provider actions |
| Protocol conformance, daemon lifecycle, and headless operation | Desktop integration, accessibility, and optional prompt frontend |

### Integration contract

- Keyring Manager will communicate with Keyringd primarily through the **standard Secret Service D-Bus API**, using the well-known bus name `org.freedesktop.secrets` and interfaces such as `org.freedesktop.Secret.Service`, `.Collection`, `.Item`, `.Session`, and `.Prompt`.
- The application will **not** directly read or modify Keyringd's private vault files, derive its vault keys, or bypass its lock state.
- If advanced management workflows require features beyond the Secret Service specification, they must be designed as **separately reviewed, versioned interfaces** with explicit authorization semantics; no private API is assumed today.
- Keyringd must remain usable headlessly and by third-party Secret Service clients **without this GUI running**.
- The GUI may eventually supply an optional prompt frontend, but it must not become a mandatory dependency of the daemon.
- Only one daemon can own `org.freedesktop.secrets` on a given session bus. This GUI does **not** acquire that name.

The Keyringd repository URL will be linked here once it has been published; no repository location is assumed.

## Architecture

```text
                    Keyring Manager (native Rust GUI)
                   +---------------------------------+
                   | Views, workflows, preferences   |
                   | Provider registry / capabilities|
                   | User-consent and unlock UX      |
                   +----------------+----------------+
                                    |
                     Provider-specific adapters
                   /                |               \
                  /                 |                \
        Local Secrets         Cryptographic Keys    Remote Vaults
        provider              providers             provider
            |                 /        \                |
     Secret Service       OpenSSH      GnuPG        Bitwarden CLI
        D-Bus API        agent/tools    tools          (initially)
            |                 |           |                |
         Keyringd         SSH keys    OpenPGP keys     Bitwarden vault
            |
      Encrypted local
      secret storage
```

The application **does not create a universal vault**. A unified list or search interface must preserve each provider's identity, access rules, supported operations, and unlock state.

### Provider model

Provider interfaces will be **capability-based**, not a single CRUD interface imposed on all backends. Initial concepts include:

- `SecretProvider`: enumerate and modify supported secrets and collections.
- `KeyProvider`: discover keys, inspect public metadata, and expose supported key operations.
- `SigningProvider`: request signatures through an agent or token without extracting private keys.
- `VaultProvider`: authenticate, unlock, lock, search, and synchronize where supported.
- `ProviderCapabilities`: declare which operations and item types a particular provider actually supports.

Names and Rust trait signatures are provisional. UI actions must be derived from advertised capabilities rather than inferred from item labels or types.

## Bitwarden integration

Bitwarden support is planned as a **provider**, not as an alternative implementation of the Keyringd service.

The first integration will evaluate the [official Bitwarden CLI (`bw`)](https://bitwarden.com/help/cli/) for authentication/unlock, item retrieval, editing, and synchronization. A dedicated adapter will isolate subprocess handling, data mapping, errors, credential exposure, and version compatibility.

A longer-term native client may be investigated separately. Bitwarden's Password Manager SDK is currently described by Bitwarden as an **internal, unsupported, unstable interface**, so this project will not assume a stable public SDK exists: [Bitwarden SDK repository](https://github.com/bitwarden/sdk-internal).

Initial Bitwarden integration will **not** claim parity with the official application. In particular, browser autofill, credential capture, browser passkey flows, organization administration, account recovery, and all advanced vault item types are not included in the initial deliverable. The official browser extension can remain in use alongside this application.

Support for Bitwarden-compatible self-hosted servers may follow the capabilities of the selected integration; interoperability must be tested rather than assumed.

## Security boundaries

**The unified interface must not imply unified trust.** Keyringd secrets, Bitwarden vault data, GnuPG key material, and SSH-agent identities remain independently managed.

The design must enforce the following rules:

- **No automatic bridges.** Do not expose a Bitwarden vault through `org.freedesktop.secrets`, mirror local application passwords to Bitwarden, or transfer private keys between providers by default.
- **Explicit transfers only.** Any cross-provider import, export, or copy requires an intentional user action and a reviewable authorization flow; support depends on what the providers permit.
- **Separate unlock sessions.** Unlocking Keyringd must not silently unlock Bitwarden, GnuPG, or an SSH agent (or vice versa).
- **Least exposure.** Prefer provider-side search and metadata-only listing when practical. Fetch or reveal secret values only when needed.
- **No secret-bearing telemetry.** Never log passwords, tokens, session keys, private keys, decrypted vault entries, or clipboard contents. Redact errors and diagnostics.
- **Careful CLI integration.** Avoid passing secret material in command-line arguments. Limit subprocess environments, inherited file descriptors, stdout/stderr handling, and lifetime of Bitwarden session state.
- **Explicit clipboard policy.** Secret copying must be deliberate. Clearing a clipboard entry on a timer is not a guarantee of deletion from clipboard managers or history.
- **Respect agents.** Prefer sign/decrypt operations through GnuPG, OpenSSH, or hardware tokens instead of extracting and re-storing private key bytes.
- **Locked means unavailable.** The UI must honor each provider's lock state and discard cached sensitive data when the relevant session ends.
- **Untrusted surfaces.** Treat item names, URLs, notes, imported key metadata, provider responses, and D-Bus traffic as untrusted input.

### Threat-model limitations

The Secret Service protocol does **not** inherently provide strong per-application isolation between all processes within an unlocked user session. A desktop GUI cannot fix that limitation simply by displaying approval dialogs. Clipboard managers, accessibility interfaces, screen capture, swap, crash dumps, compromised same-user processes, and malicious extensions may also expose secrets.

Security claims will be tied to explicit assumptions, integration tests, threat models, and independent review. Rust's memory-safety guarantees do not by themselves establish the security of the application.

**Do not use development builds to store production credentials.**

## Proposed technology stack

| Area | Candidate | Decision |
| --- | --- | --- |
| Language | Rust (stable) | Preferred |
| Native UI | Slint or Iced | Undecided; prototype and evaluate |
| D-Bus client | `zbus` | Preferred; align with Keyringd where appropriate |
| Async execution | Tokio | Under evaluation |
| Data modeling | `serde` and explicit provider types | Preferred |
| Sensitive memory hygiene | `secrecy`, `zeroize` where applicable | Defense in depth |
| SSH | Existing OpenSSH tools and SSH-agent interface | Preferred |
| OpenPGP | Existing GnuPG interfaces | Preferred |
| Bitwarden | Official `bw` CLI adapter | Initial approach |
| Diagnostics | `tracing` with strict secret redaction | Preferred |
| Distribution | Native Arch package initially | Target |

**No GUI toolkit has been selected.** The implementation should not introduce a GNOME framework dependency through its native UI stack. Third-party integrations are separate processes with independently audited dependencies.

## Development and repository layout

A possible Rust workspace layout is:

```text
crates/
  manager-app/             # Desktop executable and application lifecycle
  manager-ui/              # Views, presentation models, and accessibility
  manager-core/            # Domain concepts and provider capabilities
  provider-secret-service/ # Keyringd / Secret Service D-Bus adapter
  provider-ssh/            # OpenSSH integration
  provider-openpgp/        # GnuPG integration
  provider-bitwarden/      # Bitwarden CLI adapter
  manager-testing/         # Mocks and provider contract test helpers
docs/
  architecture/            # Boundaries, interfaces, and ADRs
  security/                # Threat model and sensitive-data handling
  compatibility/           # Keyringd and provider interoperability
packaging/
  arch/                    # Proposed Arch/Omarchy packaging
assets/                    # Icons and UI assets
```

This layout is illustrative. Crate boundaries should reflect testability and security review needs, not abstraction for its own sake.

### Build and run

There is **no supported build, installation, or run procedure yet**. The application and Keyringd are both in planning. Once code exists, this section will document the supported Rust toolchain, test-session D-Bus setup, Keyringd version compatibility, optional external provider requirements, packaging, and rollback.

Do not replace existing keyring services or connect experimental builds to live Bitwarden vaults without an explicitly documented testing and recovery process.

## Roadmap

| Phase | Deliverable | Exit criterion |
| --- | --- | --- |
| 0 — Design | Provider contracts, Keyringd integration contract, UI toolkit evaluation, threat model | Architecture decisions recorded and reviewed |
| 1 — Local MVP | Read/search/edit local Secret Service items, collection browsing, lock/unlock workflow | Integration tests against Keyringd and representative clients |
| 2 — Keys | SSH and OpenPGP browsing and supported management actions | Agent/tool interoperability tests; no accidental private-key exposure |
| 3 — Bitwarden | Optional CLI-backed login/unlock, browse/search, edit, and sync | Provider contract tests, negative-path tests, documented session handling |
| 4 — Desktop readiness | Accessible UX, packaging, failure recovery, regression coverage | Tested on Arch/Omarchy with a supported Keyringd release |
| 5 — Hardening | Security assessment and carefully selected advanced providers/features | Threat model, audit findings, and release criteria addressed |

Releases will indicate supported versions of Keyringd and optional integrations. A completed UI is not sufficient evidence that handling real secrets is safe.

## Non-goals for the first release

- Replacing the Keyringd daemon or creating a second `org.freedesktop.secrets` implementation.
- Reimplementing Keyringd's encrypted vault, storage format, or KDF.
- Inventing new cryptographic primitives or an SSH-agent replacement.
- Automatically federating, merging, or synchronizing all secret stores.
- Replacing GnuPG's cryptographic engine.
- Full replacement of the Bitwarden desktop and browser-extension ecosystem.
- Cross-platform support, GNOME-specific shell integration, or compatibility with Seahorse's internal libraries.

## Contributing

During planning, the most valuable contributions are provider interoperability findings, accessible desktop UI prototypes, security analysis, threat-model improvements, and small, testable architecture proposals.

Please **never include real passwords, private keys, vault exports, recovery codes, or session tokens** in issues, screenshots, logs, fixtures, or pull requests. Security-sensitive findings should be coordinated privately using a security disclosure process that will be published before the first release.

## Project status and naming

**Keyring Manager** is a provisional product and repository name. It is a separate application from **Keyringd**; neither project is affiliated with or endorsed by GNOME, Seahorse, Bitwarden, or their maintainers. References to those products describe compatibility goals and integration points, not sponsorship.

## License

Keyring Manager is released under the [MIT License](https://opensource.org/licenses/MIT).

## References

- Keyringd — separate companion daemon (repository URL to be added)
- [FreeDesktop Secret Service API](https://specifications.freedesktop.org/secret-service/latest/)
- [Seahorse / Passwords and Keys](https://gitlab.gnome.org/GNOME/seahorse)
- [GNOME Keyring](https://gitlab.gnome.org/GNOME/gnome-keyring)
- [Bitwarden CLI documentation](https://bitwarden.com/help/cli/)
- [Bitwarden internal SDK status](https://github.com/bitwarden/sdk-internal)
- [GnuPG](https://gnupg.org/)
- [OpenSSH](https://www.openssh.com/)
- [Slint](https://slint.dev/)
- [Iced](https://iced.rs/)
