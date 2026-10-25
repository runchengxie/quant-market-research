"""Candidate inputs are a closed set, never executable requirements or URLs."""
import pytest

from market_research.synthetic_chain import PINS


def test_candidate_platform_expands_both_distributions():
    from market_research.crossrepo_acceptance import candidate_pins
    pins = candidate_pins('{"platform": "' + 'a' * 40 + '"}')
    assert pins['quant-platform'] == pins['research-contracts'] == 'a' * 40
    assert pins['quant-market-data-platform'] == PINS['quant-market-data-platform']


@pytest.mark.parametrize('payload', [
    '{"runtime": "main"}', '{"runtime": "' + 'A' * 40 + '"}',
    '{"runtime": "$(touch /tmp/unsafe)"}', '{"unknown": "' + 'a' * 40 + '"}',
    '[]', '{"data": null}', '{"data": "' + 'a' * 40 + '", "data": "' + 'b' * 40 + '"}',
])
def test_candidates_reject_ambiguous_or_untrusted_input(payload):
    from market_research.crossrepo_acceptance import candidate_pins
    with pytest.raises(ValueError):
        candidate_pins(payload)


def test_expected_revisions_reject_nonofficial_distribution_source(monkeypatch):
    from market_research import synthetic_chain
    class Distribution:
        version = '0'
        def read_text(self, name):
            return '{"url":"https://github.com/stranger/quant-market-data-platform.git", "vcs_info":{"commit_id":"' + PINS['quant-market-data-platform'] + '"}}'
    monkeypatch.setattr(synthetic_chain.metadata, 'distribution', lambda name: Distribution())
    with pytest.raises(ValueError, match='official'):
        synthetic_chain._environment()


def test_acceptance_refuses_output_inside_consumer_before_running(tmp_path):
    from market_research.crossrepo_acceptance import run_acceptance
    with pytest.raises(ValueError, match='outside'):
        run_acceptance(tmp_path, tmp_path / 'generated', '{}')
    assert not (tmp_path / 'generated').exists()


def test_failed_install_retains_command_exit_and_lock_provenance(tmp_path, monkeypatch):
    import json
    import subprocess
    from pathlib import Path
    from market_research.crossrepo_acceptance import run_acceptance
    source = tmp_path / 'consumer'
    source.mkdir()
    subprocess.run(['git', 'init', '--quiet', str(source)], check=True)
    subprocess.run(['git', '-C', str(source), '-c', 'user.name=Test', '-c',
                    'user.email=test@example.com', 'commit', '--quiet', '--allow-empty',
                    '-m', 'fixture'], check=True)
    (source / 'src').mkdir()
    (source / 'src' / 'fixture.py').write_text('VALUE = 1\n')
    (source / 'uv.lock').write_text('lock fixture\n')
    (source / 'pyproject.toml').write_text('[tool.uv]\noverride-dependencies = [\n]\n')
    tools = tmp_path / 'tools'
    tools.mkdir()
    uv = tools / 'uv'
    uv.write_text('#!/bin/sh\necho deliberate fixture failure\nexit 42\n')
    uv.chmod(0o755)
    monkeypatch.setenv('PATH', str(tools) + ':' + str(Path('/usr/bin')))
    output = tmp_path / 'evidence'
    assert run_acceptance(source, output, '{}') == 1
    receipt = json.loads((output / 'acceptance.json').read_text())
    assert receipt['status'] == 'failed'
    assert receipt['commands'][0]['exit_code'] == 42
    assert len(receipt['consumer_revision']) == 40
    assert receipt['sha256']['original-uv.lock']
    assert 'deliberate fixture failure' in (output / 'command-0.log').read_text()


def test_candidate_overrides_preserve_formal_python_floor():
    from market_research.crossrepo_acceptance import candidate_pins, requirements
    dependencies = requirements(candidate_pins('{}'))
    formal = [item for item in dependencies if item.split(' @ ')[0] in
              ('quant-backtest-runtime', 'quant-platform', 'research-contracts')]
    assert len(formal) == 3
    assert all(item.endswith(" ; python_version >= '3.12'") for item in formal)


def test_cli_rejects_uncoordinated_contracts_before_running(tmp_path):
    import json
    from market_research.crossrepo_acceptance import candidate_pins
    from market_research.synthetic_chain import main
    pins = candidate_pins('{}')
    pins['research-contracts'] = 'a' * 40
    expected = tmp_path / 'expected.json'
    expected.write_text(json.dumps(pins))
    with pytest.raises(ValueError, match='coordinated'):
        main(['--output', str(tmp_path / 'chain'), '--expected-providers', str(expected)])
    assert not (tmp_path / 'chain').exists()


def test_source_provenance_failure_still_retains_failed_receipt(tmp_path):
    import json
    from market_research.crossrepo_acceptance import run_acceptance
    source = tmp_path / 'non-git-source'
    source.mkdir()
    output = tmp_path / 'evidence'
    assert run_acceptance(source, output, '{}') == 1
    receipt = json.loads((output / 'acceptance.json').read_text())
    assert receipt['status'] == 'failed'
    assert receipt['commands'] == []
    assert 'error' in receipt


def test_installed_snapshot_is_independent_of_chain_success(tmp_path):
    import json
    import sys
    from importlib import metadata
    from market_research.crossrepo_acceptance import snapshot_environment
    destination = tmp_path / 'installed.json'
    snapshot_environment(destination)
    snapshot = json.loads(destination.read_text())
    assert snapshot['python']['executable'] == sys.executable
    pytest_package = snapshot['distributions']['pytest']
    assert pytest_package['version'] == metadata.version('pytest')
    assert len(pytest_package['record_sha256']) == 64


def test_chain_failure_keeps_independent_installed_environment(tmp_path, monkeypatch):
    import json
    import os
    from pathlib import Path
    import sys
    from market_research.crossrepo_acceptance import run_acceptance
    tools = tmp_path / 'tools'
    tools.mkdir()
    uv = tools / 'uv'
    # Stub only package orchestration; execute the actual installed snapshot code.
    uv.write_text(
        f'#!{sys.executable}\n'
        'import os, sys\n'
        'if sys.argv[1] == "run":\n'
        '    if "python" in sys.argv:\n'
        '        os.execv(sys.executable, [sys.executable] + '
        'sys.argv[sys.argv.index("python") + 1:])\n'
        '    sys.exit(42)\n'
    )
    uv.chmod(0o755)
    monkeypatch.setenv('PATH', str(tools) + os.pathsep + os.environ['PATH'])
    output = tmp_path / 'evidence'
    assert run_acceptance(Path(__file__).resolve().parents[1], output, '{}') == 1
    receipt = json.loads((output / 'acceptance.json').read_text())
    assert receipt['commands'][-1]['exit_code'] == 42
    assert receipt['sha256']['installed-environment.json']
    snapshot = json.loads((output / 'installed-environment.json').read_text())
    assert snapshot['distributions']['pytest']['version']
    assert not (output / 'chain' / 'evidence.json').exists()


@pytest.mark.parametrize('expected', [{}, {'quant-market-data-platform': PINS['quant-market-data-platform']}])
def test_python_api_rejects_partial_expected_provider_maps(expected, tmp_path):
    from market_research.synthetic_chain import run_smoke
    output = tmp_path / "output"
    with pytest.raises(ValueError, match='exactly'):
        run_smoke(output, expected_pins=expected)
    assert not output.exists()
