# Local AI in MAESTRO

MAESTRO is designed so that intelligence resources can remain replaceable.

A local provider is not MAESTRO itself.

```text
MAESTRO
  |
Sovereign Intelligence
  |
Provider Adapter
  |
Inference Runtime
  |
Model
```

## Ollama

Ollama is the currently verified local provider path.

Typical local endpoint:

```text
http://127.0.0.1:11434
```

Useful commands:

```bash
ollama --version
ollama list
ollama pull qwen3:8b
```

API check:

```bash
curl -fsS http://127.0.0.1:11434/api/tags
```

MAESTRO's Ollama integration lives under:

```text
src/maestro/providers/ollama/
```

Sovereign routing infrastructure lives under:

```text
src/maestro/sovereign/
```

Future provider work should preserve the principle that providers supply intelligence but do not become the authority of the MAESTRO control plane.
