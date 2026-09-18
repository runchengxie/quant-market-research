# 研究收口状态（2026-09-18）

## 当前状态

| 主题 | 当前状态 | 本轮处理 | 仍需外部数据或人工核验 |
| --- | --- | --- | --- |
| 低换手 | `exploration` | 固定研究窗口、来源和下一步验证边界；网页标明探索性 | 点时截面暴露、独立前瞻月份、ADV/涨跌停成本和容量 |
| 微盘重建 | `incomplete` | 保留跨数据源边界和缺价风险说明；网页标明不完整 | 逐股复核复权因子、退市、停牌、成员资格、公司行动 |
| Barra 风格 | `derived` | 明确历史合成序列和 Barra-style 边界；网页标明来源和样本范围 | PIT 财务版本、Quality 重算、ROE/ROA 敏感性、样本外检验 |
| 指数与 ETF | `derived` | 增加实际快照日期和价格回报/ETF 口径提示 | 扩大代表性覆盖、费用/跟踪误差和更新频率审计 |
| 跨市场流动性 | `incomplete` | 保留逐市场 as-of 和待刷新状态 | 香港、美国、日本本地刷新；共同覆盖区间和可比性复核 |

## 数据新鲜度规则

- `generated_at` 是派生快照生成时间，不代表行情截至时间。
- `as_of` 或 `coverage_end` 是数据实际可用的最后日期；没有日期时显示“日期待补”。
- 跨市场数据必须逐市场显示日期，不能用一个“最新”覆盖所有市场。
- 探索性和不完整结果可以展示，但不得使用“已验证”“可交易”或“最新”作为替代描述。

## 可复现入口

微盘历史重建仍需仓库外数据根目录和运行输出目录：

```bash
uv run --locked --extra duckdb python scripts/analyze_microcap_history.py \
  --data-root /path/to/quant-market-data-platform \
  --output /path/to/research-outputs/microcap-history
```

低换手后续分析必须先冻结输入快照、代码版本、形成日名单、权重和评价指标，再写入仓库外结果目录；当前公开网页只发布审核后的汇总。

## 网页发布

在 `web/` 目录执行 `npm run build:pages`，它按顺序构建 Astro、构建 MkDocs、创建 `.nojekyll`，最后运行静态路由和公开边界校验。该命令不会刷新仓库外行情，也不会自动把 pending 数据变成 published。
