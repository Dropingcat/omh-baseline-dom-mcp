"""Test wiring: every mutable artifact stays under P/runtime.

``Service`` refuses any directory outside ``P/runtime`` (RUNTIME_PATH_REQUIRED).
That guard is a product rule and is not weakened here: instead the pytest
``tmp_path`` fixture is re-bound to ``P/runtime/tmp/<unique>/`` per test, and the
directory is removed afterwards.  Process-spawning tests inherit the same
directory, so child processes also stay inside the project runtime.
"""
import os
import shutil
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'runtime'
TMP_ROOT = RUNTIME / 'tmp'


def _safe(name):
    cleaned = ''.join(c if (c.isalnum() or c in '-_') else '_' for c in name)
    return cleaned[:60] or 'test'


@pytest.fixture(scope='session', autouse=True)
def _runtime_temp_env():
    """TEMP/TMP of the test session point into runtime/, never the system temp."""
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    keys = ('TMPDIR', 'TEMP', 'TMP')
    saved = {k: os.environ.get(k) for k in keys}
    for key in keys:
        os.environ[key] = str(TMP_ROOT)
    yield
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def tmp_path(request):
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    directory = TMP_ROOT / f"{_safe(request.node.name)}-{uuid.uuid4().hex[:10]}"
    directory.mkdir()
    yield directory
    shutil.rmtree(directory, ignore_errors=True)
