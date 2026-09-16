import http from "node:http";
import fs from "node:fs";
import path from "node:path";
const root = path.resolve(process.argv[2] ?? "dist");
const base = "/quant-market-research";
const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".csv": "text/csv; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".woff2": "font/woff2",
};

http.createServer((request, response) => {
  const pathname = new URL(request.url ?? "/", "http://localhost").pathname;
  if (pathname !== base && !pathname.startsWith(`${base}/`)) {
    response.writeHead(404).end("Not found");
    return;
  }
  const relative = decodeURIComponent(pathname.slice(base.length)).replace(/^\/+/, "");
  const target = path.resolve(root, relative || "index.html");
  if (target !== root && !target.startsWith(`${root}${path.sep}`)) {
    response.writeHead(400).end("Bad path");
    return;
  }
  const candidates = [target, path.join(target, "index.html")];
  const file = candidates.find((candidate) => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
  const fallback = file ?? path.join(root, "404.html");
  response.writeHead(file ? 200 : 404, { "content-type": contentTypes[path.extname(fallback)] ?? "application/octet-stream" });
  fs.createReadStream(fallback).pipe(response);
}).listen(Number(process.env.PORT ?? 4321), "127.0.0.1", () => {
  process.stdout.write(`Serving ${root} under ${base}/\n`);
});
