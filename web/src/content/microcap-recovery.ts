import type { LocalText } from './microcap-hub';
// Reviewed public field allowlist: no runtime locators, private configs or notebook payloads.
export const recoveryCopy = {
  "title": [
    "Evidence recovery follow-up · 2026-10-16",
    "证据找回进展 · 2026-10-16"
  ],
  "intro": [
    "This follow-up searched beyond source notes: tracked notebooks, retained derived reports, migration receipts and identified cold archives. Artifact recovery, structural checks and research reproduction are separate evidence stages.",
    "本轮从来源笔记继续追查已跟踪笔记本、保留派生报告、迁移收据和已识别冷归档。找回制品、结构检查与研究复现属于不同证据阶段。"
  ],
  "scope": [
    "The private ledger retains exact source identities, hashes, search roots and exclusions. The public build reads only this reviewed summary. No backtest or notebook was rerun and no shared data or latest pointer was changed.",
    "精确来源身份、哈希、检索根目录和排除项保留在私有账册。公开构建仅读取这份经审查摘要。本轮未重跑回测或笔记本，未修改共享数据或最新版本指针。"
  ]
} as const;
export const recoveryRecords: Array<{id:string;title:LocalText;status:LocalText;finding:LocalText;boundary:LocalText}> = [
  {
    "id": "R01",
    "title": [
      "Notebook inventory",
      "笔记本盘点"
    ],
    "status": [
      "Inspected; one family added",
      "已检查；新增一组主题"
    ],
    "finding": [
      "Seven source notebooks were found, all tracked in the two research repositories. Eight retained notebook files were also inspected: three are byte-identical copies, five are separate executed reviews. No additional untracked notebook was found in these two repositories.",
      "两研究仓库找到七份来源笔记本，均已跟踪；另检查八份保留笔记本，其中三份是逐字节相同副本，五份是独立执行审阅稿。这两个仓库未发现额外未跟踪笔记本。"
    ],
    "boundary": [
      "Cached size/beta feasibility evidence is now H35. Empty launcher notebooks, duplicate copies and synthetic calibration outputs do not count as independent empirical confirmations. No notebook was executed by this audit.",
      "规模与贝塔可行性的缓存证据已补为 H35。空输出启动笔记本、重复副本和合成校准输出不算独立实证确认。本轮没有执行笔记本。"
    ]
  },
  {
    "id": "R02",
    "title": [
      "Published snapshot lineage",
      "公开快照来源链"
    ],
    "status": [
      "53 rows matched; three still open",
      "53 行已匹配；三行仍待补"
    ],
    "finding": [
      "All 53 published rows in six table families match retained CSV fields at numerical tolerance 1e-10. This covers candidates, anatomy, capital, cadence, ledgers and the joint grid.",
      "六组表中已公开的全部 53 行，均以 1e-10 数值容差匹配保留 CSV 字段，覆盖候选、分解、资金、频率、账本与联合矩阵。"
    ],
    "boundary": [
      "The three low-turnover window rows are traceable to a public Git insertion, but a matching three-window runtime bundle was not located in the inspected roots. One coincidentally matching number elsewhere is insufficient. The published values are retained with this limitation.",
      "三个低换手窗口行可追溯到公开 Git 中的加入记录，但在已查根目录中未定位到匹配的三窗口运行包。别处单个数字相同不足以证明匹配。公开数值保留，并明确这项限制。"
    ]
  },
  {
    "id": "R03",
    "title": [
      "Historical 100-name bundle",
      "历史 100 只结果包"
    ],
    "status": [
      "Recovered through migration",
      "通过迁移记录找回"
    ],
    "finding": [
      "The dated bundle and its self-referencing metadata were located after following a documented directory rename. All full-sample summary figures agree with the rounded source note; this closes the earlier blanket “bundle unavailable” gap.",
      "沿有记录的目录更名找到对应日期结果包及其自指元数据。全样本摘要指标均与来源笔记的四舍五入数值一致，因此此前笼统的“结果包不可得”已不再成立。"
    ],
    "boundary": [
      "The recent-window comparison receipt and immutable execution binding remain missing. Recovery of stored results does not reproduce performance, verify index membership or certify implementation.",
      "近期窗口对照记录和不可变执行绑定仍缺失。找回存储结果不等于重现业绩、验证指数成分或认证执行。"
    ]
  },
  {
    "id": "R04",
    "title": [
      "Micro-cap exclusion robustness",
      "微盘排除稳健性"
    ],
    "status": [
      "Bundle recovered; provenance incomplete",
      "结果包已找回；来源链不完整"
    ],
    "finding": [
      "The full named artifact set and declared factor, weighting, buffer and capacity grids were recovered. Unique-key and completeness checks pass for 112 factor, 80 buffer and 24 capacity rows. Four checkpoint CSVs match final files.",
      "完整命名制品集，以及声明的因子、权重、缓冲和容量维度均已找回。112 行因子、80 行缓冲和 24 行容量记录通过组合键唯一与完整性检查，四份检查点 CSV 与最终文件相同。"
    ],
    "boundary": [
      "The owner-code commit fields are unknown. Input-vintage authentication, matching historical code and an independent rerun remain requirements before stronger reproducibility or strategy claims.",
      "所属代码提交字段为 unknown。在提出更强的可复现性或策略判断前，仍需认证输入版本、匹配历史代码并独立重跑。"
    ]
  },
  {
    "id": "R05",
    "title": [
      "Frozen-target rebuild receipts",
      "冻结目标重建收据"
    ],
    "status": [
      "Hashes agree; valuation remains blocked",
      "哈希一致；计价仍受阻"
    ],
    "finding": [
      "The stored readiness receipt and both target files match the hashes in the final verification receipt. Missing-mark table counts also agree with the stored audit.",
      "存储的就绪收据及两份目标文件，与最终校验收据中的哈希一致；缺价表行数也与存储审计一致。"
    ],
    "boundary": [
      "The receipts explicitly say no NAV was published. Suspension matches do not supply settlement prices or prove fills, and this audit did not verify a new engine installation or replay.",
      "收据明确写明未发布净值。匹配停牌不能补出结算价格或证明成交，本次也没有验证新的引擎安装或重放。"
    ]
  },
  {
    "id": "R06",
    "title": [
      "Attribution and characteristic decomposition",
      "归因与特征分解"
    ],
    "status": [
      "Exact bundles still missing",
      "精确结果包仍缺失"
    ],
    "finding": [
      "The exact historical Top800 attribution JSON and yearly CSV, its run-linked factor matrix, and the characteristic-decomposition output set were not found in the inventoried warm roots, migrated research subtree and identified cold archives.",
      "在已盘点的活动目录、迁移研究子树与已识别冷归档中，未找到对应历史 Top800 的精确归因 JSON、年度 CSV、绑定该次运行的因子矩阵，以及特征分解输出集。"
    ],
    "boundary": [
      "Similarly named later matrices cannot substitute. These are bounded negative findings, not proof of deletion. Resolution needs an exact artifact or a documented historical run/code/input binding; a new run must be labeled separately.",
      "后来的同名矩阵不能代替。这是有范围的未发现记录，不是删除证明。解决需要精确制品或有记录的历史运行、代码、输入绑定；新运行必须另行标识。"
    ]
  },
  {
    "id": "R07",
    "title": [
      "Later liquidity and execution reviews",
      "后续流动性与执行审阅"
    ],
    "status": [
      "Executed reviews located",
      "已定位执行审阅稿"
    ],
    "finding": [
      "Later executed notebooks preserve descriptive liquidity alignment and conditional execution-cost reviews. Synthetic calibration notebooks are separately identified as infrastructure evidence. The inspected cold-storage volume was available.",
      "后续执行笔记本保留了描述性流动性对齐与条件执行成本审阅；合成校准笔记本单独标记为基础设施证据。已检查的冷存储卷可用。"
    ],
    "boundary": [
      "Later aligned samples do not erase older source discrepancies. Numeric notebook outputs with unresolved redistribution permission remain local; cached execution and synthetic tests do not establish actual-order capacity.",
      "后续对齐样本不能抹去旧来源差异。再分发许可未解决的笔记本数值继续留在本地；缓存执行和合成测试不能证明真实订单容量。"
    ]
  }
];
