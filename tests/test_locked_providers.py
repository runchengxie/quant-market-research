"""The committed manifest/lock define the automatic PR acceptance combination."""
import copy
from pathlib import Path
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[1]


def documents():
    return tomllib.loads((ROOT / 'pyproject.toml').read_text()), tomllib.loads((ROOT / 'uv.lock').read_text())


def test_upgrade_lock_and_manifest_select_new_runtime_without_static_pin_edits():
    from market_research.locked_providers import locked_pins
    manifest, lock = documents()
    runtime = next(item for item in lock['package'] if item['name'] == 'quant-backtest-runtime')
    old = runtime['source']['git'].split('#')[-1]
    new = 'a' * 40 if old != 'a' * 40 else 'b' * 40
    manifest['project']['optional-dependencies']['formal'] = [s.replace(old, new) for s in manifest['project']['optional-dependencies']['formal']]
    package = next(item for item in lock['package'] if item['name'] == 'quant-backtest-runtime')
    package['source']['git'] = package['source']['git'].replace(old, new)
    pins = locked_pins(manifest, lock)
    assert pins['quant-backtest-runtime'] == new
    assert pins['research-contracts'] == pins['quant-platform']


@pytest.mark.parametrize('mutation', ['owner', 'short_sha', 'ref', 'duplicate', 'missing', 'subdirectory', 'mismatch', 'override', 'contracts'])
def test_locked_selection_fails_closed(mutation):
    from market_research.locked_providers import locked_pins
    manifest, lock = documents()
    package = next(item for item in lock['package'] if item['name'] == 'quant-platform')
    current = package['source']['git'].split('#')[-1]
    different = 'a' * 40 if current != 'a' * 40 else 'b' * 40
    if mutation == 'owner':
        package['source']['git'] = package['source']['git'].replace('runchengxie', 'stranger')
    elif mutation == 'short_sha':
        package['source']['git'] = package['source']['git'].replace(current, current[:7])
    elif mutation == 'ref':
        package['source']['git'] = package['source']['git'].replace('rev=' + current, 'rev=main')
    elif mutation == 'duplicate':
        lock['package'].append(copy.deepcopy(package))
    elif mutation == 'missing':
        lock['package'].remove(package)
    elif mutation == 'subdirectory':
        package['source']['git'] = package['source']['git'].replace('?rev=', '?subdirectory=arbitrary&rev=')
    elif mutation == 'mismatch':
        package['source']['git'] = package['source']['git'].replace(current, different)
    elif mutation == 'override':
        manifest['tool']['uv']['override-dependencies'][0] = manifest['tool']['uv']['override-dependencies'][0].replace(current, different)
    else:
        package = next(item for item in lock['package'] if item['name'] == 'research-contracts')
        package['source']['git'] = package['source']['git'].replace(current, different)
    with pytest.raises(ValueError):
        locked_pins(manifest, lock)


def test_automatic_acceptance_keeps_exact_lock_without_running_resolution(tmp_path, monkeypatch):
    import json
    import os
    import sys
    from market_research.crossrepo_acceptance import run_acceptance
    tools = tmp_path / 'tools'
    tools.mkdir()
    uv = tools / 'uv'
    marker = tmp_path / 'unwanted-resolution'
    uv.write_text(
        f'#!{sys.executable}\n'
        'import os, sys\n'
        'from pathlib import Path\n'
        f'if sys.argv[1] == "lock":\n    Path({str(marker)!r}).touch(); sys.exit(97)\n'
        'if sys.argv[1] == "run":\n'
        '    if "python" in sys.argv:\n'
        '        os.execv(sys.executable, [sys.executable] + '
        'sys.argv[sys.argv.index("python") + 1:])\n'
        '    sys.exit(42)\n'
    )
    uv.chmod(0o755)
    monkeypatch.setenv('PATH', str(tools) + os.pathsep + os.environ['PATH'])
    output = tmp_path / 'receipt'
    assert run_acceptance(ROOT, output) == 1  # Deliberate chain failure retains lock evidence.
    receipt = json.loads((output / 'acceptance.json').read_text())
    assert not marker.exists()
    assert receipt['selection_mode'] == 'locked'
    assert receipt['lock_recomputed'] is False
    assert receipt['commands'][0]['argv'][1] == 'sync'
    assert receipt['commands'][-1]['exit_code'] == 42
    assert receipt['sha256']['original-uv.lock'] == receipt['sha256']['resolved-uv.lock']
    assert (output / 'resolved-uv.lock').read_bytes() == (ROOT / 'uv.lock').read_bytes()


def test_explicit_candidates_keep_omitted_providers_from_consumer_lock():
    import json
    from market_research.crossrepo_acceptance import candidate_pins
    from market_research.locked_providers import locked_pins
    manifest, lock = documents()
    base = locked_pins(manifest, lock)
    base['quant-backtest-runtime'] = 'a' * 40
    selected = candidate_pins(json.dumps({'quality': 'b' * 40}), base)
    assert selected['quant-backtest-runtime'] == 'a' * 40
    assert selected['research-code-quality'] == 'b' * 40


def test_locked_acceptance_refuses_installation_that_changes_the_lock(tmp_path, monkeypatch):
    import json
    import os
    import sys
    from market_research.crossrepo_acceptance import run_acceptance
    tools = tmp_path / 'tools'
    tools.mkdir()
    uv = tools / 'uv'
    uv.write_text(
        f'#!{sys.executable}\n'
        'import sys\nfrom pathlib import Path\n'
        'if sys.argv[1] == "sync":\n'
        '    lock = Path("uv.lock"); lock.write_text(lock.read_text() + "\\n# unexpected mutation\\n")\n'
        'else:\n    sys.exit(93)\n'
    )
    uv.chmod(0o755)
    monkeypatch.setenv('PATH', str(tools) + os.pathsep + os.environ['PATH'])
    output = tmp_path / 'receipt'
    assert run_acceptance(ROOT, output) == 1
    receipt = json.loads((output / 'acceptance.json').read_text())
    assert len(receipt['commands']) == 1
    assert receipt['lock_unchanged'] is False
    assert 'lock changed' in receipt['error']
    assert receipt['sha256']['original-uv.lock'] != receipt['sha256']['resolved-uv.lock']


def test_preinstall_selection_failure_retains_input_hashes_without_installing(tmp_path):
    import hashlib
    import json
    import subprocess
    import sys
    source = tmp_path / 'consumer'
    source.mkdir()
    manifest = (ROOT / 'pyproject.toml').read_text().replace('runchengxie', 'stranger')
    (source / 'pyproject.toml').write_text(manifest)
    (source / 'uv.lock').write_bytes((ROOT / 'uv.lock').read_bytes())
    output = tmp_path / 'providers.json'
    receipt = tmp_path / 'selection.json'
    result = subprocess.run([
        sys.executable, str(ROOT / 'src/market_research/locked_providers.py'),
        '--source', str(source), '--output', str(output), '--receipt', str(receipt),
    ], capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert not output.exists()
    evidence = json.loads(receipt.read_text())
    assert evidence['status'] == 'failed'
    assert evidence['sha256']['pyproject.toml'] == hashlib.sha256((source / 'pyproject.toml').read_bytes()).hexdigest()
    assert evidence['sha256']['uv.lock'] == hashlib.sha256((source / 'uv.lock').read_bytes()).hexdigest()
    assert 'manifest/override' in evidence['error']


def test_formal_upgrade_requires_matching_default_declarations_without_executing_modules(tmp_path):
    from market_research.locked_providers import read_locked_pins, verify_default_pins
    pins = read_locked_pins(ROOT)
    package = tmp_path / 'src' / 'market_research'
    package.mkdir(parents=True)
    marker = tmp_path / 'must-not-execute'
    defaults = {key: value for key, value in pins.items() if key != 'research-code-quality'}
    (package / 'synthetic_chain.py').write_text(
        f'raise RuntimeError({str(marker)!r})\nPINS = {defaults!r}\n'
    )
    (package / 'crossrepo_acceptance.py').write_text(
        f'raise RuntimeError({str(marker)!r})\nQUALITY_PIN = {pins["research-code-quality"]!r}\n'
    )
    upgraded = dict(pins)
    upgraded['quant-backtest-runtime'] = 'a' * 40 if pins['quant-backtest-runtime'] != 'a' * 40 else 'b' * 40
    with pytest.raises(ValueError, match='default pin'):
        verify_default_pins(tmp_path, upgraded)
    defaults['quant-backtest-runtime'] = upgraded['quant-backtest-runtime']
    (package / 'synthetic_chain.py').write_text(f'raise RuntimeError("not executed")\nPINS = {defaults!r}\n')
    verify_default_pins(tmp_path, upgraded)
    assert not marker.exists()


@pytest.mark.parametrize('replacement', ['', '[engine]', '[legacy,engine]'])
def test_runtime_requires_exact_legacy_extra(replacement):
    from market_research.locked_providers import locked_pins

    manifest, lock = documents()
    manifest['project']['optional-dependencies']['formal'] = [
        requirement.replace('quant-backtest-runtime[legacy]', 'quant-backtest-runtime' + replacement)
        for requirement in manifest['project']['optional-dependencies']['formal']
    ]
    with pytest.raises(ValueError, match='quant-backtest-runtime'):
        locked_pins(manifest, lock)


def test_manual_candidate_requirements_keep_legacy_runtime_capability():
    from market_research.crossrepo_acceptance import requirements

    runtime = next(requirement for requirement in requirements(
        {'quant-backtest-runtime': 'a' * 40}
    ) if requirement.startswith('quant-backtest-runtime'))
    assert runtime.startswith('quant-backtest-runtime[legacy] @ ')
