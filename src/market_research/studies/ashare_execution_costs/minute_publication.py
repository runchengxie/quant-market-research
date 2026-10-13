"""Fixed aggregate projection for reviewed minute execution results."""
from __future__ import annotations

import math

SCENARIOS = {'gross_1m', 'fees_1m', 'fees_10m', 'fees_100m', 'fast_10m', 'split_10m',
             'weekly_10m', 'buffer_10m', 'minimum_1m'}
FIELDS = ('scenario', 'capital_cny', 'execution_minutes', 'release_slices',
          'commission_minimum_cny', 'terminal_nav', 'transaction_cost_cny',
          'mean_one_way_turnover', 'target_notional_completion', 'arrival_shortfall_p90_bp',
          'cost_unavailable_orders', 'negative_cash_sessions', 'orders', 'zero_fill_orders',
          'partial_fill_orders')


def _iso(day: str) -> str:
    return f'{day[:4]}-{day[4:6]}-{day[6:]}'


def public_projection(proposals: list[dict], blocked: dict) -> dict:
    """No row-level orders, symbols, machine paths or unreviewed extra fields."""
    windows = []
    for proposal in proposals:
        if (proposal.get('schema_version') != 'execution-minute-results.v1'
                or proposal.get('evidence') != 'modeled_bar_execution_not_live_capacity'
                or proposal.get('complete') is not True or proposal.get('expected_scenarios') != 9):
            raise ValueError('only a complete modeled scenario matrix can be reviewed for publication')
        rows = proposal['scenarios']
        if len(rows) != 9 or {row['scenario'] for row in rows} != SCENARIOS:
            raise ValueError('scenario names are incomplete or duplicated')
        selected = []
        for row in rows:
            clean = {field: row[field] for field in FIELDS}
            for field, value in clean.items():
                if field != 'scenario' and value is not None and not math.isfinite(value):
                    raise ValueError('nonfinite public metric')
            if clean['negative_cash_sessions'] != 0 or clean['terminal_nav'] <= 0:
                raise ValueError('unfunded scenario cannot be published as completed execution')
            selected.append(clean)
        inputs = proposal['inputs']
        if inputs['count'] != 40:
            raise ValueError('this publication contract is for the public 40-name diagnostic')
        suspension = inputs['suspension_valuation_audit']
        if suspension['carried_symbol_days'] and 'max_calendar_staleness_days' not in suspension:
            raise ValueError('carried valuations require reviewed maximum staleness')
        start, end = inputs['start'], inputs['end']
        window = {
            'id': '2024h2' if start == '20240701' and end == '20241231' else start[:4],
            'start': _iso(start), 'end': _iso(end), 'sessions': inputs['sessions'],
            'observed_bars': inputs['bar_audit']['rows'],
            'synthetic_suspension_marks': inputs['suspension_valuation_audit']['carried_symbol_days'],
            'max_calendar_staleness_days': inputs['suspension_valuation_audit'].get('max_calendar_staleness_days', 0),
            'corporate_events': inputs['corporate_action_audit']['events'],
            'scenarios': selected,
        }
        windows.append(window)
    return {'schema_version': 'execution-minute-public.v1', 'published': True, 'count': 40,
            'windows': windows,
            'blocked_full_2024': {key: blocked[key] for key in ('unexplained_original', 'unresolved_reobserved')},
            'source_sha256': {}}
