# 跨市场小微盘流动性对齐

跨市场小微盘研究按市场、市值分位和时间区间比较流动性。每个观察日都按当时市值重新分组，流动性使用形成日前 20 个有效观察日的 `ADV20`，结果统一换算为美元。

输入来源包括 A 股、HK cold data、Japanese NIRA 和现有美股面板。各来源的
成交额单位、交易日历、停牌记录、可交易 universe 和市值字段不同，因此
输出同时保留 native currency、FX method、universe filter、coverage 和
quality status。

这项研究用于描述市场差异。`ADV20`、低市值分组和跨市场比较结果不代表策略容量、实际成交能力或生产策略收益。
