import importlib.util
from pathlib import Path

import pytest


def module():
    spec = importlib.util.spec_from_file_location('stress_prepare',
        Path(__file__).parents[2] / 'scripts/prepare_execution_stress_profiles.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_stress_profiles_must_be_registered_without_duplicates():
    roster = [{'scenario': 'registered', 'initial_cash': 1e7}]
    assert module().registered_profiles(roster, ['registered']) == roster
    for names in [[], ['unknown'], ['registered', 'registered']]:
        with pytest.raises(ValueError):
            module().registered_profiles(roster, names)


def test_stress_output_cannot_overlap_prepared_inputs(tmp_path):
    parent = tmp_path / 'original'
    for output in [parent, parent / 'nested', tmp_path]:
        with pytest.raises(ValueError):
            module().validate_output(parent, output)
