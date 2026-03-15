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
from pag.spinner import Spinner, dump_payload

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

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        verbose: bool = False,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers={"X-RD-Token": api_key},
            timeout=TIMEOUT,
        )
        self._verbose = verbose

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

    def _post(self, path: str, body: dict, *, spinner_msg: str) -> dict:
        """POST with optional spinner and verbose logging."""
        if self._verbose:
            dump_payload(f"Request POST {path}", body)

        with Spinner(spinner_msg):
            resp = self._client.post(path, json=body)

        self._raise_for_status(resp)
        data = resp.json()

        if self._verbose:
            dump_payload(f"Response {resp.status_code}", data)

        return data

    # ── inferences ───────────────────────────────────────────────────────

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        """POST /v1/inferences — generate images or check cost."""
        body = request.model_dump(exclude_none=True)
        msg = "Checking cost" if request.check_cost else "Generating"
        data = self._post("/inferences", body, spinner_msg=msg)
        return InferenceResponse.model_validate(data)

    # ── custom styles ────────────────────────────────────────────────────

    def create_style(self, request: StyleCreateRequest) -> StyleResponse:
        """POST /v1/styles."""
        body = request.model_dump(exclude_none=True)
        data = self._post("/styles", body, spinner_msg="Creating style")
        return StyleResponse.model_validate(data)

    def update_style(
        self, style_id: str, request: StyleUpdateRequest
    ) -> StyleResponse:
        """PATCH /v1/styles/{style_id}."""
        body = request.model_dump(exclude_none=True)

        if self._verbose:
            dump_payload(f"Request PATCH /styles/{style_id}", body)

        with Spinner("Updating style"):
            resp = self._client.patch(f"/styles/{style_id}", json=body)

        self._raise_for_status(resp)
        data = resp.json()

        if self._verbose:
            dump_payload(f"Response {resp.status_code}", data)

        return StyleResponse.model_validate(data)

    def delete_style(self, style_id: str) -> None:
        """DELETE /v1/styles/{style_id}."""
        if self._verbose:
            dump_payload(f"Request DELETE /styles/{style_id}", {})

        with Spinner("Deleting style"):
            resp = self._client.delete(f"/styles/{style_id}")

        self._raise_for_status(resp)
