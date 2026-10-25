"""Strict stdlib-only provider selection before installing a PR's dependencies."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import parse_qsl, urlsplit

PROVIDERS = {
    'data': ('quant-market-data-platform', 'quant-market-data-platform'),
    'runtime': ('quant-backtest-runtime', 'quant-backtest-runtime'),
    'platform': ('quant-platform', 'quant-platform'),
    'quality': ('research-code-quality', 'quant-code-quality'),
}
REPOSITORIES = {distribution: repository for distribution, repository in PROVIDERS.values()}
REPOSITORIES['research-contracts'] = 'quant-platform'


def locked_pins(manifest: dict, lock: dict) -> dict[str, str]:
    pins = {}
    for package in lock.get('package', []):
        name = package['name']
        if name not in REPOSITORIES:
            continue
        if name in pins or set(package['source']) != {'git'}:
            raise ValueError(f'ambiguous or non-Git provider: {name}')
        url = urlsplit(package['source']['git'])
        expected_path = f'/runchengxie/{REPOSITORIES[name]}.git'
        pairs = parse_qsl(url.query, strict_parsing=True, keep_blank_values=True)
        query = dict(pairs)
        allowed = {'rev', 'subdirectory'} if name == 'research-contracts' else {'rev'}
        if (url.scheme != 'https' or url.netloc != 'github.com' or url.path != expected_path
                or len(query) != len(pairs) or set(query) != allowed
                or re.fullmatch('[0-9a-f]{40}', query.get('rev', '')) is None
                or query['rev'] != url.fragment
                or (name == 'research-contracts'
                    and query['subdirectory'] != 'packages/research-contracts')):
            raise ValueError(f'{name} requires its official repository and complete pinned SHA')
        pins[name] = query['rev']
    if set(pins) != set(REPOSITORIES):
        raise ValueError('lock must select exactly one source for every provider')
    if pins['research-contracts'] != pins['quant-platform']:
        raise ValueError('platform and contracts must share one revision')
    project = manifest['project']
    dependencies = list(project.get('dependencies', []))
    for group in project.get('optional-dependencies', {}).values():
        dependencies.extend(group)
    dependencies.extend(manifest.get('tool', {}).get('uv', {}).get('override-dependencies', []))
    declared = set()
    for requirement in dependencies:
        match = re.match(r'([A-Za-z0-9_.-]+)', requirement)
        name = match.group(1).lower().replace('_', '-') if match else ''
        if name not in REPOSITORIES:
            continue
        reference = requirement.partition(';')[0].strip()
        expected = f'{name} @ git+https://github.com/runchengxie/{REPOSITORIES[name]}.git@{pins[name]}'
        if name == 'research-contracts':
            expected += '#subdirectory=packages/research-contracts'
        if reference != expected:
            raise ValueError(f'{name} manifest/override must match the locked official SHA')
        declared.add(name)
    # Quality is currently transitive; an explicit future quality requirement is checked above too.
    if set(REPOSITORIES) - {'research-code-quality'} - declared:
        raise ValueError('manifest is missing an explicit chain dependency')
    return pins


def read_locked_pins(source: Path) -> dict[str, str]:
    with (source / 'pyproject.toml').open('rb') as stream:
        manifest = tomllib.load(stream)
    with (source / 'uv.lock').open('rb') as stream:
        lock = tomllib.load(stream)
    return locked_pins(manifest, lock)


def verify_default_pins(source: Path, pins: dict[str, str]) -> None:
    """Read declarations without importing or executing a PR's optional-dependency modules."""
    def constant(filename: str, name: str):
        tree = ast.parse((source / 'src' / 'market_research' / filename).read_text())
        assignments = [node.value for node in tree.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == name
                               for target in node.targets)]
        if len(assignments) != 1:
            raise ValueError(f'exactly one literal default pin declaration required: {name}')
        return ast.literal_eval(assignments[0])

    defaults = constant('synthetic_chain.py', 'PINS')
    if not isinstance(defaults, dict):
        raise ValueError('default pin declarations must form a complete provider map')
    defaults = {**defaults, 'research-code-quality': constant('crossrepo_acceptance.py', 'QUALITY_PIN')}
    if defaults != pins:
        raise ValueError('default pin declarations must match the formal manifest and lock')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, help='selection result retained even for invalid inputs')
    args = parser.parse_args(argv)
    receipt = {'status': 'failed', 'sha256': {}}
    try:
        for name in ('pyproject.toml', 'uv.lock'):
            receipt['sha256'][name] = hashlib.sha256((args.source / name).read_bytes()).hexdigest()
        revision = subprocess.run(['git', '-C', str(args.source), 'rev-parse', 'HEAD'],
                                  capture_output=True, text=True, check=False)
        receipt['consumer_revision'] = revision.stdout.strip() if revision.returncode == 0 else None
        pins = read_locked_pins(args.source)
        verify_default_pins(args.source, pins)
        args.output.write_text(json.dumps(pins, indent=2) + '\n')
        receipt.update(status='passed', expected_providers=pins)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as error:
        receipt['error'] = str(error)
        print(f'Provider selection failed: {error}', file=sys.stderr)
    finally:
        if args.receipt:
            args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    return 0 if receipt['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
