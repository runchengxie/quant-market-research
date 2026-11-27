"""Audit a retained bounded reference query; keep vendor output outside Git."""
import argparse
import hashlib
import json
from pathlib import Path
from market_research.bmll_identity import audit_identities
from market_research.bmll_pilot import decode_statement

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--response', type=Path, required=True)
p.add_argument('--symbols', nargs='+', required=True)
p.add_argument('--dates', nargs='+', required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
if a.output.exists() or a.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
    p.error('Use a new private output outside the repository')
result = audit_identities(decode_statement(json.loads(a.response.read_text())), a.symbols, a.dates)
result['response_sha256'] = hashlib.sha256(a.response.read_bytes()).hexdigest()
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(result, indent=2, allow_nan=False))
print(json.dumps({'observations': len(result['observations']), 'transitions': len(result['transitions'])}))
