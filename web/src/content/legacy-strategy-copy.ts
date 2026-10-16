// Chinese evidence translations are reviewed against this exact public content.
const translationReviewDigest = 'e5d5b2d39289f13a9b0c955e23bd0714e616e22dea6b2aab9c9fc7bd8bcac334';
const translations = {
  'etf-rotation': {
    title: ['ETF rotation: integration and evidence', 'ETF 轮动：迁移与证据'],
    question: ['Can retained ETF recipes run through maintained research infrastructure?', '旧 ETF 研究配方能否通过统一研究基础设施运行？'],
    baseline: '固定的 ETF 诊断配方；投资基准和成本对照仍待验证。',
  },
  hotsector: {
    title: ['Hotspot candidates: integration and evidence', '热点候选：迁移与证据'],
    question: ['Can retained hotspot candidate recipes run through maintained research infrastructure?', '旧热点候选配方能否通过统一研究基础设施运行？'],
    baseline: '确定性的主题到候选池基线；投资基准和成本对照仍待验证。',
  },
} as const;

export const legacyCopy = {
  shared: {
    stage: ['Synthetic integration', '合成数据集成验证'],
    missing: ['Investment performance has not been established. Missing returns are not zero returns.', '尚未建立投资绩效证据，缺少收益数据不代表收益为零。'],
    factors: ['Related factor methods', '相关因子方法'],
    factorBoundary: ['Factor links are conceptual references; their datasets and definitions are not interchangeable with strategy inputs.', '因子链接仅作方法参考，所用数据集和定义不能与策略输入直接替换。'],
    provenance: ['Reviewed source and public-content fingerprints', '已审查的来源与公开内容指纹'],
  },
} as const;

type Study = {
  id: string; question: string; conclusion: string; baseline: string;
  sample_scope: string; limitations: string[];
};

export function legacyStudyCopy(study: Study, reviewedContentDigest: string) {
  if (reviewedContentDigest !== translationReviewDigest) {
    throw new Error('Translation content requires review against the changed public evidence');
  }
  if (!(study.id in translations)) throw new Error('Study translation unavailable');
  const zh = translations[study.id as keyof typeof translations];
  return {
    title: zh.title,
    question: zh.question,
    conclusion: [study.conclusion, '合成数据集成验证已通过，尚未纳入真实数据的收益对照证据。'],
    baseline: [study.baseline, zh.baseline],
    scope: [study.sample_scope, '仅使用合成样本，没有历史投资样本。'],
    limitations: [study.limitations.join(' '), '集成验证不代表投资有效性。历史数据可见性和未经研究使用的评估样本仍待核验，尚未进行实时 RD-Agent 对照。'],
  } as const;
}
