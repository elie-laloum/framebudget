from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

from .errors import BudgetError


def run(
    argv: Sequence[str], *, timeout: float = 300, cwd: str | Path | None = None
) -> subprocess.CompletedProcess[str]:
    if timeout <= 0:
        raise BudgetError("Search budget exhausted")
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        raise BudgetError("Command exceeded its time budget") from exc
    except OSError as exc:
        raise BudgetError(str(exc)) from exc
    if result.returncode:
        raise BudgetError("Command failed: " + result.stderr[-1800:])
    return result
