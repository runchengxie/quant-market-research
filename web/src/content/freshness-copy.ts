export const freshnessStatusCopy: Record<string, readonly [string, string]> = {
  derived: ['Derived summary', '衍生汇总'],
  pending: ['Pending', '待补'],
  unknown: ['Unknown', '尚未确认'],
  reviewed: ['Reviewed', '已审核'],
  exploratory: ['Exploratory', '探索中'],
  validated: ['Validated', '已验证'],
  partial: ['Partial coverage', '覆盖不完整'],
  blocked: ['Blocked', '暂不可用'],
};

export const freshnessSourceCopy: Record<string, readonly [string, string]> = {
  overview: ['reviewed public research snapshots', '已审核的公开研究快照'],
};
