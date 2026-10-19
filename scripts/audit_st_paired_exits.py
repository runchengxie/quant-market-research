#!/usr/bin/env python3
"""Inventory failed frozen ST pairs without supplying prices or changing returns."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(audit: pd.DataFrame, suspension: pd.DataFrame,
              aliases: dict[str, str] | None = None) -> pd.DataFrame:
    """Preserve arm/N rows and distinguish evidence absence from suspension."""
    failed = audit.loc[~audit.resolved].copy()
    aliases = aliases or {}
    for label, day in [('entry', 'execution'), ('end', 'endpoint')]:
        present = failed[f'{label}_adj_close'].notna()
        valid = failed[f'{label}_valid'].fillna(False).astype(bool)
        failed[f'{label}_failure'] = 'valid'
        failed.loc[~valid & present, f'{label}_failure'] = 'invalid_observed_mark'
        failed.loc[~valid & ~present, f'{label}_failure'] = 'missing_clean_row'
        events = suspension.loc[suspension.suspend_type.eq('S'), ['ts_code', 'trade_date']]
        keys = set(map(tuple, events.drop_duplicates().to_numpy()))
        failed[f'{label}_suspension_evidence_code'] = [
            code if (code, date) in keys else
            aliases.get(code, '') if (aliases.get(code), date) in keys else ''
            for code, date in zip(failed.ts_code, failed[day])
        ]
        failed[f'{label}_dated_suspension'] = failed[
            f'{label}_suspension_evidence_code'].ne('')
    failed['resolution'] = 'unresolved'
    failed['required_evidence'] = [
        ('entry trade on scheduled date; ' if entry != 'valid' else '')
        + ('scheduled endpoint trade or independently specified settlement protocol'
           if terminal else 'scheduled endpoint trade')
        if end != 'valid' else 'entry trade on scheduled date'
        for entry, end, terminal in zip(
            failed.entry_failure, failed.end_failure, failed.terminal_before_end)
    ]
    columns = ['formation', 'execution', 'endpoint', 'ts_code', 'name', 'n', 'arm',
               'weight', 'delist_date', 'terminal_before_end', 'entry_failure',
               'end_failure', 'entry_dated_suspension', 'end_dated_suspension',
               'entry_suspension_evidence_code', 'end_suspension_evidence_code',
               'resolution', 'required_evidence']
    return failed[columns].sort_values(['formation', 'ts_code', 'n', 'arm'])


def output_directory(path: Path) -> Path:
    """Resolve symlinks and reject existing or repository-contained output."""
    output = path.resolve()
    repo = Path(__file__).resolve().parents[1]
    if output.exists() or output.is_relative_to(repo):
        raise ValueError('output must be a new directory outside the repository')
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--suspensions', required=True, type=Path)
    parser.add_argument('--facts', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output = output_directory(args.output)
    receipt_path = args.source / 'receipt.json'
    receipt = json.loads(receipt_path.read_text())
    audit_path = args.source / 'selection_audit.parquet'
    if digest(audit_path) != receipt['outputs'][audit_path.name]:
        raise ValueError('frozen audit hash mismatch')
    audit = pd.read_parquet(audit_path)
    if audit.duplicated(['formation', 'n', 'arm', 'ts_code']).any():
        raise ValueError('duplicate selected security')
    facts = json.loads(args.facts.read_text())
    aliases = {r['canonical_code']: r['historical_code']
               for r in facts.get('suspension_identity_aliases', [])}
    failed = inventory(audit, pd.read_parquet(args.suspensions), aliases)
    unique = failed.drop_duplicates(['formation', 'ts_code'])
    terminal = unique.loc[unique.terminal_before_end].merge(
        pd.DataFrame(facts['events']), on=['ts_code', 'formation', 'delist_date'],
        how='left', validate='one_to_one')
    if terminal.source_url.isna().any():
        raise ValueError('terminal event without reviewed evidence')
    args.output.mkdir(parents=True, exist_ok=False)
    failed.to_csv(args.output / 'failed_selected_rows.csv', index=False)
    unique.to_csv(args.output / 'failed_formation_issuers.csv', index=False)
    terminal.to_csv(args.output / 'terminal_evidence.csv', index=False)
    summary = {
        'schema_version': 'market-research.st-exit-inventory.v1',
        'revision_safe': False, 'protocol_changed': False,
        'failed_selected_rows': len(failed), 'failed_formation_issuers': len(unique),
        'terminal_formation_issuers': len(terminal),
        'terminal_with_missing_entry': int(terminal.entry_failure.ne('valid').sum()),
        'dated_suspension_selected_rows_entry': int(failed.entry_dated_suspension.sum()),
        'dated_suspension_selected_rows_end': int(failed.end_dated_suspension.sum()),
        'newly_resolved_events': 0, 'returns_recomputed': False,
        'failure_patterns': failed.groupby(
            ['entry_failure', 'end_failure', 'terminal_before_end']).size().reset_index(
                name='selected_rows').to_dict('records'),
        'inputs': {str(p): digest(p) for p in
                   (audit_path, receipt_path, args.suspensions, args.facts, Path(__file__))},
        'limitations': 'Dated suspension matches are same-provider corroboration. '
        'Absent suspension rows do not establish tradability. Official termination '
        'and transfer notices do not establish cash settlement or an endpoint fill. '
        'No raw provider rows are published; output rows are derived audit inventory.',
    }
    summary['outputs'] = {p.name: digest(p) for p in args.output.iterdir()}
    (args.output / 'receipt.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('inputs', 'outputs')}, indent=2))


if __name__ == '__main__':
    main()
