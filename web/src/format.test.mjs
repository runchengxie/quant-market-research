import test from "node:test";
import assert from "node:assert/strict";
import { asNumber, displayValue, formatNumber, formatPercent } from "./lib/format.ts";

test("English display formatters preserve missing data and render common labels", () => {
  assert.equal(formatPercent(0.12345), "12.3%");
  assert.equal(formatPercent(null), "Not reported");
  assert.equal(formatNumber("1234.567"), "1,234.57");
  assert.equal(formatNumber(""), "Not reported");
  assert.equal(asNumber("0"), 0);
  assert.ok(Number.isNaN(asNumber(undefined)));
  assert.equal(displayValue("basis", "gross_total_return"), "Gross total return");
  assert.equal(displayValue("basis", "N/A"), "Not reported");
  assert.equal(displayValue("unknown", "new_label"), "new_label");
});

test("Chinese display formatters retain the translated companion presentation", () => {
  const previousDocument = globalThis.document;
  globalThis.document = {documentElement: {lang: "zh-CN"}};
  try {
    assert.equal(formatPercent(null), "未提供");
    assert.equal(formatNumber(""), "未提供");
    assert.equal(displayValue("basis", "gross_total_return"), "税前全收益");
    assert.equal(displayValue("basis", "N/A"), "未提供");
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
  }
});
