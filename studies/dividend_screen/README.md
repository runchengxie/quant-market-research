# 年度现金股息研究

每年独立筛选：该自然年**已实施且除息日落在该年**的税前每股现金分红总额，除以同一证券、同一币种的年度最后交易日未复权收盘价，严格大于 5%。这里的“分红率”指股息率；利润分配比例另称派息率。未取得分红数据的证券保持缺失，不能解释为不分红。

代码在 `src/market_research/dividend_screen.py`，供应商原始文件、下载缓存、导出结果放在仓库外的项目数据目录。不要将 token 写进代码或 Git。

## 数据目录与复现命令

研究代码属于 `CODE_ROOT/quant/quant-market-research`，本研究的缓存和结果属于
`DATA_ROOT/quant/quant-market-research/dividend-screen/runs/<获取日期>`。
共享市场数据只读引用 `DATA_ROOT/quant/quant-market-data-platform/assets/tushare/a_share`，
不复制整套共享行情。`CODE_ROOT` 与 `DATA_ROOT` 从明确传入的工作区 TOML 解析；它们不是自动导出的环境变量。

安装锁定研究依赖：`uv sync --locked --extra dividends --extra dev --extra duckdb`。
下载命令从进程环境读取 `TUSHARE_TOKEN` / `TUSHARE_API_URL`，备用配置使用对应 `_2` 变量。
使用市场数据平台的 `marketdata config run --config <私有配置JSON> -- <下面的命令>` 注入凭证，
不要在命令行写 token 值。本仓不创建另一份凭证配置。

```bash
uv run --locked --extra dividends python scripts/research_dividend_screen.py download --workspace-config <工作区TOML>
uv run --locked --extra dividends python scripts/research_dividend_screen.py base --workspace-config <工作区TOML>
uv run --locked --extra dividends python scripts/research_dividend_screen.py history --workspace-config <工作区TOML>
uv run --locked --extra dividends python scripts/research_dividend_screen.py volatility --workspace-config <工作区TOML>
uv run --locked --extra dividends python scripts/hk_dividend_fetch.py fetch --output-dir <运行目录> --a-instruments <A名单parquet> --h-instruments <H在市名单parquet> --h-delisted <H退市名单parquet>
uv run --locked --extra dividends python scripts/export_dividend_screen.py --output-dir <运行目录> --source-root <共享A股资产目录>
```

这是 2023—2025 固定研究切片，默认获取日期为 `20261005`，可使用 `--as-of` 指定财务和分红可见性截止日。
生产数据脚本的 `base/history/volatility` 支持用 `--source-root` 与 `--output-dir` 显式指定路径。
H 映射应先生成再执行 `history`，以取得只在 H 股入选的公司的财年对照。
首次 Yahoo 下载不覆盖退市或空价证券时，执行 H 脚本的公开来源补充模式，详情见 `--help`；
补充事件与金额存入运行目录的 `h_supplementary_dividends.csv`，保留来源和未经官方逐笔核实的标记。
`output` 模式只读取已归档缓存重算，不联网；下载阶段必须自行遵守公开源限额。

本次 H 股完整流程如下；每一条命令都还需传上文的三个名单路径和同一运行目录。
`fetch` 之后 `audit` 才能读取其输出的送转事件清单，补充缓存后必须再次 `output`：

```bash
uv run --locked --extra dividends python scripts/hk_dividend_fetch.py fetch <名单与目录参数>
uv run --locked --extra dividends python scripts/hk_dividend_fetch.py audit <名单与目录参数>
uv run --locked --extra dividends python scripts/hk_dividend_fetch.py fallback <名单与目录参数>
uv run --locked --extra dividends python scripts/hk_dividend_fetch.py tencent <名单与目录参数>
uv run --locked --extra dividends python scripts/hk_dividend_fetch.py output <名单与目录参数> --supplementary-dividends <运行目录>/h_supplementary_dividends.csv
```

补充事件 CSV 的列是 `ts_code,date,amount,currency,source`，其中 `date` 是 H 股除息日，
`amount` 为该次税前港币股息的原始每股金额，`currency` 必须为 `HKD`，
`source` 为公告或独立公开记录的 URL，可用 ` | ` 保存交叉核对来源。
日期可用 ISO 格式；不要填 A 股除息日或人民币金额，也不要把同一事件从两个供应商重复加入。
补充文件属于外部运行输入，首次制作需要核对原文；离线复现直接使用归档文件及其哈希。
本次补充海通证券 2023 年末期、2024 年末期与中期，以及中集车辆 2023 年末期，
分别保留同花顺/Investing/老虎交叉核对和港交所公告来源，未官方核实的记录在输出中明确标记。
腾讯补充的是原价与复权行情，不从价格变化猜测现金分红。

`manifest.json` 记录代码提交与哈希、锁定环境版本、这些补充输入的哈希，
以及共享资产 `latest` 实际解析到的版本目录和财务/名单/行业/年末行情输入哈希。
以后重算应恢复这些版本，而不是默认读取后来更新的 `latest`；供应商可能更正历史记录。
复现本次结果可直接读取归档的 `a_all_years_base.parquet`、`a_volatility.parquet`、
`selected_dividend_history.parquet` 与 H 缓存再导出，避免重复联网。

原始响应保留在 `raw/` 和 `hk_raw/`，查询日期、获取时间与参数保存在无凭证的查询记录；
Excel、CSV、HTML 与 `manifest.json` 均为外部生成物。报告不推送至公共网页。
分红事件覆盖全部日历日期，限速低于 Tushare 200 次/分钟；任一查询最终失败则拒绝宣称完整。

### 本次实际修正与限制

- 宝丰能源 2024 实施的 2023 财年分红：中小股东每股 0.3158 元，大股东每股 0.2650 元。
  采用公众持有人口径且保留修正来源，不把公众股息外推为全公司现金额。
- 顺丰控股 2024 中期普通分红 0.4 元与特别分红 1 元合并实施：采用合计每股 1.4 元，重复版本不再相加。
- 九号公司 CDR 的供应商分红数字按每 10 份披露，需转换为每份金额，避免十倍高估。
- 8 家 H 股发生送股/拆股，Yahoo 同日股息调整行为不一致；用独立 H 股港币事件金额核对，
  恢复年末原价并统一年末份额。补充原文与股本事件全部保留在外部缓存。
- 证券行业同时参考 Tushare 公司财报类型 `comp_type=4`，避免历史退市券商因当前行业为空漏筛。
- H 名单采用法律全名匹配港币主柜台，可能遗漏因法律主体更名未匹配的 A+H 公司。
  获取了已匹配且当年末合格的全部股年价格，不等于证明全市场映射无遗漏。
- 广和通、均胜电子的 2025 H 股上市后价格已补齐；供应商无当年股息事件，零值仍保留未逐公告确认标记。
- 财年口径是截至获取日的回顾数据，包含次年实施分红和更新财报，不能当作当时可交易的历史信息。

## 输入与重算

全部函数接收 pandas DataFrame，支持从 CSV 或 parquet 读取后重算；日期使用 `YYYYMMDD` 或 ISO 日期。A、H 股用独立证券代码；价格与每股分红必须先统一币种。人民币分红除港币价格前应转换，并保存汇率日期与来源。年度收盘价必须以对应市场交易日历确认是最后交易日，不能直接用数据中最后一个非空价格替代。

- 分红事件：`ts_code,end_date,ex_date,div_proc,cash_div_tax`，可加 `cash_amount`。`div_proc` 接受 `实施` / `implemented`；`cash_div_tax` 是税前每股金额。事件键为代码、分红所属期末日与除息日。重复相同金额只计一次，冲突金额拒绝计算。缺失任一笔金额使该年度总额缺失。
- `normalize_tushare_cash` 使用 Tushare `base_share`（万股）计算 `cash_amount`（元）：基数 × 10000 × 税前每股分红。应先核对供应商字段单位；不能以期末股份数填补缺失分红基数。
- 年末报价：`ts_code,year,close`，可带 Tushare `dv_ratio,dv_ttm` 和其他财务指标。`screen` 保留这些字段，与实施口径并列。`dividend_totals(..., basis='fiscal')` 单独汇总所属财年，不能混用实施年份和财年净利润。
- 复权行情：`ts_code,trade_date,adj_close`。收益率是复权价格简单日收益；年度波动率为样本标准差 × √252 × 100，包含上一年最后一个交易日到该年首个交易日的收益。缺失价格不前向填充，重复报价拒绝计算。样本少于 200 个收益标 `insufficient_sample`；可计算值仍保留，少于两点结果缺失。停牌造成的非交易日不人为补零。行情至少覆盖上一年最后一个交易日。
- 行业头部：输入完整 A 股年度横截面 `ts_code,year,sw_l1,is_broker,total_mv`。按同年申万一级行业的 A 股报价总市值取前三；券商同时在券商集合独立取前三。并列按代码排序。缺失行业、市值不能认定行业头部。该定义是市值代理，不是营收、盈利或业务地位判断。H 股通过发行人映射继承对应 A 股标记；不得加入 A 股排序重复计算发行人。
- 财年派息：`cash_div_tax,cash_amount,net_profit_parent,eps`。现金总额与归母净利必须使用同币种同金额单位；优先现金总额 / 正归母净利。否则使用 DPS / 正 EPS 并显式标 `dps/eps_proxy`；不能当成真实总额派息率。亏损年份比例缺失。

建议导出全覆盖表、超过阈值表、券商筛选表、缺失与来源审计表，以及口径差异表。A+H 对照需保留发行人关系、各自行情与货币来源、汇率转换和分红公告来源。行业分类采用的日期与版本也需写入运行清单，避免将当前行业标记误称历史行业。

离线回归测试：`uv run --locked --extra dev pytest -q tests/test_dividend_screen.py`。

## 同年送转股与年末份额

自然年实施股息率先调用 `restated_dividend_events`：每笔税前每股现金分红除以从其除息日（含当日）至该年末所有送转股的累乘因子 `1 + stk_div`。纯送转、现金为零的事件也必须输入。例如六月每股现金 0.6 元并送转 0.5 股，十二月另派 0.2 元，年末份额口径为 0.4 + 0.2 = 0.6 元，而原始 DPS 为 0.8 元。否则以送转前分红除送转后股价会高估股息率。

函数保留 `cash_div_tax_raw`、`share_factor_to_year_end` 和真实 `cash_amount`；所属财年的派息率继续使用原始真实现金。不同年份送转不相互作用，同日重复送转只计一次，同日不同正送转比例拒绝计算。同日独立现金记录中的零送转不是额外股票行动。负送转比例拒绝，缺失比例默认零并标 `stk_div_assumed_zero` 供审计。调用前只保留已实施事件。增发融资不属于拆分或送转，不能录入此因子。供应商特殊证券单位纠错应在输入规范化层按已核实公告记录覆盖，并保留审计清单。
