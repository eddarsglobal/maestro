# MAESTRO Governed Supply-Chain Verification Constitution

## Scope

This constitution governs BMF-022:

Adapters and update artifacts have provenance and integrity verification.

BMF-022 verifies supply-chain evidence for adapter and update artifacts.

Verification is evidence.

Verification is not trust, installation, activation, authorization, execution, or system truth.

## SCV-01 — Every governed artifact has an explicit manifest

Supply-chain verification SHALL operate on an explicit ArtifactManifest.

The manifest SHALL identify:

- artifact identity
- artifact kind
- artifact version
- claimed origin
- source reference
- digest algorithm
- expected digest
- optional signer identity
- optional signature algorithm

An adapter or update artifact SHALL NOT be treated as verified solely because it was discovered.

DISCOVERED != VERIFIED.

## SCV-02 — Integrity is independently computed

Artifact integrity SHALL be determined from the observed artifact bytes.

SCV0.1 SHALL compute SHA-256 over the observed bytes and compare it with the manifest expected digest.

A digest mismatch SHALL fail verification.

HASH MATCH != TRUST.

DIGEST MATCH != AUTHORIZATION.

## SCV-03 — Provenance claims are explicitly bound

Artifact provenance SHALL identify the same artifact identity, version, origin, source reference, digest algorithm, and digest as the manifest.

A provenance mismatch SHALL fail closed.

A provenance claim SHALL NOT become verified merely because its fields are present.

PROVENANCE CLAIM != VERIFIED PROVENANCE.

## SCV-04 — Signature presence is not signature validity

Signature state SHALL distinguish at least:

- ABSENT
- UNKNOWN
- VALID
- INVALID

SIGNATURE PRESENT != SIGNATURE VALID.

An externally supplied signature-verification result SHALL remain explicit evidence.

SCV0.1 SHALL NOT silently invent cryptographic validation.

## SCV-05 — Verified provenance requires valid signature evidence

PROVENANCE VERIFIED SHALL require:

- manifest/provenance binding
- artifact/digest binding
- signer binding
- signature algorithm binding
- VALID cryptographic verification evidence

PROVENANCE VERIFIED without VALID signature evidence SHALL fail closed.

VALID signature evidence SHALL resolve matching provenance to VERIFIED.

## SCV-06 — Overall verification state is deterministic and fail-closed

The governed verification result SHALL distinguish:

- VERIFIED
- FAILED
- INCOMPLETE

FAILED integrity, FAILED provenance, or INVALID signature SHALL produce FAILED verification.

Verified integrity plus verified provenance SHALL produce VERIFIED verification.

Unresolved provenance or signature SHALL remain INCOMPLETE.

UNKNOWN != VERIFIED.

INCOMPLETE != FAILED.

INCOMPLETE != VERIFIED.

Equivalent evidence SHALL produce equivalent verification identity.

## SCV-07 — Verification grants no trust

SUPPLY-CHAIN VERIFIED != TRUSTED.

A VERIFIED artifact SHALL NOT silently assert trust.

Trust requires a separate governed authority boundary.

No supply-chain result SHALL itself promote an artifact into a trusted operational resource.

## SCV-08 — Verification grants no lifecycle authority

VERIFIED ARTIFACT != INSTALLATION AUTHORIZED.
VERIFIED ARTIFACT != INSTALLED.
VERIFIED ARTIFACT != ACTIVATION AUTHORIZED.
VERIFIED ARTIFACT != ACTIVATED.
VERIFIED ARTIFACT != EXECUTION AUTHORIZED.
VERIFIED ARTIFACT != EXECUTED.

Any attempted lifecycle or authority escalation inside BMF-022 SHALL fail closed.

## SCV-09 — Supply-chain verification is passive

BMF-022 SHALL perform no:

- network access
- download
- registry mutation
- installation
- activation
- authorization
- execution
- migration
- promotion
- Core mutation

The verification contract SHALL remain deterministic and side-effect free.

It SHALL remain technology-generic.

Contemporary signing providers, package managers, operating systems, runtimes, protocols, and hardware identities SHALL NOT become constitutional requirements.

## SCV-10 — BMF-022 remains separate from BMF-023

BMF-022 produces governed supply-chain verification evidence.

BMF-023 governs observability across generations.

SUPPLY-CHAIN VERIFICATION != OBSERVABILITY SYSTEM.

BMF-022 SHALL NOT create or activate monitoring infrastructure.

VERIFICATION EVIDENCE != PERFORMANCE EVIDENCE.

VERIFICATION EVIDENCE != RELIABILITY VERDICT.

VERIFICATION EVIDENCE != SECURITY VERDICT.

## Canonical boundary

ARTIFACT MANIFEST
        +
OBSERVED ARTIFACT BYTES
        +
PROVENANCE CLAIM
        +
OPTIONAL SIGNATURE-VERIFICATION EVIDENCE
        |
        v
GOVERNED SUPPLY-CHAIN VERIFICATION
        |
        +---- FAILED
        |
        +---- INCOMPLETE
        |
        +---- VERIFIED

The boundary stops before trust, installation, activation, authorization, execution, Core mutation, or observability-system creation.

## Final invariant

MAESTRO MAY VERIFY THE INTEGRITY AND PROVENANCE OF AN ADAPTER OR UPDATE ARTIFACT WITHOUT GRANTING THAT ARTIFACT TRUST OR OPERATIONAL AUTHORITY.
