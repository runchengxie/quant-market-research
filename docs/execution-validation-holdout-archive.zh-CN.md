# 前瞻执行验证：登记与归档契约

[English](execution-validation-holdout-archive.md)

本文为未来替代批次规定操作契约，不代表已经登记或启动新批次。协议 v1 及其既有哈希作为历史记录保留；不能把错过的 2026-10-15 起点事后重建成未见样本。冻结的研究设计仍见 [v1 协议](execution-validation-followup-protocol.json)；规划新版本前先阅读[状态与数据缺口说明](execution-validation-next-stage.zh-CN.md)。

## 就绪情况

仓库现有 `prepare_execution_validation_suite.py` 和 `run_execution_validation_suite.py`，用于历史执行验证的准备和回放；它们不登记前瞻批次，也不封存每日回执。项目数据目录中有历史验证套件，但没有 252 日前瞻批次目录。不得把历史套件输出当成前瞻记录。下文规定缺失的交接契约；登记新批次前，必须用合成样本实现并演练每日采集自动化。

## 仓库外批次目录

所有批次记录都放在稳定的数据根目录下，不进 Git：

```text
$DATA_ROOT/quant/quant-market-research/ashare_execution_costs/prospective-holdout/<cohort-id>/
  registration.json
  protocol.json
  session-calendar.json
  sessions/
    YYYY-MM-DD/
      pre_session.json
      post_session.json
      <已登记的数据源与账本文件>
      corrections/                 # 仅在需要时追加
```

使用新的批次 ID 和新的协议版本，不得原地修改或覆盖 v1。登记包必须在首个适用交易日前封存，并绑定：

- 批次 ID、schema 版本、UTC 登记时间和明确确定的首个观察交易日。
- 协议原始字节及 SHA-256、252 个交易日时长、主要/次要比较、参数、指标、不确定性计算、支持标准、中期可见范围和缺失数据规则。
- 将要产出记录的选股、执行和评估代码及配置对应的 Git commit 与 SHA-256。
- 交易日历、日线/全候选池输入、公告与 ST 证据、分钟行情、费用、公司行动/估值等来源身份、版本、覆盖范围和哈希。
- 采集时间安排、责任人、归档位置、保留/备份规则，以及迟到、缺失或损坏文件的处理流程。

登记记录保存相邻 `protocol.json` 与 `session-calendar.json` 原始字节的哈希；每份回执绑定 `registration.json` 原始字节的哈希。日历文件列出来源与252个交易日；登记记录逐日绑定决策、开市、入场截止和收盘归档时刻。操作人员必须在登记前核对权威日历。机器可读契约见[登记 schema](schemas/execution-validation-holdout-registration.v1.schema.json)、[交易日历 schema](schemas/execution-validation-session-calendar.v1.schema.json)和[逐日回执 schema](schemas/execution-validation-holdout-session-receipt.v1.schema.json)。检查器会核对日历字节哈希、日历日期与登记时段是否一致，并检查日期/时刻格式和顺序；不会联网获取或独立证明交易日历权威性。代码、来源、参数或缺失处理规则如需改变，必须登记独立版本并开启新的前瞻窗口，不得静默修改进行中的批次。

## 每日回执

每个适用交易日在 `sessions/YYYY-MM-DD/` 写 `pre_session.json` 和 `post_session.json`。分成两份回执后，输入可以在预登记的入场截止时间前封存，成交和估值文件则在交易结束后封存。两份回执都只用于清点和检查完整性；不得写入净值、收益、回撤、容量、成交率汇总或其他绩效结果。每份回执均须绑定已登记批次，并包含：

- `schema_version`、`cohort_id`、`session_date`、`captured_at_utc`、`capture_phase` 和 `registration_sha256`。
- `status`（`complete` 或 `blocked`）及缺失/迟到原因。空事件表不能证明事件来源覆盖完整。
- `pre_session` 回执的文件清单包括完整候选池、选股目标、输入/来源清单、公告和 ST 证据、分钟行情清单及引擎/配置指纹；`post_session` 回执包括完整现金/持仓/委托/成交/估值账本。
- 固定的工件 ID 为 `candidate_universe`、`targets`、`input_manifest`、`announcement_st_evidence`、`minute_data_manifest`、`engine_config_fingerprint` 和 `cash_holdings_orders_fills_valuation_ledgers`。严格 schema 会拒绝其他 ID 和所有未登记回执字段，包括绩效字段。
- 每份文件相对于当日目录的路径、字节数和 SHA-256；回执中不写本机绝对路径。

在登记的决策时刻之后、入场截止时刻之前写入并核验 `pre_session.json`。登记时间必须早于首个交易日的决策时刻。不早于登记的收盘归档时间、且在前一回执之后写入 `post_session.json`。采集不完整时标记 `blocked`，保留缺失项；不得事后补档并把该日称为有效前瞻样本。更正须另存为新版本，使用新回执并引用被替代文件；绝不能覆盖已用过的字节。

## 安全的逐日检查与结项

在当日收盘归档完成后运行仅完整性检查器：

```bash
uv run python scripts/validate_execution_holdout_archive.py \
  --root "$HOLDOUT_ARCHIVE_ROOT" \
  --through-session-date YYYY-MM-DD
```

单独运行临时合成演练：

```bash
uv run --locked --extra dev pytest -q tests/test_execution_holdout_archive_validator.py
```

两个参数均必填，工具没有默认数据路径。它核对登记、协议和日历指纹，检查日历顺序日期与登记时段相符，并核对回执 schema/状态/时序、文件相对路径、大小和 SHA-256。它只哈希文件字节，不解析包括账本在内的文件内容，只输出完整性状态或错误；不会验证操作者登记的交易日历是否权威。现有历史回放脚本会生成评价结果，不适用于每日检查。合成演练会在测试器临时目录创建测试归档，不创建真实批次，也不读写项目 DATA_ROOT。

满 252 个适用交易日后，先封存归档，独立核对登记哈希、所有每日回执、文件哈希、交易日序列及缺失/更正记录。此后才能按登记协议进行一次性评估。若期末估值或处置现金未解决，须将最终净值记为不完整，不发布全期绩效。

## 启动前检查表

- [ ] 新协议版本已审阅；原始字节已归档，v1 未改动。
- [ ] 登记包含上述字段，且时间戳早于首个适用交易日。
- [ ] 仓库外 DATA_ROOT 位置、权限、不可变保留和备份均已验证。
- [ ] 每日采集和仅完整性检查已通过文档所述合成演练；测试没有生成真实交易日记录或 DATA_ROOT 文件。
- [ ] 故障处理可阻止迟到数据被标成准时，也可阻止更正覆盖原始输入。
- [ ] 中期访问仅限完整性元数据；一次性结项前绩效输出不可见。
