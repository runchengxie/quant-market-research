export const legacyCopy = {
  'etf-rotation': {
    title: ['ETF rotation: integration and evidence', 'ETF 轮动：迁移与证据'],
    question: ['Can retained ETF recipes run through maintained research infrastructure?', '旧 ETF 研究配方能否通过统一研究基础设施运行？'],
    conclusion: ['Synthetic integration succeeded. No real-data comparative return evidence has been admitted.', '合成数据集成验证已通过，尚未纳入真实数据的收益对照证据。'],
    baseline: ['Fixed ETF diagnostic recipes; investment benchmark and cost comparison remain pending.', '固定的 ETF 诊断配方；投资基准和成本对照仍待验证。'],
  },
  hotsector: {
    title: ['Hotspot candidates: integration and evidence', '热点候选：迁移与证据'],
    question: ['Can retained hotspot candidate recipes run through maintained research infrastructure?', '旧热点候选配方能否通过统一研究基础设施运行？'],
    conclusion: ['Synthetic integration succeeded. No real-data comparative return evidence has been admitted.', '合成数据集成验证已通过，尚未纳入真实数据的收益对照证据。'],
    baseline: ['Deterministic topic-to-candidate baseline; investment benchmark and cost comparison remain pending.', '确定性的主题到候选池基线；投资基准和成本对照仍待验证。'],
  },
  shared: {
    stage: ['Synthetic integration', '合成数据集成验证'],
    scope: ['Synthetic fixtures only; no historical investment sample.', '仅使用合成样本，没有历史投资样本。'],
    missing: ['Investment performance has not been established. Missing returns are not zero returns.', '尚未建立投资绩效证据，缺少收益数据不代表收益为零。'],
    limitations: ['Historical availability and untouched evaluation samples remain unverified. No live RD-Agent comparison was performed.', '历史数据可见性和未经研究使用的评估样本仍待核验，尚未进行实时 RD-Agent 对照。'],
    factors: ['Related factor methods', '相关因子方法'],
    factorBoundary: ['Factor links are conceptual references; their datasets and definitions are not interchangeable with strategy inputs.', '因子链接仅作方法参考，所用数据集和定义不能与策略输入直接替换。'],
    provenance: ['Reviewed source and public-content fingerprints', '已审查的来源与公开内容指纹'],
  },
} as const;
