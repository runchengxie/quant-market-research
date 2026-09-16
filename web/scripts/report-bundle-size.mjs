import fs from "node:fs";
import path from "node:path";

const dist = path.resolve(process.argv[2] ?? "dist");
const files = [];
function walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(file);
    else if (/\.(?:js|css|html)$/.test(entry.name)) files.push(file);
  }
}
walk(dist);
const rows = files.map((file) => ({ file: path.relative(dist, file), bytes: fs.statSync(file).size }))
  .sort((left, right) => right.bytes - left.bytes);
const total = rows.reduce((sum, row) => sum + row.bytes, 0);
console.log(`静态产物总大小：${(total / 1024).toFixed(1)} KiB`);
for (const row of rows.slice(0, 10)) console.log(`${String(row.bytes).padStart(9)} B  ${row.file}`);
