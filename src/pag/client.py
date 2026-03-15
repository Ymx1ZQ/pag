"""HTTP client for the Retro Diffusion API."""

from __future__ import annotations

import httpx

from pag.models import (
    InferenceRequest,
    InferenceResponse,
    StyleCreateRequest,
    StyleResponse,
    StyleUpdateRequest,
)

BASE_URL = "https://api.retrodiffusion.ai/v1"
TIMEOUT = 120.0  # generous timeout for image generation


class APIError(Exception):
    """Raised when the Retro Diffusion API returns an error."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class RetroClient:
    """Synchronous client for the Retro Diffusion API."""

    def __init__(self, api_key: str, *, base_url: str = BASE_URL) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers={"X-RD-Token": api_key},
            timeout=TIMEOUT,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> RetroClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ── helpers ──────────────────────────────────────────────────────────

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.is_success:
            return
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise APIError(resp.status_code, str(detail))

    # ── inferences ───────────────────────────────────────────────────────

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        """POST /v1/inferences — generate images or check cost."""
        resp = self._client.post(
            "/inferences",
            json=request.model_dump(exclude_none=True),
        )
        self._raise_for_status(resp)
        return InferenceResponse.model_validate(resp.json())

    # ── custom styles ────────────────────────────────────────────────────

    def create_style(self, request: StyleCreateRequest) -> StyleResponse:
        """POST /v1/styles."""
        resp = self._client.post(
            "/styles",
            json=request.model_dump(exclude_none=True),
        )
        self._raise_for_status(resp)
        return StyleResponse.model_validate(resp.json())

    def update_style(
        self, style_id: str, request: StyleUpdateRequest
    ) -> StyleResponse:
        """PATCH /v1/styles/{style_id}."""
        resp = self._client.patch(
            f"/styles/{style_id}",
            json=request.model_dump(exclude_none=True),
        )
        self._raise_for_status(resp)
        return StyleResponse.model_validate(resp.json())

    def delete_style(self, style_id: str) -> None:
        """DELETE /v1/styles/{style_id}."""
        resp = self._client.delete(f"/styles/{style_id}")
        self._raise_for_status(resp)

    def list_styles(self) -> list[StyleResponse]:
        """GET /v1/styles."""
        resp = self._client.get("/styles")
        self._raise_for_status(resp)
        return [StyleResponse.model_validate(s) for s in resp.json()]
