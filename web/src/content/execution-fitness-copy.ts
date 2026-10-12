export const fitnessCopy = {
 finding:['Both dates reproduce the earliest-minute selections with zero mismatches. On 2026-04-16, the original source is missing {missing} minutes across {stocks} sampled stocks; this is not repaired by rerunning the calculation.','两天的每分钟第一条记录都复现一致。但2026年4月16日原始文件中，{stocks}只样本股票缺了{missing}个分钟，重复计算并不能补回这些报价。'],
 title:['What the existing data can support',"这些数字核查到哪一步了"],
 scope:['Two raw snapshot dates are checked against the saved first quote of every sampled minute. Saved event references and fixed-day five-minute paths are reported separately. This is a bounded audit, not a complete warehouse certification.',"这轮核查只覆盖两个日期。先从原文件核对每分钟第一条盘口，再检查逐笔编号和五分钟模拟，没有检查整个数据仓库。"],
 candidates:['Common candidate stocks','共同候选股票'], included:['Included paths','纳入试算的股票'], invalid:['Invalid-book exclusions','盘口无效而排除的股票'], fresh:['Fresh terminal benchmarks','结束时有新报价的股票'],
 source:['Original-file selection and missing records',"哪些报价缺了"],
 sourceNote:['Each raw security/date/clock is rescanned; comparison retains invalid first books. The daily positive-trading-amount universe is a retrospective cross-check, not a historical eligibility master or a supplier completeness certificate.',"每分钟选出的第一条记录与原文件一致。另与同日有成交额的股票比较，寻找完全没有盘口的股票。这份日线名单不能替代完整的历史证券名单。"],
 day:['Date','日期'],selected:['Sampled minute records','抽出的分钟记录'],wrong:['Wrong / missing first records','选错或漏掉的第一条'],missing:['Missing minutes','缺失分钟'],absent:['Daily-traded stocks without raw books','日线有交易但原始盘口缺失的股票'],
 events:['An order number match still needs checking','订单编号对上后，还要查什么'],
 eventNote:['A unique matching key present by the trade is stronger than an arbitrary lookup, but does not verify side, cancel meaning, priority or completeness. Equal timestamps do not establish exchange order. Early keys lack channels. Candidate IDs are tested separately; we never choose the higher rate as proof of the correct field.','找到同名编号后，继续查它是否只出现一次、是否在最早记录的时间是否不晚于成交。重复编号可能来自更新或撤单，尚未弄清含义。同一时间戳内的先后顺序仍不知道。早期记录没有通道字段，不同候选编号分别统计，不把匹配率最高的那个自动当成正确字段。'],
 market:['Market','市场'],shanghai:['Shanghai','沪市'],shenzhen:['Shenzhen','深市'],candidate:['Candidate ID','候选编号字段'],eligible:['Positive-price/quantity trades','价格和数量为正的成交数'],unique:['Unique key available by trade',"唯一编号且时间不晚于成交"],ambiguous:['Repeated key available by trade',"重复编号且时间不晚于成交"],ties:['Same first timestamp','最早时间与成交相同'],
 future:['Key first appears after trade','编号只在成交后出现'],unmatched:['No key found','未找到编号'],
 paths:['Larger same-day execution sensitivity','扩大同日成交试算'],
 pathNote:['The common observed stocks use three share quantities in a fixed opening five-minute window. Each day stays separate. Paths with invalid displayed books are excluded and counted. Arrival quotes later than one minute are excluded and terminal costs need a quote no older than one minute. Share quantities are not equal cash amounts. Snapshot refresh, no own impact, no fees or passive queues remain assumptions; negative shortfall includes market moves.','两天共同出现的股票分别试算1000股、1万股和10万股，每天只用当天开盘后的五分钟。出现无效盘口的整条路径另列排除数量，不悄悄删掉报价。第一条盘口晚于开盘一分钟的样本不纳入，结束时没有一分钟内报价的成本留空。相同股数对应的金额不同，不能直接当作相同资金规模。后续挂单按快照刷新，未计税费、排队和自身订单影响；负成本也包含行情涨跌。'],
 quantity:['Shares','股数'],side:['Side','方向'],buy:['Buy','买入'],sell:['Sell','卖出'],mode:['Mode','方式'],marketMode:['Immediate displayed-depth sweep','立即按挂单成交'],twap:['Fixed-clock equal slices','按分钟等量分批'],limit_wait:['Marketable limit crossings','限价等待可直接成交'],total:['Paths','样本数'],filled:['Fully completed','全部完成'],costCount:['Cost observations','能算出成本的样本'],median:['Median shortfall (bp)','成本中位数（基点）'],
 details:['Open all measured values','展开完整测量结果'],
 next:['What still blocks stronger conclusions','还缺什么才能往前走'],
 nextNote:['These checks cannot establish real slippage. Vendor event definitions and cross-stream exchange order are still needed for full book reconstruction; actual order and fee records are needed for calibration. Missing securities require historical status and supplier coverage records.','这些检查还不能测出真实滑点。完整还原订单簿还缺供应商事件说明和跨文件交易所顺序。真实订单及收费记录用于校准，历史证券状态和供应商覆盖说明用于解释缺失股票。'],
 report:['Methods and reproducible findings ↗','查看方法与复现结果 ↗'],download:['Download reviewed aggregate checks','下载已复核的汇总检查'],
} as const;

export const flatCostCopy = {
 title:['How to interpret a 0.4% flat trading cost','回测里的0.4%该怎么理解'],
 note:['0.4% equals 40 bp. If it is the total all-in cost, do not add the same fees or slippage again. It is higher than the 100,000-yuan static median in this selected sample, but cannot guarantee coverage of large orders, waiting or missing fills. A 0.4% round-trip cost corresponds to 20 bp per side only under a symmetric split.','0.4%等于40基点。如果它已经包含全部交易费用，就不要再加一次佣金或滑点。它高于本样本10万元订单的静态成本中位数，可以用来做较严格的压力测试，但不能保证覆盖大订单、等待和未成交损失。一买一卖合计0.4%，只有在两侧平均分摊时才相当于每侧20基点。'],
 side:['40 bp on each buy and sell','买入、卖出每侧各40基点'],round:['40 bp round trip, split equally','买卖合计40基点，两侧均分'],
 cost:['Flat all-in assumption','全部费用假设'],linear:['Linear annual expense','线性年度支出比例'],
 warning:['At 250 sessions with buying and selling each 60% of NAV daily, linear expenses are 120% or 60%. This sums expenditure at constant capital; it is not a realized NAV loss or a compounded return. These flat assumptions are stress scenarios, not calibrated cost estimates.','按一年250天、每天买卖各占净值60%计算，线性支出分别为120%和60%。这是资金规模固定时累计花了多少钱，不是实际净值损失，也不是复利回报。这两档是假设的压力情景，还没有用真实订单校准。'],
} as const;
