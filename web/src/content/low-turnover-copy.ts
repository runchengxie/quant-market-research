import reader from '../../public/data/low_turnover_reader.json';
const labels: Record<string, readonly [string,string]> = {
 raw: ['Raw signal', '原始信号'], size: ['Control for size', '控制市值'],
 size_lowvol: ['Add low volatility', '再控制低波动'], plus_beta_value: ['Full listed controls', '加入其余控制'],
};
export const lowTurnoverEvidence = reader;
export const lowTurnoverControls = reader.controls.map(row => ({...row,label:labels[row.id]}));

const raw = lowTurnoverControls[0].spread.toFixed(2);
const full = lowTurnoverControls[3].spread.toFixed(2);

export const lowTurnoverCopy = {
  title: ['Low-turnover stocks and subsequent returns', '低换手股票后来表现怎样'],
  description: ['Historical group comparisons, sample limits and trading simulations for low-turnover stocks.', '低换手股票的历史分组比较、样本限制与模拟交易结果。'],
  kicker: ['Factors and style · exploratory research', '因子与风格 · 探索性研究'],
  introduction: ['The main signal averages daily share turnover over the 60 trading sessions before selection, excluding the selection date. This page compares subsequent returns and checks what changes after accounting for other stock characteristics.', '主信号采用选股日前 60 个交易日的平均换手率，不含选股当天。这里比较换手较低与较高的股票后来表现怎样，再看加入其他股票特征后，差距有何变化。'],
  status: ['Exploratory evidence', '探索性证据'],
  findings: ['Current findings', '目前的发现'],
  conclusion: ['The historical return gap is positive. Reliable trading gains remain unverified.', '历史分组差距为正，实际交易能赚多少仍待验证。'],
  lead: [`In this historical sample, the low-turnover group averaged ${raw} percentage points more per month than the high-turnover group. After accounting for the full listed controls and regrouping on the adjusted score, the gap was about ${full} points. These are group comparisons. A consistent trading test is still needed to establish after-cost portfolio performance.`, `这轮历史比较中，低换手组的月均收益比高换手组高约 ${raw} 个百分点。加入市值和波动等控制、按调整后的信号重新分组后，完整控制版本的差值约为 ${full} 个百分点。实际持仓能获得多少收益，还需要用一致的交易规则验证。`],
  scope: ['The 86 selection dates run from May 2019 through June 2026, with holding periods from June 2019 through July 2026. The common sample requires positive PE and usable control data. It does not represent every A-share stock. This history has been examined repeatedly.', '这 86 期名单形成于 2019 年 5 月至 2026 年 6 月，对应持有期从 2019 年 6 月延续到 2026 年 7 月。共同样本要求市盈率为正，控制变量也须有可用数据，不能代表全部 A 股。这段历史已经被多轮研究查看。'],
  date: ['Evidence snapshot · 16 September 2026. Content and source hashes checked · 22 October 2026. This edit adds no new observation months.', '证据快照截至 2026 年 9 月 16 日，文字与来源哈希于 2026 年 10 月 22 日复核。本次修订没有增加新的观察月份。'],
  common: ['Common sample', '共同样本'], months: ['86 selection months', '86 期选股名单'],
  formation: ['Selected May 2019 to June 2026', '选股日期为 2019 年 5 月至 2026 年 6 月'],
  raw: ['Raw low minus high', '原始分组差值'], full: ['Full listed controls', '完整控制后的差值'],
  spreadUnit: ['Mean monthly gap · percentage points', '月均收益差，单位为百分点'],
  observed: ['Archived later observation', '归档的后续观察'], oneMonth: ['1 completed window', '1 个已完成窗口'],
  registration: ['Pre-period registration evidence remains incomplete', '仍缺持有期开始前的登记证据'],
  controls: ['Controls and group comparisons', '加入其他特征后，差距怎样变化'],
  controlsLead: ['Every row uses the same 86 selection months. Controls are applied sequentially, then stocks are ranked again on the remaining signal and divided into ten groups. The low and high labels refer to the two ends of that adjusted score. Membership changes between rows.', '各行使用同样的 86 期选股日期。每一步先用已列特征调整信号，再按剩余信号重新排序，分成十组。控制后的两端对应调整后得分最高与最低的组，名单会变化，未必仍是原始换手率最低与最高的股票。'],
  controlsList: ['The final row includes size, low volatility, trading activity, Amihud illiquidity, momentum, reversal, beta and valuation. Amihud illiquidity compares absolute price moves with traded value as a rough indicator of how strongly prices move for a given trading amount.', '最后一行纳入市值、低波动、成交活跃度、Amihud 流动性指标、动量、反转、贝塔和估值。Amihud 指标用价格涨跌幅绝对值与成交额作比较，粗略描述一定成交金额对应多大的价格变化。'],
  chart: ['Average monthly return gap and its 95% range', '月均收益差及其 95% 估算范围'],
  range: ['95% estimated range', '95% 估算范围'], between: [' to ', ' 至 '],
  low: ['Low-turnover end', '低换手得分端'], high: ['High-turnover end', '高换手得分端'],
  uncertainty: ['Dots show mean gaps in percentage points. Lines show 95% block-bootstrap intervals, resampling 12-month blocks 2,000 times so adjacent months can move together. They describe uncertainty within this history and do not account for every specification tried during the research.', '圆点表示月均差值，单位为百分点。线段是以连续 12 个月为一块、重抽 2,000 次得到的 95% 区间，保留相邻月份一起变化的影响。它只描述这段历史中的估算不确定性，没有覆盖整个研究过程尝试过的全部方案。'],
  controlsLimit: ['Sequential controls compare conditional relationships. Correlated features and changing memberships prevent the row differences from identifying one feature’s causal contribution. The plotted group returns do not include a complete execution or borrowing model.', '逐步加入特征后得到的是有条件的历史比较。特征之间相关，组内名单也会变化，行与行的差值不能算作某个特征单独造成的收益。图中的分组收益尚未计入完整的成交与融券模型。'],
  regression: ['A separate joint cross-sectional regression estimates about 0.60 percentage points more next-period return per one-standard-deviation higher low-turnover score. The coefficient is positive in 76.7% of the 86 months. This conditional historical relationship does not establish a causal effect or an executable return.', '另一项联合截面回归中，低换手得分每高一个标准差，下一期收益平均高约 0.60 个百分点，86 期中有 76.7% 的系数为正。这是给定其他特征后的历史关系，尚不足以判断因果作用或实际交易收益。'],
  interpretation: ['What might explain the difference?', '这些差距可能与什么有关'],
  interpretationLead: ['The historical comparisons leave several explanations open. The study has not separated their causal effects.', '历史比较还没有分清各种特征各自的作用，下面保留的是需要继续核对的解释。'],
  volatility: ['Lower volatility', '较低的价格波动'],
  volatilityText: ['Adding low volatility narrows this sample’s gap from 1.63 to 0.86 percentage points. Both the score and group membership change, so the decline cannot be assigned entirely to volatility.', '加入低波动后，这批样本的差值从约 1.63 缩小到 0.86 个百分点。信号和名单同时改变，这个变化还不能全部归因于波动。'],
  activity: ['Trading activity and liquidity', '交易活跃度与流动性'],
  activityText: ['Share turnover, traded value and price response measure related aspects of trading. Their controls change which stocks rank at each end. A positive remaining gap does not identify a separate economic mechanism.', '换手率、成交额和价格对成交的反应有联系。加入这些变量后，两端名单会改变。剩余差值为正，还不能证明某一种独立的经济机制。'],
  legs: ['Check both groups separately', '把两端收益分别看清'],
  legsText: ['The current raw groups average +1.08% and −0.30% per month. Earlier samples have different leg contributions. The present comparisons do not establish that avoiding crowding or speculation causes the gap.', '当前原始分组的月均收益分别约为 1.08% 和负 0.30%。早期样本中两端的贡献不同，不能直接套用。拥挤或投机是否造成差距，仍需要专门检验。'],
  limitations: ['What still limits the result?', '哪些问题仍影响判断'],
  sampleLimit: ['The signal is an average daily share-turnover rate. Portfolio turnover later on this page measures the portfolio’s own trading. A stock with low share turnover need not be cheap or easy to trade.', '这里的换手率是股票每天成交股份占相应股份数的比例。后文的组合换手衡量组合自己买卖了多少，两者含义不同。股票换手低，也不能保证买卖成本低或容易成交。'],
  historyLimit: ['The revised ranking fixes membership before checking future return availability. Missing future prices still limit which outcomes can be observed. Historical revisions and reconstructed stock eligibility remain unresolved, and the repeatedly examined 2024–2026 history is not an untouched test set.', '修正版先按选股日信号固定分组，再检查未来收益是否可用。未来缺价仍会限制能观察哪些结果。历史数据修订和证券资格重建也未完全核实，反复查看过的 2024 年至 2026 年历史不能充当未接触的检验样本。'],
  forwardLimit: ['The archive dated 16 September 2026 contains one completed August window and one pending window. Its manifest names a July cutoff but references a September data product. This does not by itself establish registration before the August holding period. Retain it as a later observation until a verifiable pre-period registration record is recovered.', '2026 年 9 月 16 日的归档包含一个已完成的八月窗口和一个待完成窗口。清单写有七月底的数据截止日，同时引用九月的数据产物。现有记录还不足以证明八月持有期开始前已经登记，补齐可核验的事前记录前，暂按后续观察保留。'],
  tradingLimit: ['Theoretical long-short spreads and net long-only simulations use different portfolio directions and accounting rules. Their difference cannot measure execution costs. A matched test must keep the signal, universe and period fixed while changing only the execution assumption.', '理论多空差值和扣成本多头模拟采用不同的组合方向与记账规则，两者相减不能衡量执行成本。检验成交约束的影响，需要固定同一信号、股票池和期间，只改变成交假设。'],
  next: ['What to test next', '下一步怎样检验'],
  nextTitle: ['Does adding the rule improve a comparable portfolio?', '加入低换手规则，能否改善同条件的组合'],
  nextText: ['Use one universe, ledger and cost model to compare a benchmark with portfolios that exclude the highest-turnover group or favor low turnover. The existing 5.46% versus 5.33% annualized comparison already tried one exclusion rule and found only a small difference. Future tests need timestamped registration before holdings begin and a record of every specification tried.', '用同一股票池、账本和成本模型，比较基准组合与加入低换手条件后的组合。剔除最高换手组的旧测试已得到约 5.46% 与 5.33% 的净年化，差异很小，详细记录保留在方法文档。后续检验要在持有期开始前登记并保留时间证据，同时记录尝试过的方案。'],
  versions: ['Result version and earlier records', '结果版本与较早记录'],
  versionNote: ['This page uses the reviewed formation-first ranking revision. Earlier figures remain in the methodology as labeled historical records. Source hashes below identify this version; they do not certify revision-safe financial histories.', '本页采用先固定选股日分组的已核对修正版。旧数字在方法文档中标为历史记录保留。下列来源哈希用于识别版本，不能单独证明财务历史已排除事后修订。'],
  manifest: ['Source manifest SHA-256', '来源清单 SHA-256'], summary: ['Effect summary SHA-256', '收益汇总 SHA-256'],
  method: ['Read the full methodology ↗', '阅读完整方法说明 ↗'], style: ['View 18-year style-factor research ↗', '查看 18 年风格因子 ↗'],
} as const;
