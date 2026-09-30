# MAESTRO Installation Guide

This guide installs the MAESTRO community source tree from GitHub.

## Requirements

- Git
- Python 3.11+
- Python 3.12 recommended
- pip
- terminal
- optional: Ollama for local model execution

## 1. Clone

```bash
git clone https://github.com/eddarsglobal/maestro.git
cd maestro
```

## 2. Check Python

```bash
python3 --version
```

MAESTRO requires Python 3.11 or newer.

Recommended:

```bash
python3.12 --version
```

## 3. Create the environment

```bash
python3.12 -m venv .venv
```

On a macOS installation where Python 3.12 is under `/usr/local/bin`:

```bash
/usr/local/bin/python3.12 -m venv .venv
```

## 4. Verify the environment

Use the virtual environment Python directly:

```bash
./.venv/bin/python --version
```

Do not rely on a shell alias named `python`.

## 5. Upgrade packaging tools

```bash
./.venv/bin/python -m pip install --upgrade pip setuptools wheel
```

## 6. Install MAESTRO

Development install:

```bash
./.venv/bin/python -m pip install -e .
```

Standard install:

```bash
./.venv/bin/python -m pip install .
```

## 7. Run tests

```bash
./.venv/bin/python -m unittest discover -s tests -q
```

The MAESTRO v1.1.0 R1 baseline was certified with:

```text
Ran 283 tests
OK
```

## 8. Boot

```bash
./.venv/bin/python - <<'PY'
from pathlib import Path
from maestro import ProductionGenesisSystem

system = ProductionGenesisSystem(Path("runtime"))
result = system.start()

print("VERSION :", result["version"])
print("STATUS  :", result["status"])
print("BOOT    :", result["boot"])
print("RECOVERY:", result["recovery"])
PY
```

Expected v1.1.0 status:

```text
VERSION : 1.1.0
STATUS  : READY
```

## 9. Optional local AI with Ollama

Verify Ollama:

```bash
ollama --version
ollama list
```

Verify the local API:

```bash
curl -fsS http://127.0.0.1:11434/api/tags
```

Install a model, for example:

```bash
ollama pull qwen3:8b
```

## Troubleshooting

### Wrong Python version

If installation says that Python 3.9 or another unsupported version is being used, recreate the virtual environment with Python 3.11+ and call the environment Python directly:

```bash
rm -rf .venv
/usr/local/bin/python3.12 -m venv .venv
./.venv/bin/python --version
./.venv/bin/python -m pip install -e .
```

### Runtime data

The mutable repository-root directories `runtime/` and `runtime_test/` are intentionally ignored by Git.

They are not source code.

### Support

Community questions should use GitHub Issues or Discussions when available.

Commercial or enterprise inquiries:

**maestro.men@gmail.com**
