export const liquidityCaveatTranslations: Record<string, string> = {
  "A股仅含沪深，排除北交所和已确认的前身代码；本地日线始于2015年，跨市场比较从2020年起。": "A-shares cover SH/SZ only; BSE and confirmed predecessor codes are excluded. Local daily data starts in 2015 and shared cross-market comparisons start in 2020.",
  "日股市值使用Yahoo历史股数侧表，覆盖不完整且未证明历史修订安全，只作探索性比较。": "Japanese market values use an exploratory Yahoo historical-share sidecar with incomplete coverage and unverified revision safety.",
  "共同日期只统一观察时间，不会消除各来源证券范围、估值和状态记录的差异。": "Common dates align observation time, but do not remove differences in source universes, valuations or status histories.",
  "本结果是可复算的回顾性流动性描述，不是策略容量、真实成交或历史PIT证明。": "These reproducible retrospective profiles establish neither portfolio capacity, actual fills nor historical point-in-time validity.",
  "A 股日频数据没有记录被省略的停牌日，因此无法仅凭零成交量频率推断停牌情况。": "The A-share daily data omits suspended trading days, so suspension status cannot be inferred from zero-turnover frequency alone.",
  "这里展示的是机械性的流动性画像，不等同于策略容量或实际执行容量。": "These mechanical liquidity profiles do not establish strategy capacity or executable capacity.",
  "当前历史快照覆盖美国、香港和 A 股；日本仍保留在统一适配器契约中，但目前尚未发布可比的分位桶快照。": "The current historical snapshot covers the US, Hong Kong, and A-shares. Japan remains in the shared adapter contract, but comparable bucket snapshots have not been published.",
};

const chineseCaveats: Record<string, string> = {
  "A股仅含沪深，排除北交所和已确认的前身代码；本地日线始于2015年，跨市场比较从2020年起。": "A股样本包括沪深股票，北交所和已确认的前身代码另行排除。本地日线从2015年开始，跨市场比较从2020年起。",
  "日股市值使用Yahoo历史股数侧表，覆盖不完整且未证明历史修订安全，只作探索性比较。": "日股市值借助Yahoo历史股数估算，目前只适合探索。覆盖仍不完整，能否还原当时版本也需要核查。",
  "共同日期只统一观察时间，不会消除各来源证券范围、估值和状态记录的差异。": "各市场按共同日期观察，证券范围和估值方法仍有差异。状态记录也要按来源分别核对。",
  "本结果是可复算的回顾性流动性描述，不是策略容量、真实成交或历史PIT证明。": "这些结果描述已观察的流动性。策略容量和真实成交需要另做检验，历史时点资料也还需核查。",
};

export function liquidityCaveats(notes: string[], locale: string) {
  return locale === "zh-CN"
    ? notes.map(note => chineseCaveats[note] ?? note).join(" ")
    : notes.map((note) => liquidityCaveatTranslations[note] ?? "A research caveat is available in the Chinese source.").join(" ");
}
