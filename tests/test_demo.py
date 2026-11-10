"""The documented demo command must really run and produce inspectable artifacts."""
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml
import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'runtime'
PASSED_ENV = ('SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATH', 'PATHEXT', 'USERPROFILE',
              'APPDATA', 'LOCALAPPDATA', 'PROGRAMDATA', 'SYSTEMDRIVE', 'NUMBER_OF_PROCESSORS')


def env():
    values = {k: v for k, v in os.environ.items() if k in PASSED_ENV}
    values.update(PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE='1',
                  TEMP=str(RUNTIME / 'tmp'), TMP=str(RUNTIME / 'tmp'))
    (RUNTIME / 'tmp').mkdir(parents=True, exist_ok=True)
    return values


def demo(output_dir, *extra):
    return subprocess.run([sys.executable, '-B', '-m', 'mockup.demo', '--output-dir', str(output_dir), *extra],
                          cwd=str(ROOT), env=env(), capture_output=True, text=True, encoding='utf8', timeout=180)


def test_demo_creates_real_artifacts(tmp_path):
    run_directory = tmp_path / 'demo'
    finished = demo(run_directory)
    assert finished.returncode == 0, finished.stderr[-2000:]
    assert 'REMAINDER (NOT IMPLEMENTED / NOT PROVEN)' in finished.stdout

    database = run_directory / 'dom.sqlite3'
    assert database.stat().st_size > 0
    exports = sorted((run_directory / 'exports').glob('*.yaml'))
    assert len(exports) >= 4
    document = yaml.safe_load(exports[0].read_text(encoding='utf8'))
    assert document['simulated'] is True
    assert document['claims'][0]['origin_branch'] in ('AA', 'AB')
    assert document['claims'][0]['origin_version'] == 'synthetic-artifact-v1'
    assert (run_directory / 'omh-target.json').exists()

    summary = json.loads((run_directory / 'demo.json').read_text(encoding='utf8'))
    assert summary['trace_pending']['ready_for_owner_review'] is False
    assert 'SYNC_PENDING' in summary['trace_pending']['blockers']
    assert summary['trace_ready']['ready_for_owner_review'] is True
    assert summary['trace_ready']['owner_close_called'] is False
    assert all(marker['origin_branch'] in ('AA', 'AB') for marker in summary['origin_markers'].values())
    assert summary['historical_export']['sha256'] in summary['historical_export']['handle']

    # no silent overwrite of an existing run directory
    refused = demo(run_directory)
    assert refused.returncode != 0
    assert 'REFUSED' in (refused.stdout + refused.stderr)

    # explicit reset is allowed only for a disposable run directory
    reset = demo(run_directory, '--reset')
    assert reset.returncode == 0, reset.stderr[-2000:]
    assert (run_directory / 'dom.sqlite3').exists()


def marker(path, tool='mockup.demo'):
    (path / 'demo.json').write_text(json.dumps({'tool': tool, 'simulated': True,
                                                'run_directory': str(path)}), encoding='utf8')


def test_reset_is_limited_to_this_demos_own_run_directory(tmp_path):
    """M1: ``--reset`` never deletes the run root, foreign dirs or earlier runs."""
    from mockup.demo import new_run_directory

    foreign = tmp_path / 'foreign'
    foreign.mkdir()
    (foreign / 'keep.txt').write_text('keep', encoding='utf8')
    with pytest.raises(SystemExit) as refused:
        new_run_directory(foreign, True)
    assert 'REFUSED' in str(refused.value)
    assert (foreign / 'keep.txt').read_text(encoding='utf8') == 'keep'

    with pytest.raises(SystemExit) as refused_root:
        new_run_directory(ROOT / 'runtime' / 'runs', True)
    assert 'REFUSED' in str(refused_root.value)

    hand_made = tmp_path / 'hand-made'
    hand_made.mkdir()
    marker(hand_made, tool='someone-else')
    with pytest.raises(SystemExit):
        new_run_directory(hand_made, True)
    assert (hand_made / 'demo.json').exists()

    own = new_run_directory(tmp_path / 'demo-a')
    marker(own)
    earlier = new_run_directory(tmp_path / 'earlier-run')
    reused = new_run_directory(own, True)
    assert reused == own and not (own / 'demo.json').exists()
    assert earlier.exists(), 'resetting one run must not remove another'

