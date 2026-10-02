# Migrating reviewed index snapshots

The legacy snapshot copier is a migration utility, outside the current refresh
and publication flow. It accepts only the fixed index snapshot file family; an
operator must review the derived public contents before running it. It does not
sanitize raw vendor data or private strategy outputs.

```bash
python scripts/sync_public_research_data.py --source-root /path/to/reviewed-index-outputs
```

The required source directory replaces the retired machine-specific
index-research checkout. `--target-root` optionally selects a public snapshot
directory containing `manifest.json`; its default is `web/public/data`.

The utility reads the manifest and checks its snapshot-count object before
copying. It preflights all 22 required source files so a missing file causes no
copies. A successful migration records the actual file count, retains unrelated
snapshot counts, and preserves the existing evidence and refresh receipts.
It does not fabricate a new verification date or upgrade evidence status.

This is not a transaction across files: an I/O error during copying can still
leave some files replaced. Keep a recoverable target and review the resulting
diff before publication. No source snapshots were migrated as part of this
code change.

The [local runbook](runbook-local.md) contains the Chinese operational reference.
