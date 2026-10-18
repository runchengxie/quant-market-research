"""Exact feature-row revision comparisons, with new dates separated from backfills."""

from __future__ import annotations

from .liquidity_rebuild import _identifier


def compare_features(con, baseline: str, candidate: str) -> dict:
    b, a = map(_identifier, (baseline, candidate))
    schemas = [con.execute(f"DESCRIBE {t}").fetchall() for t in [b, a]]
    if [(r[0], r[1]) for r in schemas[0]] != [(r[0], r[1]) for r in schemas[1]]:
        raise ValueError("feature schema drift requires review")
    keys = ["market", "symbol", "date"]
    columns = [r[0] for r in schemas[0]]
    if not set(keys) <= set(columns):
        raise ValueError("feature schema lacks keys")

    def quote(x):
        return '"' + x.replace('"', '""') + '"'

    profiles = []
    for t in [b, a]:
        if con.execute(
            f"SELECT count(*) FROM {t} WHERE market IS NULL OR symbol IS NULL OR date IS NULL"
        ).fetchone()[0]:
            raise ValueError("null feature keys")
        if con.execute(
            f"SELECT count(*) FROM (SELECT market,symbol,date FROM {t} GROUP BY ALL HAVING count(*)>1)"
        ).fetchone()[0]:
            raise ValueError("duplicate feature keys")
        floats = [quote(r[0]) for r in schemas[0] if r[1] in ("DOUBLE", "FLOAT")]
        if (
            floats
            and con.execute(
                f"SELECT count(*) FROM {t} WHERE "
                + " OR ".join(f"({c} IS NOT NULL AND NOT isfinite({c}))" for c in floats)
            ).fetchone()[0]
        ):
            raise ValueError("nonfinite feature values")
        n, d0, d1 = con.execute(f"SELECT count(*),min(date),max(date) FROM {t}").fetchone()
        if not n:
            raise ValueError("empty feature input")
        profiles.append(dict(rows=n, start=str(d0), end=str(d1)))
    values = [c for c in columns if c not in keys]
    change = " OR ".join(f"b.{quote(c)} IS DISTINCT FROM a.{quote(c)}" for c in values) or "false"
    row = con.execute(f"""SELECT
      count(*) FILTER(WHERE b.symbol IS NOT NULL AND a.symbol IS NOT NULL AND ({change})),
      count(*) FILTER(WHERE a.symbol IS NULL),
      count(*) FILTER(WHERE b.symbol IS NULL AND a.date<=(SELECT max(date) FROM {b})),
      count(*) FILTER(WHERE b.symbol IS NULL AND a.date>(SELECT max(date) FROM {b}))
      FROM {b} b FULL OUTER JOIN {a} a USING(market,symbol,date)""").fetchone()
    result = dict(
        zip(["changed_rows", "removed_rows", "historical_added_rows", "new_date_rows"], row)
    )
    result.update(
        baseline=profiles[0],
        candidate=profiles[1],
        status=("review_required" if any(row[:3]) else "append_only" if row[3] else "unchanged"),
    )
    return result


def validate_replacement(previous: dict, proposed: dict, report: dict | None) -> None:
    """Require revision evidence when replacing the published SH/SZ feature version.

    Initial publications and unchanged feature bytes retain the existing review
    flow. A historical rewrite is not an automatic append-only update.
    """

    def feature(summary):
        return next(
            (
                r["sha256"]
                for r in summary.get("source_receipts", [])
                if r["source_id"] == "a_sh_sz_features"
            ),
            None,
        )

    old, new = feature(previous), feature(proposed)
    if old is None or old == new:
        return
    if not report or report.get("schema_version") != "liquidity.feature-revision.v1":
        raise ValueError("changed SH/SZ features require a revision receipt")
    if report.get("sha256") != {"baseline": old, "candidate": new}:
        raise ValueError("revision receipt version binding does not match publication")
    if report.get("status") not in ["unchanged", "append_only"] or any(
        report.get(k) != 0 for k in ["changed_rows", "removed_rows", "historical_added_rows"]
    ):
        raise ValueError("historical revisions require investigation before replacement")
