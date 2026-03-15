"""Animated spinner with elapsed time for API calls."""

from __future__ import annotations

import itertools
import json
import sys
import threading
import time


_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class Spinner:
    """Context-manager that shows an animated spinner on stderr."""

    def __init__(self, message: str = "Generating") -> None:
        self._message = message
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._start_time = 0.0

    def __enter__(self) -> Spinner:
        self._start_time = time.monotonic()
        self._stop.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join()
        elapsed = time.monotonic() - self._start_time
        # Clear the spinner line and print final time
        sys.stderr.write(f"\r\033[K{self._message}... done ({elapsed:.1f}s)\n")
        sys.stderr.flush()

    def _spin(self) -> None:
        for frame in itertools.cycle(_FRAMES):
            if self._stop.is_set():
                break
            elapsed = time.monotonic() - self._start_time
            sys.stderr.write(f"\r\033[K{frame} {self._message}... {elapsed:.1f}s")
            sys.stderr.flush()
            self._stop.wait(0.08)


def dump_payload(label: str, data: dict, *, redact_base64: bool = True) -> None:
    """Pretty-print a JSON payload to stderr, optionally truncating base64 fields."""
    display = _redact(data) if redact_base64 else data
    formatted = json.dumps(display, indent=2, ensure_ascii=False)
    sys.stderr.write(f"\n── {label} ──\n{formatted}\n")
    sys.stderr.flush()


def _redact(obj: object) -> object:
    """Recursively replace long strings (likely base64) with a truncated preview."""
    if isinstance(obj, dict):
        return {k: _redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(item) for item in obj]
    if isinstance(obj, str) and len(obj) > 200:
        return f"{obj[:40]}...({len(obj)} chars)"
    return obj
