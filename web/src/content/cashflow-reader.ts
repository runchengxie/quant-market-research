import type { Copy } from './research-reading';
// Reading copy only. Reviewed source assets and their hashes remain unchanged.
const projection: Record<string, Copy> = {
  "现金流指数：规则复现与策略边界": [
    "Rebuilding cash-flow indices and testing portfolio choices",
    "现金流指数复现到了哪一步"
  ],
  "可用快照校准与影子组合研究回答不同问题。完整公开记录现由本专题维护。": [
    "The report checks daily index movements using available constituent snapshots, then compares research portfolios over 80 monthly intervals. Historical coverage and trading assumptions still need work.",
    "研究先用已有成分名单核对指数每天的涨跌，再用 80 个月度区间比较模拟组合。历史资料和交易假设还有缺口，本页把已取得的结果与待核验事项放在一起。"
  ],
  "本研究对现金流、红利与自建组合做了部分规则复现和聚合回放。官方指数完整复现与生产资格验证尚未完成。": [
    "Some rules and aggregate replays have been reproduced. Complete official-history replication and production qualification remain open.",
    "研究已复现部分规则，也做了组合整体回放。官方指数完整历史仍待复现，实盘使用所需检验也未完成。"
  ],
  "现金流、红利和相关自建组合已有部分规则复现与聚合回放证据，但尚不能视为完整的官方成分复现或生产策略验证。": [
    "The available snapshots support a partial rule replay. Cash-flow, dividend and custom portfolios have aggregate results. Complete official-history replication and production qualification remain open.",
    "研究已用已有成分资料回放部分规则，汇总了现金流、红利和自建组合结果。官方指数完整历史仍待复现，实盘使用所需检验也未完成。"
  ],
  "可用成分快照上的日收益相关性支持规则研究和本地校准，但不等于完整官方成分复现。": [
    "Daily returns track the official series closely within the available snapshot sample. Historical constituent coverage remains incomplete.",
    "已有快照样本中，回放结果与官方日收益变化很接近。历史成分名单还没补齐，结论适用于这部分样本。"
  ],
  "980092、932365 和 000922 需要区分当前研究对象、广义基准和红利基准。": [
    "980092 is the current research index, 932365 is the broad cash-flow reference, and 000922 is the dividend reference. Keep their roles separate.",
    "980092 是当前研究对象，932365 和 000922 分别用于全市场现金流、红利基准对照。比较时要写清用了哪个指数。"
  ],
  "后续仍需核对历史规则变化、点时财报覆盖、规模/行业/估值/质量归因和统一交易成本。": [
    "Further work needs rule changes and financial reports available at each historical date, attribution to size, industry, valuation and quality, and a common cost model.",
    "后续要补历史规则变更和当时已公开的财报，还要核对市值、行业、估值与质量带来的影响，并用同一套成本假设比较。"
  ],
  "可用成分快照不覆盖完整十年官方历史成分和规则变更。": [
    "The full ten-year history of official constituents and methodology is incomplete.",
    "十年官方成分名单和规则历史仍有缺口。"
  ],
  "公开投影只保留聚合结果，不代表逐股票信号、组合权重或可成交回放。": [
    "The public record contains aggregate results only. It excludes stock-level signals, portfolio weights and execution details.",
    "公开记录只提供组合汇总结果，不提供逐只股票的信号、组合权重和可执行成交回放。"
  ],
  "尚未据此进入生产策略或形成完整样本外结论。": [
    "Production qualification and full out-of-sample validation remain incomplete.",
    "实盘使用所需检验和完整样本外检验尚未完成。样本外检验要用未参与规则选择的数据。"
  ],
  "可用成分快照覆盖期；完整十年官方成分回放尚未完成": [
    "The replay uses available constituent snapshots. The full ten-year official history remains incomplete.",
    "回放覆盖已有成分快照对应的区间。完整十年官方历史仍待补齐。"
  ],
  "规则校准与影子策略研究回答不同问题。": [
    "The four steps below track what was checked and how far each result reaches.",
    "下面四步保留每次核对的问题、结果和当时判断。"
  ],
  "对照官方日收益校准": [
    "Check the daily movements",
    "先核对每天的涨跌"
  ],
  "现有成分快照能否复现日收益变化？": [
    "Can available constituent snapshots reproduce daily returns?",
    "用已有成分名单回放，日收益能贴近官方结果吗？"
  ],
  "现有快照回放相关性为红利 0.997、全市场自由现金流 0.992。": [
    "Snapshot replay correlations are 0.997 for the dividend benchmark and 0.992 for broad free cash flow.",
    "红利基准的日收益相关系数为 0.997，全市场自由现金流基准为 0.992。"
  ],
  "用于局部校准，不代表补齐缺失的历史成分。": [
    "Use the result to check this sample. Missing historical constituents still need to be recovered.",
    "这部分样本可用于核对回放方法。缺失的历史成分仍要补齐。"
  ],
  "比较影子历史中的持仓宽度": [
    "Compare how many stocks to hold",
    "再比较持有多少只股票"
  ],
  "更集中是否一致改善结果？": [
    "Does a more concentrated portfolio consistently produce higher returns?",
    "少持有几只股票，收益就会一直更高吗？"
  ],
  "标准影子回放随持仓宽度、权重变化，收益曲线并非单调。": [
    "Results change with both holding count and weighting. Returns do not rise or fall consistently as the count changes.",
    "持仓数量和分配权重都会影响收益。股票从 10 只增加到 100 只时，两种权重方式的收益变化并不一致。"
  ],
  "不能看完本表再选择最优持仓宽度。": [
    "Choose holding-count rules before testing on fresh data. Selecting the highest entry after inspecting this table would use the result to choose the rule.",
    "持仓数量应在新样本检验前确定。看完这张表再挑最高收益，会把已看到的结果用来选规则。"
  ],
  "研究缓冲与成本": [
    "Check turnover and trading costs",
    "接着看调仓和成本"
  ],
  "能否区分降低换手与 Alpha？": [
    "Does keeping some existing holdings reduce trading, and is extra return independently established?",
    "暂留部分老持仓能少交易多少？额外收益经过独立验证了吗？"
  ],
  "老持仓缓冲降低了换手；成本阶梯中各臂收益均随成本上升而降低。": [
    "The source reports lower turnover with buffering. Every cost-stress variant earned less as assumed costs rose.",
    "研究记录显示，暂留部分老持仓降低了换手。成本压力测试中，所有方案都随着假设成本上升而少赚。"
  ],
  "视为组合构造与成本敏感性，不称官方指数复现或容量结论。": [
    "These results describe portfolio construction and cost sensitivity. Official replication and tradable capacity still need separate checks.",
    "这些结果用于了解持仓安排和成本影响。官方指数完整复现、资金能容纳多少，都还需要各自核验。"
  ],
  "区分官方历史成分与权重": [
    "Check which official records are available",
    "最后核对官方资料覆盖到哪里"
  ],
  "现已取得官方指数历史中的哪部分资料？": [
    "Which parts of official index history are available?",
    "官方历史资料已经拿到了哪些？"
  ],
  "官方 980092 调整导出覆盖自 2024-09-18 起的 9 个区间，每个区间含 100 个成分。文件提供成分变更，但没有历史权重；官方权重导出仅提供 2026-09-30 快照。": [
    "The 980092 adjustment export covers nine intervals from 2024-09-18, with 100 constituents in each interval and no historical weights. The weight export contains only the 2026-09-30 snapshot.",
    "980092 官方调整文件包含自 2024 年 9 月 18 日起的 9 个区间，每个区间有 100 只成分股。文件记录了成分变更，缺少历史权重。官方权重文件只有 2026 年 9 月 30 日这一个快照。"
  ],
  "现行方法自 2024-08-15 生效，但导出未覆盖该日至 2024-09-17 的成分。历史权重仍缺失。这不代表完成十年官方指数复现；此前快照相关性和影子组合比较应单独呈现。": [
    "The current method took effect on 2024-08-15. Membership is missing through 2024-09-17 and historical weights remain unavailable. The ten-year official replay is incomplete. Earlier snapshot correlations and research portfolios remain separate evidence.",
    "现行方法从 2024 年 8 月 15 日生效，成分资料缺少当天至 9 月 17 日这一段，历史权重也未补齐。十年官方回放仍未完成。已有快照相关系数与模拟组合结果继续分开记录。"
  ],
  "部分早期字段使用代理，逐字段严格 PIT 复核仍待完成。": [
    "Some early fields are proxies; field-level strict PIT review remains open.",
    "部分早期字段用了替代值。每个字段在历史当天是否已经公开，仍要逐项核对。"
  ],
  "引用记录尚未独立完成这一项核查。": [
    "Not independently qualified in the cited record.",
    "引用记录尚未独立核对历史财报版本。需要确认回放使用了当时可取得的版本。"
  ],
  "官方成分快照不完整，历史规则曾变化。": [
    "Official constituent snapshots are partial and historical rules changed.",
    "官方成分快照还不完整，历史规则也改过。每个日期哪些股票符合条件，仍待核对。"
  ],
  "公司行动、股息和临时替换尚未完整复现。": [
    "Corporate actions, dividends and temporary replacements are not fully reproduced.",
    "公司行动、股息和临时替换还未完整回放，退市及终止价格处理也需要核验。"
  ],
  "规则影子与官方指数校准是不同证据。": [
    "Rule-shadow and official-index calibration are separate evidence.",
    "按规则重建的模拟组合与官方日收益核对分开记录。交易时点能否实际执行仍待确认。"
  ],
  "共同可执行成本对照仍待完成。": [
    "A common executable cost comparison remains open.",
    "各方案还需要按同一套可执行交易成本比较。"
  ],
  "来源入口或产物哈希不等于完整复跑认证；原始可得性、依赖和历史资格必须一致。": [
    "A complete rerun must match original input availability, dependencies and historical eligibility. Source links and file hashes cover only part of that verification.",
    "完整复跑要核对原始数据当时能否取得，并核对依赖与历史证券资格。来源入口和文件校验值只覆盖其中一部分。"
  ],
  "标准影子家族与官方成分校准分开记录。": [
    "Research portfolio replays and official constituent calibration are recorded separately.",
    "模拟组合回放与官方成分核对分开记录。"
  ],
  "稳定现金流规则能否通过一致历史规则、PIT 与共同执行假设检验？": [
    "Can the cash-flow rule hold up when historical rules are consistent, inputs were public at each date and execution assumptions match?",
    "如果统一历史规则，只用当时已公开的数据，并采用相同交易假设，现金流规则还能保持稳定吗？"
  ],
  "核实历史规则与成分，再对齐日期、权重与执行成本比较。": [
    "Verify historical rules and constituents first. Then use common dates, weights and execution costs for comparison.",
    "先核实历史规则与成分，再按相同日期、权重和交易成本比较。"
  ],
  "保留不可变审计并解决上述证据缺口；门槛未通过则保留原判断。": [
    "Resolve the named gaps and retain an immutable audit record. Keep the existing research-only decision if qualification fails.",
    "补齐上述缺口后，保留不可修改的核验记录。检验未通过时，继续保留仅供研究的判断。"
  ],
  "较高官方收益相关性可能被理解为完整指数复现。": [
    "The available snapshots showed high correlations with official daily returns. The scope of that result needed to be stated.",
    "已有快照显示，回放与官方日收益相关系数较高。这项结果能支持多大范围的复现，尤其能否支持完整指数历史，需要进一步界定。"
  ],
  "可用快照仍缺历史成分，并存在规则变化。": [
    "Historical constituents are missing and methodology changed over time.",
    "核对资料后，历史成分仍有缺口，规则也曾变化。"
  ],
  "将校准与现行规则影子视为独立且有边界的证据。": [
    "Keep snapshot calibration and current-rule research portfolios as separate results, each with its own limits.",
    "快照核对与按现行规则重建的模拟组合分别记录，各自注明适用范围。"
  ],
  "数据取自量化研究仓库的公开研究入口；官方指数、规则重建影子指数和自建组合分属不同证据类型。": [
    "Data comes from the public research entry in the quantitative research repository. The official index, the rule-reconstructed shadow index, and the self-built portfolio are separate evidence types.",
    "资料取自量化研究仓库的公开研究入口。官方指数数据用于核对日收益，按规则重建的模拟组合和自建组合分别记录，使用时要保留各自范围。"
  ],
  "原发布契约和来源哈希保留于 publication.json；原本缺失的运行哈希仍标为缺失。": [
    "publication.json retains the original publication contract and source hashes. Missing run hashes remain unrecorded.",
    "publication.json 保留原发布约定与来源校验值。缺失的运行校验值继续标为未记录。"
  ],
  "影子收益随持仓宽度变化": [
    "How returns change with holding count",
    "持仓数量变了，收益怎样变化"
  ],
  "影子年化收益": [
    "Annualized research portfolio return",
    "模拟组合年化收益"
  ],
  "980092 标准影子回放，80 个月度区间；混合历史规则与重建数据，不是官方指数历史。": [
    "980092 standard research replay over 80 monthly intervals, using mixed historical rules and reconstructed data. Returns belong to these research portfolios. Official index history is separate and remains incomplete.",
    "980092 标准模拟回放覆盖 80 个月度区间，使用混合历史规则和重建数据。图中收益属于这套研究用模拟组合，官方指数历史单独记录，完整历史仍有缺口。"
  ],
  "权重与持仓宽度相互影响，没有单调赢家或生产资格。": [
    "Equal weight leads at 10, 50 and 100 holdings. Capped cash-flow weighting leads at 20 and 30. Fresh-data tests and production qualification remain open.",
    "10 只、50 只和 100 只时，等权方案收益较高。20 只和 30 只时，现金流封顶方案较高。选定规则后还要用新样本检验，实盘使用所需检验也未完成。"
  ],
  "持仓缓冲换手诊断": [
    "How turnover changes with holding count",
    "暂留老持仓后，换手率怎样变化"
  ],
  "平均单边换手": [
    "Average one-way turnover",
    "平均单边换手率"
  ],
  "同一等权标准影子家族，使用老持仓缓冲；此图没有绘制无缓冲对照。": [
    "The same equal-weight research family retains some existing holdings to reduce replacements. Only buffered results are shown. A matching unbuffered series is unavailable here.",
    "这一组等权模拟组合允许暂留部分老持仓，以减少换股。图中只展示采用缓冲后的结果，公开图表没有无缓冲方案的对应数值。"
  ],
  "较大持仓宽度通常降低换手，但这一构造诊断不能确立 Alpha。": [
    "Turnover is 16.90% at 50 holdings and rises to 19.49% at 100. This chart cannot quantify the reduction from buffering or establish extra return.",
    "持有 50 只时，换手率为 16.90%，增加到 100 只时回升至 19.49%。这张图只显示缓冲后的换手率，降低了多少要补无缓冲对照，额外收益也仍待验证。"
  ],
  "现金流封顶影子": [
    "Cash-flow weighting with a cap",
    "现金流封顶权重"
  ],
  "缓冲后的等权": [
    "Equal weight with holding buffer",
    "暂留老持仓的等权组合"
  ],
"官方快照校准与独立规则影子":["Official-snapshot checks and separate research portfolios", "已有官方快照用于核对日收益，模拟组合单独比较规则。"],
"校准对照官方日收益，构造对照共同影子组合臂":["Compare calibration to official daily returns, and portfolio choices within a common research setup.", "回放结果与官方日收益比较，持仓安排在同一套模拟条件下比较。"],
"部分成分与重建财务历史":["Partial constituent records and reconstructed financial history", "部分成分资料，以及重建的历史财务数据。"],
"可用快照；标准影子持仓宽度回放含 80 个区间":["Available snapshots; holding-count research covers 80 monthly intervals.", "快照覆盖已取得的成分资料，持仓数量比较覆盖 80 个月度区间。"],
"同一标准影子协议与所选持仓宽度；官方历史保持独立。":["Compare weights under the same research protocol and selected holding count. Official history is recorded separately.", "比较采用同一套模拟规则和指定持仓数量。官方指数历史单独记录。"],
"现金流影子权重":["Comparison scope and review date", "比较范围与复核日期"],
"估值与质量过滤也可用于诊断现金流组合的价值陷阱。":["Valuation and quality checks can help identify low-priced stocks with weak fundamentals in cash-flow portfolios.", "估值与质量检查可帮助识别现金流组合中价格便宜、基本面却较弱的股票。"],
"两边均有现金流叠加，但行业与市场阶段限制各自独立。":["Both records add cash-flow criteria, with their own industry and market-period limits.", "两项研究都加入了现金流条件，适用行业和市场阶段需要分别核对。"],
"家族拆解可区分价值、质量暴露与现金流解释。":["Comparing fundamental factor families helps distinguish valuation and quality effects from cash-flow effects.", "拆开比较不同基本面因子，可帮助辨别结果来自估值、质量还是现金流。"],
"可用回放相关性":["Daily return correlation in available replay", "已有快照回放的日收益相关系数"],
};
export const readerCopy = (en: string, zh: string): Copy => projection[zh] ?? [en, zh];
