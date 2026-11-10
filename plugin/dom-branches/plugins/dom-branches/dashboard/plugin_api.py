"""Backend half of the ``dom-branches`` Hermes Desktop plugin (read-only).

Hermes' web server imports this file by path and mounts ``router`` under
``/api/plugins/dom-branches`` -- only while ``dom-branches`` is in the host's
``plugins.enabled``. The router runs inside the gateway process and answers for
the gateway's OWN Hermes home (a ``profile`` query is not read), so the DOM run
directory is taken from ``<hermes_home>/dom-branches.json``::

    {"directory": "E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/runtime/ORIENT/home"}

The directory must resolve (symlinks, ``..``) inside ``<PROJECT_ROOT>/runtime``;
anything else is refused with an error record that does not name the path.
The data comes from ``python -m mockup.overview`` (the product's read-only
reader) run as a subprocess without a shell and with a 10 s timeout. Every
failure is an error RECORD with HTTP 200 (``{"error": ...}``): in the pane a
thrown error is indistinguishable from a transport failure.

Pure functions (``read_config``, ``resolve_directory``, ``run_overview``,
``overview_payload``) are separate from the router so they can be called
without FastAPI, which is the host's dependency.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from fastapi import APIRouter
    from fastapi.concurrency import run_in_threadpool
except ImportError:  # imported on a host without FastAPI (tests)
    APIRouter = None
    run_in_threadpool = None

PANEL_SCHEMA_VERSION = "dom_branches_panel/v1"
CONFIG_NAME = "dom-branches.json"
PROJECT_ROOT = Path("E:/opencode_harness_portable/projects/omh-baseline-dom-mcp")
PYTHON = Path("E:/opencode_harness_portable/.venv/Scripts/python.exe")
TIMEOUT_SECONDS = 10
MAX_OUTPUT_BYTES = 5_000_000
DEFAULT_LIMIT = 200
BRANCH_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")
ERROR_STATUSES = {"READER_ERROR", "DIRECTORY_REFUSED", "INVALID_ARGUMENT"}


class PanelError(Exception):
    """A refusal whose message is safe to show (never names foreign paths)."""


def _error(message: str, **extra: Any) -> dict[str, Any]:
    record = {"error": message, "schema_version": PANEL_SCHEMA_VERSION}
    record.update(extra)
    return record


def resolve_hermes_home() -> Path:
    try:
        from hermes_constants import get_hermes_home
    except ImportError:
        get_hermes_home = None
    if get_hermes_home is not None:
        return Path(get_hermes_home())
    configured = os.environ.get("HERMES_HOME", "").strip()
    return Path(configured) if configured else Path.home() / ".hermes"


def read_config(hermes_home: str | Path) -> dict[str, Any]:
    """The parsed ``dom-branches.json`` of this home; PanelError if unusable."""
    path = Path(hermes_home) / CONFIG_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PanelError(f"{CONFIG_NAME} not found in the Hermes home of this gateway")
    except (OSError, ValueError):
        raise PanelError(f"{CONFIG_NAME} is unreadable or not valid JSON")
    if not isinstance(data, dict) or not isinstance(data.get("directory"), str) or not data["directory"].strip():
        raise PanelError(f'{CONFIG_NAME} must be {{"directory": "<run dir>"}}')
    return data


def resolve_directory(raw: str, project_root: str | Path = PROJECT_ROOT) -> Path:
    """Resolve ``raw`` and require it strictly inside ``<project_root>/runtime``."""
    if not isinstance(raw, str) or "\x00" in raw:
        raise PanelError("directory is not a valid path")
    candidate = Path(raw)
    if not candidate.is_absolute():
        raise PanelError("directory must be absolute")
    try:
        resolved = candidate.resolve()
        runtime = (Path(project_root) / "runtime").resolve()
    except (OSError, RuntimeError, ValueError):
        raise PanelError("directory cannot be resolved")
    if resolved == runtime or not resolved.is_relative_to(runtime):
        raise PanelError("directory is outside the project runtime")
    return resolved


_BOOTSTRAP = (
    "import sys; sys.path.insert(0, sys.argv[1]); sys.argv[1:2] = []; "
    "from mockup.overview import main; sys.exit(main())"
)


def run_overview(
    directory: Path,
    branch: str | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    project_root: str | Path = PROJECT_ROOT,
    python: str | Path = PYTHON,
    timeout: float = TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run ``mockup.overview`` and return its record, or an error record.

    ``-I`` makes the interpreter ignore ``PYTHONPATH``, so the project root is put
    on ``sys.path`` by a tiny bootstrap instead of the environment (``-B``: the
    gateway must not write bytecode into the product tree).
    """
    root = str(Path(project_root))
    argv = [str(python), "-I", "-B", "-c", _BOOTSTRAP, root, "--directory", str(directory), "--limit", str(int(limit))]
    if branch is not None:
        argv += ["--branch", branch]
    env = {k: v for k, v in os.environ.items() if k.upper() in {"SYSTEMROOT", "PATH", "TEMP", "TMP"}}
    env["PYTHONPATH"] = root
    try:
        done = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=timeout, shell=False, check=False)
    except subprocess.TimeoutExpired:
        return _error(f"reader timed out after {int(timeout)} s")
    except (OSError, ValueError) as exc:
        return _error(f"reader could not start: {type(exc).__name__}")
    if done.returncode != 0:
        return _error(f"reader exited with code {done.returncode}")
    if len(done.stdout) > MAX_OUTPUT_BYTES:
        return _error("reader output too large")
    try:
        record = json.loads(done.stdout.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return _error("reader returned invalid JSON")
    if not isinstance(record, dict):
        return _error("reader returned a non-object")
    if record.get("status") in ERROR_STATUSES:
        record.setdefault("error", f"reader status {record['status']}")
    return record


def overview_payload(
    hermes_home: str | Path,
    branch: str | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    project_root: str | Path = PROJECT_ROOT,
    python: str | Path = PYTHON,
    timeout: float = TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """The record the pane renders for this gateway's home. Never raises."""
    try:
        if branch is not None and not BRANCH_RE.match(str(branch)):
            return _error("invalid branch name")
        directory = resolve_directory(read_config(hermes_home)["directory"], project_root)
        return run_overview(directory, branch, limit, project_root=project_root, python=python, timeout=timeout)
    except PanelError as exc:
        return _error(str(exc))
    except Exception as exc:  # the failure becomes the record the pane shows
        return _error(f"{type(exc).__name__}")


if APIRouter is not None:
    router = APIRouter()

    @router.get("/overview")
    async def overview() -> dict[str, Any]:
        return await run_in_threadpool(overview_payload, resolve_hermes_home())

    @router.get("/branch")
    async def branch(branch: str = "") -> dict[str, Any]:
        if not branch:
            return _error("branch is required")
        return await run_in_threadpool(overview_payload, resolve_hermes_home(), branch)
