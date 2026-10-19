# 海外信号前向封存协议 v1

[English version](overseas-forward-v1.md)

10 月 18 日安装探针不合格，不计入前向观察；2026 年 10 月 19 日上海时间 08:44 首次定时归档已成功，现保留 1 个合格观察。

## 首次定时验收：2026 年 10 月 19 日

定时器于上海时间 08:44:00 启动服务，08:44:02 成功退出，未手工触发或重跑。实际采集从 `2026-10-19T00:44:00.373965Z` 开始，至 `00:44:02.093013Z` 完成，预测于 `00:44:02.236136Z` 封存。当日 manifest 的 `eligible=true`，无弃样原因；8 份归档 CSV、receipt 及 prediction 的 SHA256 均经独立核验。

这 1 个合格观察只验证采集与封存链路，不证明预测效果或收益。仍须累计至少 60 个合格目标日再做首次评估；本次未自动评分、发送消息或交易。

稳定核验标识：资格 manifest SHA256 为 `7e2a388e925d0b46d846793781e055c1338a73afbf3d87958d07c6c163cef139`；原始 receipt SHA256 为 `6827020df51f990fb8fce1c74454c5a349fa5574f3b677c4c54ec337251ff3a4`。这里只公布证据哈希，不公开原始行、当次预测方向或本机路径。

本协议只从真实 receipt 开始累计证据。既有历史数据用于研究和训练，不能再称作 untouched holdout，也不能凭现在下载证明历史时点可得。

首版固定信号 `spx-last-session-direction-csi300-open-next-open-v1` 预测沪深300当日开盘至下一 SSE 交易日开盘的涨跌方向：SPX 最近已闭市两个收盘价的收益率为正预测 +1，为负预测 -1，零为 0。不拟合、不再调参，不是既有年度 expanding 三臂模型，也不是交易或收益保证。选择该简单基线用于验证真实时点链路，不根据未来结果切换模型。

上海工作日 08:44 发起新请求，08:45 截止，完成 receipt 与预测封存都必须不晚于截止。采集开始须落在 08:43–08:45。SSE 当日交易必须由同次 receipt 的 trade_cal 确认。SPX 最晚来源日期必须等于截止在纽约的日期向前退至工作日；若美国假期导致此日期没有数据，保守弃样，不把前一日价格当作新信息。两个 SPX bar 之间不超过七个自然日，价格有限且为正、日期不重复，闭市加一小时不晚于截止。常规闭市时间仅为假设，真实 receipt 时间才是本轮接收证据。亚洲、FX 数据同时保存但不参与 v1 预测。

`python -m market_research.studies.overseas_leadlag.forward --receipt-directory <MDP-run> --output <QMR-owner-data>/forward/overseas-v1`

读取时核对原始 CSV hash；先独占写入 `.prediction.json` 并 fsync，再读取实际写入完成时钟。随后独占写入 `.json` manifest，其 `eligible` 是资格判定依据，包含 payload hash 和实际 `sealed_utc`，跨截止一律弃样。只有 payload 而无 manifest 表示封存中断。派生 JSON 保留 receipt hash、代码 hash、固定信号身份、选用 bar、预测和不合格原因。scheduled 每个目标日只允许独占创建一个文件，包括迟到/失败弃样，禁止覆写或事后挑选重跑。probe 独立封存，永不计入前向观察。若进程在 CSV/receipt/预测封存前失败，保留现有证据，次日人工核对缺口；不回填成合格记录。完整 started 而无 receipt 表示采集中断，完整 receipt 而无 forecast 表示封存失败。

v1 不消费任何目标日之后的国内价格。不自动打分、不发送消息、不下单。未来评分须另加 append-only outcome 记录，以真实后续获取的目标开盘价标注标签与接收时间；不改写预测。累计至至少 60 个合格 SSE 目标日再做首次方向命中率及不确定性评估，同时列出所有缺失、迟到和美国假期弃样；期间不因结果改规则。变更信号、截止或依赖必须启用新协议版本并重新起算。

稳定发布安装两个 owner 后，可以用 `scripts/overseas_forward.sh [scheduled|capture_probe]` 串联采集与封存。所需环境变量为 `MARKETDATA_BIN`（已安装的 owner launcher）、`DATA_PLATFORM_CONFIG`、`MDP_CAPTURE_PYTHON`、`RESEARCH_PYTHON`、`OVERSEAS_RAW_ROOT`、`OVERSEAS_DERIVED_ROOT`。两个 Python 和脚本自身必须指向已合并的不可变 release。单用途 systemd timer 采用 `OnCalendar=Mon..Fri *-*-* 08:44:00 Asia/Shanghai`、`AccuracySec=1s`、`RandomizedDelaySec=0`、`Persistent=false`，服务不自动重试，防止重跑替换当日弃样。日志保留服务退出和产物路径。
