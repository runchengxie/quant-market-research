import { spawnSync } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const web = process.cwd();
const root = path.resolve(web, "..");
const npm = process.platform === "win32" ? "npm.cmd" : "npm";
const uv = process.platform === "win32" ? "uv.exe" : "uv";

function run(command, args, cwd) {
  const result = spawnSync(command, args, { cwd, stdio: "inherit" });
  if (result.status !== 0) process.exit(result.status ?? 1);
}

run(npm, ["run", "build"], web);
run(uv, ["run", "--locked", "--extra", "docs", "mkdocs", "build", "--strict"], root);
const dist = path.join(web, "dist");
mkdirSync(dist, { recursive: true });
writeFileSync(path.join(dist, ".nojekyll"), "");
run(npm, ["run", "verify:static"], web);
