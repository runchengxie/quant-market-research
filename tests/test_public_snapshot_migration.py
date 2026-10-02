from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sync_public_research_data.py"
spec = importlib.util.spec_from_file_location("snapshot_migration", SCRIPT)
assert spec and spec.loader
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)


def test_missing_source_leaves_existing_targets_untouched(tmp_path: Path) -> None:
    source, target = tmp_path / "source", tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "first.csv").write_text("new")
    (target / "first.csv").write_text("old")
    with pytest.raises(FileNotFoundError):
        migration.copy_files(source, target, ("first.csv", "missing.csv"))
    assert (target / "first.csv").read_text() == "old"
    assert list(target.iterdir()) == [target / "first.csv"]


def _snapshots(tmp_path: Path) -> tuple[Path, Path]:
    source, target = tmp_path / "source", tmp_path / "target"
    for relative in migration.INDEX_FILES:
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("reviewed derived fixture")
    target.mkdir()
    return source, target


def test_migration_counts_all_files_and_preserves_other_evidence(tmp_path: Path) -> None:
    source, target = _snapshots(tmp_path)
    manifest = {
        "generated_at": "2026-09-18",
        "included_snapshots": {"microcap_repair_files": 1, "index_research_files": 12},
        "evidence": {"status": "incomplete"},
    }
    (target / "manifest.json").write_text(json.dumps(manifest))
    migration.main(["--source-root", str(source), "--target-root", str(target)])
    updated = json.loads((target / "manifest.json").read_text())
    assert updated["included_snapshots"] == {
        "microcap_repair_files": 1,
        "index_research_files": 22,
        "raw_data_published": False,
    }
    assert updated["generated_at"] == "2026-09-18"
    assert updated["evidence"] == {"status": "incomplete"}
    assert len([path for path in (target / "index").rglob("*") if path.is_file()]) == 22


@pytest.mark.parametrize("manifest", ["not json", "[]", '{"included_snapshots": []}'])
def test_invalid_manifest_fails_before_copying(tmp_path: Path, manifest: str) -> None:
    source, target = _snapshots(tmp_path)
    (target / "manifest.json").write_text(manifest)
    with pytest.raises((ValueError, SystemExit)):
        migration.main(["--source-root", str(source), "--target-root", str(target)])
    assert not (target / "index").exists()


def test_source_argument_is_required(capsys) -> None:
    with pytest.raises(SystemExit) as error:
        migration.main([])
    assert error.value.code == 2
    assert "--source-root" in capsys.readouterr().err
