import approved from '../../public/data/microcap_raw_sell_review.json';
import type { LocalText } from './microcap-hub';
import { tAgenda, type AgendaLocale } from './microcap-agenda';

export interface RawSellReview {
 schema_version: number; reviewed_on: string; status: string;
 raw_share_strategy_ready: boolean; new_prospective_observations: number;
 comparison: {noncode_inputs_matched:number; captured_artifacts_matched:number;
  window_targets_calendar_match:boolean; inputs_unchanged:boolean; prior_failure_retained:boolean};
 policy: {explicit_sell_round_lot:number; buy_lot_independent:boolean;
  sell_round_lot_default_is_continuous:boolean; default_compatibility_scope:string;
  full_integer_liquidation_allowed:boolean; adjusted_price_basis_allowed:boolean;
  capacity_weight_ledger_allowed:boolean; fraction_tolerance_cap:number;
  tiny_float_residue_preserved:boolean; capacity_expansion:boolean};
 account: {sessions:number; formations:number; targets_per_formation:number;
  distinct_target_names:number; query_rows_scanned:number; included_actions:number;
  excluded_pre_entry_actions:number; fills:number; buy_fills:number; sell_fills:number;
  all_inventory_integral:boolean; tolerance_cny:number;
  max_errors_cny:{cash:number; marked_value:number; fees:number; identity:number}};
 certification: {full_period:boolean; historical_account:boolean; tax:boolean;
  registrar_holder:boolean; historical_information_set:boolean};
 source_sha256: {account_manifest:string; independent_review:string; prior_failed_receipt:string};
}

const requireReview = (condition:boolean) => {if (!condition) throw new Error('Reviewed replay changed; independent review required');};
const keys = (value:object, expected:string) => requireReview(Object.keys(value).sort().join('|') === expected.split('|').sort().join('|'));
export function validateRawSellReview(value:RawSellReview) {
 keys(value, 'schema_version|reviewed_on|status|raw_share_strategy_ready|new_prospective_observations|comparison|policy|account|certification|source_sha256');
 keys(value.comparison, 'noncode_inputs_matched|captured_artifacts_matched|window_targets_calendar_match|inputs_unchanged|prior_failure_retained');
 keys(value.policy, 'explicit_sell_round_lot|buy_lot_independent|sell_round_lot_default_is_continuous|default_compatibility_scope|full_integer_liquidation_allowed|adjusted_price_basis_allowed|capacity_weight_ledger_allowed|fraction_tolerance_cap|tiny_float_residue_preserved|capacity_expansion');
 keys(value.account, 'sessions|formations|targets_per_formation|distinct_target_names|query_rows_scanned|included_actions|excluded_pre_entry_actions|fills|buy_fills|sell_fills|all_inventory_integral|max_errors_cny|tolerance_cny');
 keys(value.account.max_errors_cny, 'cash|marked_value|fees|identity');
 keys(value.certification, 'full_period|historical_account|tax|registrar_holder|historical_information_set');
 keys(value.source_sha256, 'account_manifest|independent_review|prior_failed_receipt');
 const {account:a, comparison:c, policy:p}=value;
 requireReview(value.schema_version===1 && value.status==='bounded_account_reconciled' && value.raw_share_strategy_ready===false && value.new_prospective_observations===0);
 requireReview(/^\d{4}-\d{2}-\d{2}$/.test(value.reviewed_on));
 requireReview(Object.values(value.certification).every(flag=>flag===false));
 requireReview(Object.values(value.source_sha256).every(hash=>/^[a-f0-9]{64}$/.test(hash)));
 requireReview(c.noncode_inputs_matched===57 && c.captured_artifacts_matched===4 && c.window_targets_calendar_match===true && c.inputs_unchanged===true && c.prior_failure_retained===true);
 requireReview(p.explicit_sell_round_lot===100 && p.buy_lot_independent===true && p.sell_round_lot_default_is_continuous===true && p.default_compatibility_scope==='provider_regression_tests');
 requireReview(p.full_integer_liquidation_allowed===true && p.adjusted_price_basis_allowed===false && p.capacity_weight_ledger_allowed===false && p.fraction_tolerance_cap===1e-8 && p.tiny_float_residue_preserved===true && p.capacity_expansion===false);
 requireReview(a.sessions===21 && a.formations===2 && a.targets_per_formation===40 && a.distinct_target_names===46 && a.query_rows_scanned===2230 && a.included_actions===1 && a.excluded_pre_entry_actions===1);
 requireReview([a.fills,a.buy_fills,a.sell_fills].every(count=>Number.isSafeInteger(count)&&count>=0) && a.fills===a.buy_fills+a.sell_fills && a.sell_fills>0 && a.all_inventory_integral===true);
 requireReview(a.tolerance_cny===1e-7 && Object.values(a.max_errors_cny).every(error=>Number.isFinite(error)&&error>=0&&error<=a.tolerance_cny));
 requireReview(a.max_errors_cny.identity===Math.max(...Object.values(a.max_errors_cny)));
 return value;
}

export const rawSellEvidence = validateRawSellReview(approved);

export const rawSellCopy = {
 navTitle:['Sell-policy review','卖出规则复核'],
 entry:['The same 21-session constructed replay now passes independent quantity and accounting checks under an explicit sell-lot policy. Full-history strategy capacity remains uncertified, and no new prospective observation is added.','同一组 21 个交易日的构造重放，在显式卖出交易单位规则下通过了独立数量与核算检查；完整历史策略容量尚未认证，也没有新增前瞻观察。'],
 evidenceStage:['Bounded accounting passes; full history unverified','有限区间核算通过；完整历史待核验'],
 title:['Sell quantities reconcile in the same bounded account replay','同一区间的账户重放已通过卖出数量与核算检查'],
 conclusion:['The replay passes independent integer-inventory, cash, marked-value and fee checks using the same frozen targets, window and source inputs as the earlier rejected attempt. An explicit sell-lot policy removes that accounting obstacle for this constructed slice. Full-history strategy readiness remains unestablished.', '本轮沿用先前未通过核验时的冻结目标、区间与来源输入，独立的股份整数、现金、持仓计价和费用检查均已通过。显式卖出交易单位规则解决了这个构造区间中的数量核算障碍，完整历史策略仍未达到就绪标准。'],
 reviewed:['Independent review date','独立审阅日期'],
 gatesTitle:['What changed at the acceptance gates?','核验门槛发生了什么变化？'],
 gatesBoundary:['The 1.0.7 rejection is retained below. Matching the calendar, target definitions, source hashes and captured artifacts makes this an accounting-policy comparison within the same bounded study. It does not recover the original full historical account.', '下方保留 1.0.7 版的拒绝记录。日历、目标定义、来源哈希与捕获制品均已匹配，因此这里比较的是同一有限区间内的核算规则；原始完整历史账户仍未找回。'],
 scopeTitle:['The constructed slice and its fills','构造区间与成交范围'],
 scopeBoundary:['The replay starts from assumed cash, follows two frozen formations and includes one in-window action while excluding one pre-entry action. It checks the entire selected slice together; these are constructed account records rather than observed broker fills.', '重放从假设现金开始，跟踪两次冻结目标，纳入一项区间内事件并排除一项入场前事件，统一核对所选区间的账户记录。这些是构造账户记录，不是观察到的券商成交。'],
 errorsTitle:['Independent reconciliation with the original tolerance','按原有容差进行独立对账'],
 errorsBoundary:['Each number is the largest absolute reconciliation residual in CNY. The existing 1e-7 tolerance is unchanged. Share quantities pass independent integer and lot checks at the stated precision; tiny floating-point residues are preserved rather than rounded away.', '下表给出各项以元计的最大绝对核算残差，沿用原有 1e-7 容差。股份数量在注明精度下通过独立整数与交易单位检查；微小浮点残差继续保留，没有通过取整抹去。'],
 policyTitle:['An explicit policy, with the continuous default preserved','显式规则与保留的连续份额默认模式'],
 policy:['sell_round_lot=100 is opt-in and independent of the buy-side round_lot setting. Partial sells use the configured sell lot; full liquidation can release an integral odd-lot position. Leaving sell_round_lot=None retains the continuous default. Backward compatibility is supported by provider regression tests, not inferred from this replay.', 'sell_round_lot=100 需要显式启用，与买入端 round_lot 设置相互独立。部分卖出按所设交易单位处理，完整清仓可卖出整数零股。sell_round_lot=None 继续使用连续份额默认模式。默认行为的兼容性依据是通用引擎回归测试，不能从本次重放推断。'],
 policyLimits:['The opt-in policy accepts raw or unspecified price basis and rejects explicitly adjusted prices. The capacity/weight-ledger path rejects this policy. Fractional inventory fails closed beyond min(lot_tolerance, 1e-8); preserving tiny residues does not enlarge a capacity budget. This simulation policy does not certify every exchange or board rule.', '该规则接受原始价格或未声明价格口径的输入，拒绝明确声明为复权价格的输入；容量／权重账本路径也拒绝此规则。股份的小数偏差超过 min(lot_tolerance, 1e-8) 时核验即失败，保留微小残差不会扩大容量预算。这项模拟规则不构成对所有交易所及板块规则的认证。'],
 boundaryTitle:['What this changes, and what still needs evidence','哪些判断已有变化，哪些仍需证据'],
 boundary:['The earlier sell-quantity rejection no longer blocks this independently reviewed slice. Full-period accounting, historical information availability, holder allocation and tax remain uncertified, and the original historical account remains unrecovered. No new prospective market observation is added. The seven-notice, six-unknown-inventory and register findings remain the dated 1.0.7 snapshot.', '先前的卖出数量问题已不再阻塞本次经过独立核验的区间。完整区间核算、历史信息可得性、持有人分配与税费仍未认证，原始历史账户仍未找回，也没有新增前瞻市场观察。七份公告、六项未知库存及登记册结论，继续作为注明日期的 1.0.7 版快照保留。'],
 next:['Next, reconcile the full history under an explicit share policy with complete event and settlement evidence. Capacity claims also require calibrated execution costs and market impact; passing this bounded replay does not supply them.', '下一步须在明确的股份规则下，结合完整事件与结算证据核对全部历史。容量判断还需要校准后的执行成本与市场冲击，这次有限区间的核验尚未补齐这些材料。'],
 prior:['Read the retained 1.0.7 rejection and source review','查看保留的 1.0.7 版拒绝记录与来源复查'],
 provenance:['Reviewed aggregate provenance','已审查汇总的来源记录'],
 download:['Download reviewed sell-policy and account aggregates','下载已审查的卖出规则与账户汇总'],
} satisfies Record<string,LocalText>;
const label=(en:string,zh:string,locale:AgendaLocale)=>locale==='zh-CN'?zh:en;
const error=(value:number)=>value===0?'0':value.toExponential(3);
export function rawSellTables(value:RawSellReview,locale:AgendaLocale) {
 const {account:a,comparison:c}=validateRawSellReview(value);
 const metrics:Array<[LocalText,number]>=[
  [['Sessions','交易日数'],a.sessions], [['Frozen formations','冻结目标形成次数'],a.formations],
  [['Target names per formation','每次形成的目标股票数'],a.targets_per_formation],
  [['Distinct target names','不同目标股票总数'],a.distinct_target_names],
  [['Source rows scanned','扫描来源行数'],a.query_rows_scanned],
  [['Included actions','纳入事件'],a.included_actions],
  [['Excluded pre-entry actions','排除的入场前事件'],a.excluded_pre_entry_actions],
  [['Fills','成交笔数'],a.fills], [['Buy fills','买入笔数'],a.buy_fills], [['Sell fills','卖出笔数'],a.sell_fills],
 ];
 const errors:Array<[LocalText,keyof RawSellReview['account']['max_errors_cny']]>=[
  [['Cash','现金'],'cash'],[['Marked holdings value','持仓计价'],'marked_value'],
  [['Fees','费用'],'fees'],[['Largest accounting identity residual','最大核算恒等式残差'],'identity'],
 ];
 return {
  gates:{headers:label('Check|Version 1.0.7 attempt|Reviewed bounded replay','核验项目|1.0.7 版尝试|本次有限区间重放',locale).split('|'), rows:[
   [label('Frozen study inputs','冻结研究输入',locale),label('Coverage recorded','已记录覆盖范围',locale),label(`${c.noncode_inputs_matched} noncode inputs + ${c.captured_artifacts_matched} captured artifacts matched`,`${c.noncode_inputs_matched} 项非代码输入与 ${c.captured_artifacts_matched} 份捕获制品匹配`,locale)],
   [label('Sell quantity contract','卖出数量约定',locale),label('Rejected by independent lot guard','未通过独立交易单位检查',locale),label('Explicit sell lots and integral full liquidation','显式卖出交易单位与整数清仓',locale)],
   [label('Account reconciliation','账户对账',locale),label('NAV withheld','暂不接受净值',locale),label('Passed for the reviewed slice','已通过本次区间核验',locale)],
   [label('Full-history strategy readiness','完整历史策略就绪',locale),label('Unestablished','尚未确立',locale),label('Still unestablished','仍未确立',locale)],
  ]},
  scope:{headers:label('Reviewed measure|Count','核验项目|数量',locale).split('|'),rows:metrics.map(([name,count])=>[tAgenda(name,locale),String(count)])},
  errors:{headers:label('Reconciliation check|Maximum residual, CNY|Existing tolerance, CNY','核算项目|最大残差，元|原有容差，元',locale).split('|'),rows:errors.map(([name,key])=>[tAgenda(name,locale),error(a.max_errors_cny[key]),error(a.tolerance_cny)])},
 };
}
const mdTable=(table:{headers:string[];rows:string[][]})=>[table.headers,table.headers.map(()=>'---'),...table.rows].map(row=>`| ${row.map(cell=>cell.replaceAll('|','\\|')).join(' | ')} |`).join('\n');
export function rawSellMarkdown(value:RawSellReview,locale:AgendaLocale) {
 const tables=rawSellTables(value,locale); const t=(key:keyof typeof rawSellCopy)=>tAgenda(rawSellCopy[key],locale);
 return [`## ${t('title')}`,t('conclusion'),`${t('reviewed')}: ${value.reviewed_on}`,
  `### ${t('gatesTitle')}`,mdTable(tables.gates),t('gatesBoundary'),
  `### ${t('scopeTitle')}`,mdTable(tables.scope),t('scopeBoundary'),
  `### ${t('errorsTitle')}`,mdTable(tables.errors),t('errorsBoundary'),
  `### ${t('policyTitle')}`,t('policy'),t('policyLimits'),
  `### ${t('boundaryTitle')}`,t('boundary'),t('next'),
  `[${t('prior')}](https://runchengxie.github.io/quant-market-research/research/microcap/#microcap-chain)`,
  `### ${t('provenance')}`,`[${t('download')}](https://runchengxie.github.io/quant-market-research/data/microcap_raw_sell_review.json)`,
  ...Object.entries(value.source_sha256).map(([role,hash])=>`- ${role}: \`${hash}\``),
 ].join('\n\n');
}
