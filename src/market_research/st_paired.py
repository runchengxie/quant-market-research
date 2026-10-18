"""Descriptive ST eligibility comparison; incomplete pairs never receive a return."""
from __future__ import annotations

import numpy as np
import pandas as pd


def classify_status(rows: pd.DataFrame, names: pd.DataFrame) -> pd.DataFrame:
    """Require dated known names and agreement with reconstructed daily state.

    This checks announcement dates, not original release vintages. Missing names,
    same-day announcements, state conflicts and unavailable positive states stay unknown.
    """
    result = rows.copy()
    active = names.copy()
    for col in ('start_date', 'end_date', 'ann_date'):
        active[col] = active[col].fillna('99999999').astype(str)
    frames = []
    for day, block in result.groupby('trade_date', sort=True):
        event = active.loc[(active.start_date <= day) & (active.end_date >= day)
                           & (active.ann_date < day)]
        event = event.sort_values(['ts_code', 'start_date', 'ann_date'])
        # Ambiguous latest names must not be resolved by an arbitrary input row.
        event = event.drop_duplicates()
        last_start = event.groupby('ts_code').start_date.transform('max')
        event = event.loc[event.start_date.eq(last_start)]
        ambiguous = event.groupby('ts_code').name.nunique().gt(1)
        event = event.drop_duplicates('ts_code', keep='last')
        event['ambiguous'] = event.ts_code.map(ambiguous)
        block = block.merge(event[['ts_code', 'name', 'change_reason', 'ambiguous']],
                            on='ts_code', how='left', validate='many_to_one')
        st_name = block.name.str.upper().str.contains('ST', na=False)
        known = block.name.notna() & ~block.ambiguous.fillna(True).astype(bool)
        agree = block.is_st.notna() & block.is_st.eq(st_name)
        available = ~st_name | block.st_available_from.fillna('99999999').le(day)
        block['status'] = np.where(known & agree & available,
                                   np.where(st_name, 'st', 'non_st'), 'unknown')
        block['delisting_period'] = block.change_reason.eq('退市整理期')
        block['name_known'] = known
        block['status_conflict'] = known & ~agree
        block['positive_not_available'] = known & st_name & ~available
        frames.append(block)
    return pd.concat(frames, ignore_index=True)


def pair_period(formation: pd.DataFrame, prices: pd.DataFrame, *, n: int,
                execution: str, endpoint: str) -> tuple[dict, pd.DataFrame]:
    """Rank before endpoint availability, then invalidate both arms on any missing mark.

    No individual name is removed because its forward price is absent. Original
    weights are retained in the audit even for invalid periods. All endpoint marks
    require positive volume/amount; stale or suspended marks are unresolved.
    """
    eligible = formation.loc[
        formation.status.ne('unknown') & ~formation.delisting_period
        & formation.total_mv.gt(0) & formation.amount.gt(0)
        & formation.adj_close.gt(0) & ~formation.is_suspended.fillna(True)
        & formation.list_date.notna() & formation.list_date.le(formation.trade_date)
        & (formation.delist_date.isna() | formation.delist_date.gt(formation.trade_date))
    ].sort_values(['total_mv', 'ts_code'])
    arms = {'include_st': eligible.head(n),
            'exclude_st': eligible.loc[eligible.status.eq('non_st')].head(n)}
    selected = []
    for arm, block in arms.items():
        block = block.copy()
        block['arm'] = arm
        block['weight'] = 1 / n
        selected.append(block)
    audit = pd.concat(selected, ignore_index=True)
    for label, day in [('entry', execution), ('end', endpoint)]:
        marks = prices.loc[prices.trade_date.eq(day),
                           ['ts_code', 'adj_close', 'amount', 'is_suspended']].copy()
        marks['valid'] = marks.adj_close.gt(0) & marks.amount.gt(0) & ~marks.is_suspended.fillna(True)
        marks = marks.rename(columns={c: f'{label}_{c}' for c in marks if c != 'ts_code'})
        audit = audit.merge(marks, on='ts_code', how='left', validate='many_to_one')
    audit['terminal_before_end'] = audit.delist_date.notna() & audit.delist_date.le(endpoint)
    audit['resolved'] = (audit.entry_valid.fillna(False).astype(bool)
                         & audit.end_valid.fillna(False).astype(bool)
                         & ~audit.terminal_before_end)
    audit['forward_return'] = (audit.end_adj_close / audit.entry_adj_close - 1).where(audit.resolved)
    full = all(len(b) == n for b in arms.values())
    complete = bool(full and audit.resolved.all())
    a, b = (set(arms[k].ts_code) for k in ('include_st', 'exclude_st'))
    record = {'n': n, 'execution': execution, 'endpoint': endpoint,
              'formation': str(formation.trade_date.iloc[0]), 'complete_pair': complete,
              'known_eligible': len(eligible), 'st_eligible': int(eligible.status.eq('st').sum()),
              'include_st_count': int(arms['include_st'].status.eq('st').sum()),
              'common_names': len(a & b), 'replaced_names': len(a - b),
              'common_weight': len(a & b) / n, 'unresolved_selected_rows': int((~audit.resolved).sum()),
              'terminal_selected_rows': int(audit.terminal_before_end.sum())}
    for arm in arms:
        block = audit.loc[audit.arm.eq(arm)]
        record[f'{arm}_return'] = float(block.forward_return.mean()) if complete else None
        record[f'{arm}_unresolved'] = int((~block.resolved).sum())
        record[f'{arm}_later_delisted'] = int(block.delist_date.notna().sum())
    record['difference'] = (record['include_st_return'] - record['exclude_st_return']) if complete else None
    audit['n'] = n
    audit['formation'] = record['formation']
    audit['execution'] = execution
    audit['endpoint'] = endpoint
    return record, audit
