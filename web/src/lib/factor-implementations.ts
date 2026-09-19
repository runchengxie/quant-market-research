/** Inspected current source, NOT an assertion of identity with the legacy run. */
export const implementationSource = {
  project: "quant-research",
  revision: "b4317aaae6521111aa0c7674f2b1b0fe22dd3bd6",
  inspected: "2026-09-19",
};

export const currentFactorImplementations: Record<string, string> = {
  size: "ln(total_mv + 1)。total_mv 为源数据总市值字段；高分对应更大市值。",
  value: "仅保留正 PB，将 PB 限制在 [0.01, 100] 后取倒数；低 PB 得分较高。",
  earnings_yield: "仅保留正 PE_TTM，将 PE_TTM 限制在 [1, 500] 后取倒数。它是估值指标，不是经营质量指标。",
  momentum: "按股票计算收盘价过去 21 个观测的涨幅，再滞后 1 个观测；高分对应此前上涨较多。交易观测窗口不等于自然日。",
  lowvol: "股票日收益的 21 个观测滚动标准差（至少 10 个），滞后 1 个观测后取负值；低波动得分较高。",
  beta: "−Cov(rᵢ, rₘ) / Var(rₘ)，窗口 252 个观测、至少 126 个。rᵢ = pct_chg / 100，rₘ 为当日样本股票的等权平均收益；该实现包含形成日观测，不是默认使用某个指数。",
  liquidity: "−clip(turnover_rate, 0.01, 100)，即形成日换手率的负值；低换手得分较高，并非 20 日或 60 日均值。",
  growth: "净利润同比截断至 [−300, 500]，营收同比截断至 [−200, 500]，对可用项求均值；两项字段都需存在，单项缺失时均值使用另一项。财务可见版本仍需 PIT 核验。",
  leverage: "−clip(debt_to_assets, 0, 500)。保留源字段单位，资产负债率越低得分越高。",
  quality: "ROE、负债率负值、盈利波动负值、经营现金流 / 正净利润分别在截面 1%/99% 缩尾并 z-score，再等权平均。ROE 必须有效；参与组件的个股缺失分数填 0，组件列整体缺失时不参与平均。盈利波动使用按公告排序的 8 个财务观测（至少 4 个），不保证是 8 个连续季度。",
  liquidity_flow: "优先取 buy_lg_amount_rate；只有该列不存在时才改用 net_amount，并非逐行缺失回退。两字段不是同一单位，因此不能统一描述成“大单净买入占比”。",
  chip_concentration: "取 top10_float_concentration，即前十大流通股东集中度字段，再做统一截面处理。具体可见日需沿持仓源表继续核验。",
  institution_holding: "取 top10_inst_float_hold_ratio，即前十大机构流通持股比例字段；不是全部机构持仓的完整统计。",
  fund_breadth: "ln(1 + max(重仓基金数, 0))。基金数仅统计将该股票列入前十大重仓的基金，不代表全持仓覆盖。",
  fund_breadth_change: "sign(Δ基金数) × ln(1 + |Δ基金数|)。Δ 是相邻形成日上可见的前十大重仓基金数之差。",
  fund_ownership: "取 fund_top10_stk_float_ratio_sum：同一披露范围内，基金前十大重仓的流通股持有比例求和。",
  fund_ownership_change: "取上述流通持股比例之和在相邻形成日的变化，不是收益率，也不是基金数的变化。",
  dividend_yield: "直接取 daily_basic.dv_ttm（滚动股息率源字段），再做统一截面处理；不另外假设分红再投资。",
  ps_value: "对正 ps_ttm 取倒数，非正值视为不可用；低市销率得分较高。",
};

export const commonFactorProcessing = "最终得分在每个截面做 1%/99% 缩尾；有申万一级行业信息时减去行业均值，再做全市场 z-score。这不保证最终多空组合行业权重中性。";
