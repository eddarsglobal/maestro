# MAESTRO v1.0.1 — LOCAL INTELLIGENCE

## Objective

Connect MAESTRO Production Genesis to a real local intelligence provider without changing the constitutional core.

## Reference provider

Ollama is the first local provider adapter.

Default endpoint:

```text
http://localhost:11434
```

## Added

- OllamaClient
- OllamaProviderAdapter
- OllamaEmbeddingAdapter
- Ollama model auto-discovery
- provider health inspection
- generation metrics
- capability-first local model policy
- LocalIntelligence facade

## Data policy

MAESTRO persists:
- final response if useful;
- provider/model identity;
- success/failure;
- latency;
- load duration;
- prompt/eval counts;
- tokens per second.

MAESTRO does not need to persist:
- model private/thinking text;
- raw context token arrays.

## Selection law

Bootstrap model selection is:

```text
CAPABILITY
↓
SMALLEST SUFFICIENT LOCAL MODEL
↓
ACADEMY MEASURES QUALITY/PERFORMANCE
↓
ADAPTIVE POLICY MAY PROPOSE A BETTER MODEL
```

No model name is constitutional authority.

## Current verified Mac deployment

The user's current Ollama installation has already demonstrated:
- local completion;
- ultra-light completion;
- local embeddings.

These empirical results are external deployment evidence, not hardcoded runtime rules.
