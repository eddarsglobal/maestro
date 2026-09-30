# Contributing to MAESTRO

Thank you for considering a contribution to MAESTRO.

MAESTRO is open to engineers, researchers, designers, security specialists and AI builders who want to improve the project.

## Before you start

For small fixes, documentation improvements and tests, you can open a pull request directly.

For significant architectural work, please open an Issue first.

Examples:

- new Council or Council authority change;
- state-machine changes;
- governance changes;
- new provider architecture;
- persistence format changes;
- policy activation changes;
- security model changes;
- breaking public APIs.

## Development setup

```bash
git clone https://github.com/eddarsglobal/maestro.git
cd maestro

python3.12 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip setuptools wheel
./.venv/bin/python -m pip install -e .

./.venv/bin/python -m unittest discover -s tests -q
```

## Pull-request expectations

A contribution should normally include:

1. a clear description of the problem;
2. the rationale for the proposed change;
3. tests for behavioral changes;
4. updated documentation where applicable;
5. no unrelated refactoring;
6. evidence that the relevant tests pass.

## MAESTRO invariants

Contributions must not casually break MAESTRO's core architectural principles.

In particular:

```text
MAESTRO COMMANDS MODELS.
MODELS DO NOT COMMAND MAESTRO.
```

Changes affecting authority boundaries require explicit architectural review.

## Security

Do not submit undisclosed security vulnerabilities through public Issues.

See `SECURITY.md`.

## Licensing and contribution rights

By contributing, you confirm that you have the right to submit the contribution.

MAESTRO is intended to support both an AGPL community distribution and separate commercial licensing by EddarsGlobal.

A Contributor License Agreement may be required for material contributions as the project governance matures.

## Contact

Community collaboration should happen publicly through GitHub whenever possible.

Commercial inquiries:

**maestro.men@gmail.com**
