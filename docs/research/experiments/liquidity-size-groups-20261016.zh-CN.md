# 如何理解空桶与各市场内部市值分组

[English](liquidity-size-groups-20261016.md)

页面默认市值桶已改为1亿—10亿美元，各个已发布视图在此都有A股观测。绝对市值空桶会说明“所选组无合资格观测”，同时列出该市场的完整样本数量；整个市场缺少数据仍单独列在区间覆盖信息里。

A股`< $10m`桶在五个视图中均无合资格观测，但A股来源没有缺席。本次合资格A股面板覆盖2019-11-29—2026-10-15。此前核查还发现151个低于1,000万美元的候选证券日因缺少连续市场观察日被排除。因此“没有观测”只适用于当前合资格样本，不能推断整个A股历史上从未有过这一规模的股票。

## 可选的相对比较

新增的“各市场内部市值五等分”沿用[已复核美元分组](liquidity-rebuild-20261016.zh-CN.md)的合资格特征、来源日期、共同日交集、滚动统计和汇率，只改变分组成员：

- 每个观察日，在各来源市场内部按前期美元总市值从小到大排序。
- 使用`NTILE(5)`分成五组；同市值按稳定的证券标识顺序排列。各组整数数量可相差一只，极小测试样本可以出现空组。
- 历史区间汇总每日成员，按证券日等权。股票可能跨组，因此各组去重股票数不能相加。显示的实际市值范围覆盖所选组的全部证券日，并非固定每日分界。

2025-09-30最小五分之一分别有美股884只、港股486只、A股1,044只、日股731只。市值上界分别约为1.0115亿／1,774万／4.8268亿／3,848万美元。这说明相同的市场内部排名**不等于相同美元规模**。范围保留来源估值，包括极小正值；历史股数及证券股类尚未获得独立认证，相对分组也不会修复来源股票池或估值差异。

原有美元分组JSON及独立复核校验和保持原样。单独的[相对分组汇总](../../../web/public/data/liquidity/relative-summary.json)绑定该版本的精确校验和。另一条pandas／NumPy路径核对了每日五等分成员及**950个汇总单元格**，包括两种滚动口径、样本数量及实际市值范围；还重新核对原美元分组的760个单元格，并校验实际读取的特征文件哈希，防止误用不同版本。复核覆盖各发布视图的19,275,158个证券日条目，视图之间有重叠，不能写成独立审计了同等数量的原始记录。详见[相对分组复核记录](../../../web/public/data/liquidity/relative-review.json)。

## 复现

设置`PYTHONPATH=src`，私有变量`FEATURE_DIR`指向前轮已核对的特征文件；运行输出及中间文件均保存在Git仓库外：

```sh
python scripts/build_liquidity_relative.py --features "$FEATURE_DIR" --base web/public/data/liquidity/summary.json --output "$RUN_DIR"
python scripts/review_liquidity_relative.py --base web/public/data/liquidity/summary.json --features "$FEATURE_DIR" --proposal "$RUN_DIR/relative.proposed.json" --output "$RUN_DIR/independent-review.json"
python scripts/publish_liquidity_relative.py --proposal "$RUN_DIR/relative.proposed.json" --review "$RUN_DIR/independent-review.json" --base web/public/data/liquidity/summary.json --output web/public/data/liquidity/relative-summary.json
```

发布门禁检查复核及基础版本的精确校验和、汇总字段边界、市场／日期／股票池信息保持一致及数量守恒。公开文件不包含证券标识、原始行或私有路径。相对分组文件加载失败时可以单独重试，美元分组仍可使用。
