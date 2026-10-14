"""Clone immutable execution inputs for registered profiles in isolated directories."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(part)
    return value.hexdigest()


def registered_profiles(roster, names):
    rows = [row for row in roster if row['scenario'] in names]
    if not names or len(set(names)) != len(names) or len(rows) != len(names):
        raise ValueError('explicit unique registered profiles required')
    return rows


def validate_output(parent, output):
    if parent == output or parent in output.parents or output in parent.parents:
        raise ValueError('stress output must not overlap prepared inputs')
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('stress output must be new or empty')


def prepare(parent, output, names):
    parent, output = Path(parent).resolve(), Path(output).resolve()
    validate_output(parent, output)
    inputs = json.loads((parent / 'inputs.json').read_text())
    if inputs.get('experiment_study', {}).get('mode') != 'combined':
        raise ValueError('stress profiles require the registered combined rule arm')
    for name, digest in inputs['input_sha256'].items():
        if Path(name).name != name or sha(parent / name) != digest:
            raise ValueError('stress source prepared input hash mismatch')
    protocol = json.loads((parent / 'protocol.json').read_text())
    if sha(parent / 'protocol.json') != inputs['experiment_study']['protocol_sha256']:
        raise ValueError('stress source protocol binding differs')
    profiles = registered_profiles(protocol['profiles'], names)
    fresh = copy.deepcopy(inputs)
    fresh['experiment_study'].update(authorized_profiles=profiles,
        profile_source_prepared=str(parent), profile_source_receipt_sha256=sha(parent / 'inputs.json'),
        profile_preparation_sha256=sha(Path(__file__)))
    output.mkdir(parents=True, exist_ok=True)
    for name in inputs['input_sha256']:
        os.link(parent / name, output / name)
    (output / 'inputs.json').write_text(json.dumps(fresh, indent=2, ensure_ascii=False,
                                                allow_nan=False)+'\n')
    (output / 'requested-profiles.json').write_text(json.dumps(profiles, indent=2, allow_nan=False)+'\n')
    print('stress profiles', names, output, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--profile', action='append', required=True)
    args = parser.parse_args()
    prepare(args.prepared, args.output, args.profile)


if __name__ == '__main__':
    main()
