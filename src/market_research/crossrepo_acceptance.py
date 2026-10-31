"""Disposable official-provider acceptance using the existing synthetic CLI."""
from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from market_research.synthetic_chain import PINS

from market_research.locked_providers import PROVIDERS, REPOSITORIES, read_locked_pins, verify_default_pins

QUALITY_PIN = '6daeeca7a3d405f23c8ad49c8364bfdc8e9bb661'


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate candidate key: {key}')
        result[key] = value
    return result


def candidate_pins(payload: str, base_pins: dict[str, str] | None = None) -> dict[str, str]:
    candidates = json.loads(payload, object_pairs_hook=_unique_pairs)
    if not isinstance(candidates, dict):
        raise ValueError('candidates must be an object')
    pins = dict(base_pins) if base_pins is not None else {**PINS, 'research-code-quality': QUALITY_PIN}
    for key, revision in candidates.items():
        if key not in PROVIDERS:
            raise ValueError(f'unknown provider: {key}')
        if not isinstance(revision, str) or re.fullmatch('[0-9a-f]{40}', revision) is None:
            raise ValueError(f'{key} requires a complete lowercase commit SHA')
        pins[PROVIDERS[key][0]] = revision
        if key == 'platform':
            pins['research-contracts'] = revision
    return pins


def validate_expected_pins(supplied: dict[str, str]) -> dict[str, str]:
    if not isinstance(supplied, dict) or set(supplied) != set(REPOSITORIES):
        raise ValueError('expected providers must include exactly the coordinated official packages')
    expected = candidate_pins(json.dumps({
        key: supplied[distribution] for key, (distribution, _) in PROVIDERS.items()
    }))
    if supplied != expected:
        raise ValueError('expected providers must include exactly the coordinated official packages')
    return expected


def requirements(pins: dict[str, str]) -> list[str]:
    return [
        f"{name}{'[legacy]' if name == 'quant-backtest-runtime' else ''} @ git+https://github.com/runchengxie/{REPOSITORIES[name]}.git@{revision}"
        + ('#subdirectory=packages/research-contracts' if name == 'research-contracts' else '')
        + (" ; python_version >= '3.12'" if name in
           ('quant-backtest-runtime', 'quant-platform', 'research-contracts') else '')
        for name, revision in pins.items()
    ]


def snapshot_environment(destination: Path) -> None:
    """Retain actual installed provenance before running the potentially failing chain."""
    distributions = {}
    for distribution in metadata.distributions():
        record = distribution.read_text('RECORD')
        distributions[distribution.metadata['Name']] = {
            'version': distribution.version,
            'direct_url': json.loads(distribution.read_text('direct_url.json') or '{}'),
            'record_sha256': hashlib.sha256(record.encode()).hexdigest() if record else None,
        }
    destination.write_text(json.dumps({
        'python': {'executable': sys.executable, 'version': platform.python_version()},
        'distributions': distributions,
    }, indent=2) + '\n')


def run_acceptance(source: Path, output: Path, payload: str | None = None) -> int:
    # Validate before creating outputs or running any command.
    if payload is not None:
        candidate_pins(payload)  # Reject untrusted candidate text before creating outputs.
    pins = {}
    source = source.resolve()
    output = output.resolve()
    if output.is_relative_to(source):
        raise ValueError("acceptance output must be outside the consumer source")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        'schema_version': 1, 'expected_providers': pins,
        'python': {'executable': sys.executable, 'version': platform.python_version()},
        'commands': [], 'status': 'failed',
        'selection_mode': 'locked' if payload is None else 'explicit_candidates',
        'lock_recomputed': payload is not None,
    }
    clean_env = {key: value for key, value in os.environ.items()
                 if not key.startswith(('PYTHON', 'UV_', 'VIRTUAL_ENV', 'GIT_'))}
    clean_env['PYTHONNOUSERSITE'] = '1'

    def command(argv, cwd):
        index = len(receipt['commands'])
        with (output / f'command-{index}.log').open('w') as log:
            result = subprocess.run(argv, cwd=cwd, env=clean_env, stdout=log,
                                    stderr=subprocess.STDOUT, check=False)
        receipt['commands'].append({'argv': argv, 'exit_code': result.returncode,
                                    'log': f'command-{index}.log'})
        if result.returncode:
            raise subprocess.CalledProcessError(result.returncode, argv)

    try:
        receipt['consumer_revision'] = subprocess.check_output(
            ['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True,
            stderr=subprocess.STDOUT).strip()
        receipt['consumer_source_sha256'] = {
            str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((source / 'src').rglob('*.py'))
        }
        pins = read_locked_pins(source)
        if payload is None:
            verify_default_pins(source, pins)
        if payload is not None:
            pins = candidate_pins(payload, pins)
        receipt['expected_providers'] = pins
        shutil.copy2(source / 'uv.lock', output / 'original-uv.lock')
        shutil.copy2(source / 'pyproject.toml', output / 'original-pyproject.toml')
        with tempfile.TemporaryDirectory(prefix='crossrepo-acceptance-') as temporary:
            project = Path(temporary)
            shutil.copytree(source / 'src', project / 'src',
                            ignore=shutil.ignore_patterns('__pycache__', '*.egg-info'))
            shutil.copy2(source / 'uv.lock', project / 'uv.lock')
            manifest = (source / 'pyproject.toml').read_text()
            if payload is not None:
                # Explicit manual experiments alone resolve overrides in this disposable copy.
                manifest, count = re.subn(
                    r'(?m)^override-dependencies = \[.*?^\]',
                    'override-dependencies = ' + json.dumps(requirements(pins)), manifest,
                    flags=re.DOTALL)
                if count != 1:
                    raise ValueError('expected exactly one existing uv override block')
            (project / 'pyproject.toml').write_text(manifest)
            shutil.copy2(project / 'pyproject.toml', output / 'resolved-pyproject.toml')
            if payload is not None:
                command(['uv', 'lock', '--python', sys.executable], project)
            shutil.copy2(project / 'uv.lock', output / 'resolved-uv.lock')
            extras = ['--extra', 'dev', '--extra', 'duckdb', '--extra', 'formal',
                      '--extra', 'integration']
            command(['uv', 'sync', '--locked', '--python', sys.executable, *extras], project)
            shutil.copy2(project / 'uv.lock', output / 'resolved-uv.lock')
            receipt['lock_unchanged'] = (
                (output / 'original-uv.lock').read_bytes() == (output / 'resolved-uv.lock').read_bytes()
            )
            if payload is None and not receipt['lock_unchanged']:
                raise ValueError('committed lock changed during locked acceptance')
            command(['uv', 'run', '--locked', *extras, 'python', '-c',
                     'from pathlib import Path; import sys; '
                     'from market_research.crossrepo_acceptance import snapshot_environment; '
                     'snapshot_environment(Path(sys.argv[1]))',
                     str(output / 'installed-environment.json')], project)
            (output / 'expected-providers.json').write_text(json.dumps(pins))
            command(['uv', 'run', '--locked', *extras, 'market-research-synthetic-chain',
                     '--output', str(output / 'chain'), '--expected-providers',
                     str(output / 'expected-providers.json')], project)
        receipt['status'] = 'passed'
    except (OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as error:
        receipt['error'] = str(error)
    finally:
        for name in ('original-uv.lock', 'resolved-uv.lock', 'original-pyproject.toml',
                     'resolved-pyproject.toml', 'installed-environment.json'):
            path = output / name
            if path.exists():
                receipt.setdefault('sha256', {})[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        (output / 'acceptance.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return 0 if receipt['status'] == 'passed' else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--candidates', default='', help='JSON: data/runtime/platform/quality to SHA')
    args = parser.parse_args()
    return run_acceptance(args.source.resolve(), args.output, args.candidates or None)


if __name__ == '__main__':
    raise SystemExit(main())
