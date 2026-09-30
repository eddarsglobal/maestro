# MAESTRO Security Policy

## Reporting a vulnerability

Please do **not** open a public GitHub Issue for a vulnerability that could put MAESTRO users at risk.

Report security issues privately to:

**maestro.men@gmail.com**

Include when possible:

- affected MAESTRO version or commit;
- operating system;
- affected component;
- reproduction steps;
- impact;
- logs or proof of concept with secrets removed;
- suggested mitigation, if known.

## Sensitive information

Do not include:

- private API keys;
- passwords;
- private tokens;
- personal information not required for reproduction;
- unrelated user data.

## Scope

Security reports may involve:

- Local Gateway security;
- provider boundaries;
- tool execution;
- filesystem boundaries;
- authority bypass;
- state-transition bypass;
- evidence tampering;
- persistence corruption;
- transaction integrity;
- unsafe deserialization;
- dependency vulnerabilities;
- model/provider injection that crosses a control-plane boundary.

The maintainers may request additional reproduction evidence before classifying a report.
