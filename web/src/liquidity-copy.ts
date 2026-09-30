export const liquidityCaveatTranslations: Record<string, string> = {
  "A 股日频数据没有记录被省略的停牌日，因此无法仅凭零成交量频率推断停牌情况。": "The A-share daily data omits suspended trading days, so suspension status cannot be inferred from zero-turnover frequency alone.",
  "这里展示的是机械性的流动性画像，不等同于策略容量或实际执行容量。": "These mechanical liquidity profiles do not establish strategy capacity or executable capacity.",
  "当前历史快照覆盖美国、香港和 A 股；日本仍保留在统一适配器契约中，但目前尚未发布可比的分位桶快照。": "The current historical snapshot covers the US, Hong Kong, and A-shares. Japan remains in the shared adapter contract, but comparable bucket snapshots have not been published.",
};

export function liquidityCaveats(notes: string[], locale: string) {
  return locale === "zh-CN"
    ? notes.join(" ")
    : notes.map((note) => liquidityCaveatTranslations[note] ?? "A research caveat is available in the Chinese source.").join(" ");
}
