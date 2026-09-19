export type ResourceSnapshot<T> = { data: T | null; error: string; loading: boolean };

export function parseJsonResource<T = unknown>(text: string): T {
  return JSON.parse(text.replace(/^\uFEFF/, "")) as T;
}

// Structural CSV validation only: no assumptions about domain column names.
export function parseCsvResource(text: string): Record<string, string>[] {
  text = text.replace(/^\uFEFF/, "");
  if (!text.trim()) return [];
  if (/^\s*</.test(text)) throw new Error("CSV 返回了 HTML，无法读取研究数据");
  const rows: string[][] = [];
  let row: string[] = [], cell = "", quoted = false, closed = false;
  const finishRow = () => {
    row.push(cell);
    if (row.some(value => value.trim() !== "") || row.length > 1) rows.push(row);
    row = []; cell = ""; closed = false;
  };
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (quoted) {
      if (char !== '"') cell += char;
      else if (text[i + 1] === '"') { cell += '"'; i++; }
      else { quoted = false; closed = true; }
    } else if (char === ",") { row.push(cell); cell = ""; closed = false; }
    else if (char === "\n" || char === "\r") {
      if (char === "\r" && text[i + 1] === "\n") i++;
      finishRow();
    } else if (char === '"' && !cell && !closed) quoted = true;
    else {
      if (closed || char === '"') throw new Error("CSV 引号格式无效");
      cell += char;
    }
  }
  if (quoted) throw new Error("CSV 引号未闭合");
  if (cell || row.length || closed) finishRow();
  const headers = rows.shift() ?? [];
  if (headers.some(header => !header.trim()) || new Set(headers).size !== headers.length) throw new Error("CSV 列名为空或重复");
  return rows.map(values => {
    if (values.length !== headers.length) throw new Error("CSV 数据列数与表头不一致");
    return Object.fromEntries(headers.map((header, i) => [header, values[i]]));
  });
}

/** One resource per hook/path; retries preserve its last successful value. */
export function createResource<T>(url: string | null, parse: (text: string) => T, fetcher: typeof fetch = (...args) => fetch(...args)) {
  let snapshot: ResourceSnapshot<T> = { data: null, error: "", loading: url !== null };
  const initial = snapshot;
  const listeners = new Set<() => void>();
  let generation = 0;
  let controller: AbortController | undefined;
  let timer: ReturnType<typeof setTimeout> | undefined;
  const publish = (next: ResourceSnapshot<T>) => { snapshot = next; listeners.forEach(listener => listener()); };
  const cancel = () => {
    generation++;
    clearTimeout(timer);
    controller?.abort();
  };
  const load = () => {
    cancel();
    if (url === null) return;
    const request = generation;
    const abort = new AbortController();
    controller = abort;
    publish({ data: snapshot.data, error: "", loading: true });
    // Publish directly on timeout: even a fetch/body implementation ignoring
    // AbortSignal must leave the loading state. Generation guards late results.
    timer = setTimeout(() => {
      if (request !== generation) return;
      cancel();
      publish({ data: snapshot.data, error: `${url}：请求超时（15 秒），请重试`, loading: false });
    }, 15_000);
    void (async () => {
      try {
        const response = await fetcher(url, { signal: abort.signal });
        if (!response.ok) throw new Error(`${url}（${response.status}）`);
        const value = parse(await response.text());
        if (request === generation) publish({ data: value, error: "", loading: false });
      } catch (reason) {
        if (request === generation) publish({ data: snapshot.data, error: reason instanceof Error ? reason.message : String(reason), loading: false });
      } finally {
        if (request === generation) clearTimeout(timer);
      }
    })();
  };
  return {
    getSnapshot: () => snapshot,
    getServerSnapshot: () => initial,
    subscribe: (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener); }; },
    load, cancel,
  };
}
