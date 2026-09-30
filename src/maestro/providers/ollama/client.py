from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class OllamaHTTPError(RuntimeError):
    pass


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = self.base_url + path
        data = None
        headers = {}
        method = "GET"

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
            method = "POST"

        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(
                req,
                timeout=self.timeout,
            ) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)

        except urllib.error.HTTPError as exc:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )
            raise OllamaHTTPError(
                f"Ollama HTTP {exc.code}: {body}"
            ) from exc

        except urllib.error.URLError as exc:
            raise OllamaHTTPError(
                f"Ollama unreachable: {exc}"
            ) from exc

    def tags(self) -> dict[str, Any]:
        return self._request("/api/tags")

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        system: str | None = None,
        options: dict[str, Any] | None = None,
        think: bool | str | None = None,
    ) -> dict[str, Any]:

        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system

        if options:
            payload["options"] = options

        # Important:
        # False is a valid explicit policy.
        # Therefore do NOT use `if think:`.
        if think is not None:
            payload["think"] = think

        return self._request(
            "/api/generate",
            payload,
        )

    def embed(
        self,
        *,
        model: str,
        input_text: str | list[str],
    ) -> dict[str, Any]:

        return self._request(
            "/api/embed",
            {
                "model": model,
                "input": input_text,
            },
        )
