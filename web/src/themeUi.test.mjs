import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const [layout, themeToggle, styles, charts] = await Promise.all([
  readFile(new URL("./layouts/SiteLayout.astro", import.meta.url), "utf8"),
  readFile(new URL("./components/react/ThemeToggle.tsx", import.meta.url), "utf8"),
  readFile(new URL("./styles.css", import.meta.url), "utf8"),
  readFile(new URL("./components/ResearchCharts.tsx", import.meta.url), "utf8"),
]);

test("theme is applied before the page paints and can be changed from the shell", () => {
  assert.match(layout, /market-research-theme/);
  assert.match(layout, /document\.documentElement\.dataset\.theme/);
  assert.match(themeToggle, /className="theme-toggle"/);
  assert.match(themeToggle, /persistThemeChoice/);
});

test("dark mode defines semantic palette tokens", () => {
  assert.match(styles, /\[data-theme="dark"\]/);
  assert.match(styles, /--paper:/);
  assert.match(styles, /--chart-grid:/);
  assert.match(styles, /--table-hover:/);
});

test("charts read their axis palette from the active theme", () => {
  assert.match(charts, /readChartTheme/);
  assert.match(charts, /theme\.grid/);
});
