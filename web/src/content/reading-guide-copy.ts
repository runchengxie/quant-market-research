type Copy=readonly [string,string];
export const readingGuideCopy={title:['Research terms in everyday language','常用研究词怎么理解'],intro:['The table explains terms used across the research pages. Each chart keeps its own dates and calculation rules.','这里解释网站常用的研究词。每张图仍会注明样本日期和计算方法。'],link:['Explain the research terms','查看常用词解释']} as const;
export const readingTerms:readonly {name:Copy;meaning:Copy}[]=[
 {name:['Annualized return','年化收益'],meaning:['The constant yearly compound rate that produces the observed start-to-end return.','把起点到终点的收益，换算成每年按同一速度复利增长的结果。']},
 {name:['Drawdown','回撤'],meaning:['The fall from a previous peak. Month-end observations cover month-end falls.','从此前最高点下跌多少。图中采用月末数据时，只能看到月末之间的变化。']},
 {name:['Percentage point','百分点'],meaning:['Subtract two percentages directly. A rise from 3% to 5% is 2 percentage points.','两个百分比直接相减。收益从3%升到5%，增加了2个百分点。']},
 {name:['Basis point','基点'],meaning:['One basis point is 0.01 percentage point. A 50bp fee is 0.5%.','1基点等于0.01个百分点。50基点费率就是0.5%。']},
 {name:['Calculation basis','口径'],meaning:['The scope and rules used to calculate a number.','计算这组数字时采用的范围和规则。']},
 {name:['Overlapping windows','重叠窗口'],meaning:['Holding periods that share some of the same months and therefore share observations.','两段持有期共用部分月份，结果会相互关联。']},
 {name:['Resampling','重抽样'],meaning:['Repeatedly selecting pieces of observed history to inspect how results vary.','从已有历史中反复抽取片段，查看结果怎样变化。']},
 {name:['Attribution','归因'],meaning:['Checking how identified factors contribute to a return or change.','逐项核对收益变化与哪些因素有关。证据充分时，才能进一步解释原因。']},
 {name:['Point-in-time data (PIT)','时点数据（PIT）'],meaning:['Information aligned with when it became public. Original historical versions need separate checks.','按资料当时公开的时间对齐信息。能否还原原始版本，还要另行核查。']},
 {name:['Right-censored wait','尚未结束的等待'],meaning:['The observation ends before recovery, leaving only the time already observed.','观察结束时仍未恢复，只知道已经等了多久。研究中也称右截尾。']},
 {name:['Public projection','公开汇总'],meaning:['The reviewed summary fields selected from a complete research result for publication.','从完整研究结果中选出经过核对、允许公开的汇总数据。有些记录把这一步称为投影。']},
 {name:['Admission','纳入正式研究'],meaning:['The checks required before a sample or observation enters the stated research process.','样本或观察通过事先约定的检查后，才纳入正式研究。页面中的准入指这一步。']},
 {name:['Out-of-sample check','样本外检验'],meaning:['Checking a rule with data that did not help choose the rule.','用未参与规则选择的数据，单独检查结果。']},
];
