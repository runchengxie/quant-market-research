"""Run a bounded, read-only SQL file with the configured Databricks CLI identity."""

import argparse
import json
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--warehouse-id", required=True)
parser.add_argument("--sql", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
parser.add_argument("--timeout-seconds", type=int, default=300)
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
if args.output_dir.resolve().is_relative_to(repo):
    parser.error("Results must be outside the repository")
if not 10 <= args.timeout_seconds <= 600:
    parser.error("Timeout must be between 10 and 600 seconds")
statement = args.sql.read_text()
if not statement.lstrip().upper().startswith(("SELECT ", "WITH ")):
    parser.error("Only reviewed SELECT/WITH query files are supported")
args.output_dir.mkdir(parents=True, exist_ok=True)
name = args.sql.stem
output = args.output_dir / f"{name}.json"
if output.exists():
    parser.error("Use a new task output directory; existing evidence is not overwritten")
(args.output_dir / f"{name}.sql").write_text(statement)
payload = {
    "warehouse_id": args.warehouse_id,
    "statement": statement,
    "wait_timeout": "10s",
    "on_wait_timeout": "CONTINUE",
    "row_limit": 500,
    "byte_limit": 2000000,
}


def api(method, endpoint, body=None):
    command = ["databricks", "api", method, endpoint]
    if body is not None:
        command += ["--json", json.dumps(body)]
    return json.loads(subprocess.check_output(command))


response = api("post", "/api/2.0/sql/statements", payload)
output.write_text(json.dumps(response, indent=2))
endpoint = "/api/2.0/sql/statements/" + response["statement_id"]
started = time.monotonic()
while response["status"]["state"] in ("PENDING", "RUNNING"):
    if time.monotonic() - started > args.timeout_seconds:
        api("post", endpoint + "/cancel", {})
        raise TimeoutError(f"Query timeout; cancellation requested, inspect {output}")
    time.sleep(5)
    response = api("get", endpoint)
    output.write_text(json.dumps(response, indent=2))
print(
    json.dumps(
        {
            "statement_id": response["statement_id"],
            "status": response["status"],
            "rows": response.get("manifest", {}).get("total_row_count"),
        }
    )
)
if response["status"]["state"] != "SUCCEEDED":
    raise RuntimeError("Query failed; exact response retained in the output file")
