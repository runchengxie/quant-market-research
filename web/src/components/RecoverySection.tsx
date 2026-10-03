import { useEffect, useRef, useState } from 'react';
import { ResearchBarChart } from './ResearchCharts';
import { isRecoverySnapshot, type Snapshot } from './recovery-data';
import { PUBLIC_ROUTES, withBase } from '../lib/routes';
import { publicDataUrl } from '../lib/public-data';
export { isRecoverySnapshot } from './recovery-data';
export type { Snapshot } from './recovery-data';

type Scope = 'cashflow' | 'microcap';
const groups: Record<string, [string, string]> = {cashflow_price: ['现金流 · 价格回报', 'Cash flow · price return'], cashflow_gross_total_return: ['现金流 · 税前全收益', 'Cash flow · gross total return'], microcap_vendor_close: ['微盘与小盘对照 · 供应商点位', 'Micro-cap and small-cap reference · vendor level']};
const seriesNamesEn: Record<string, string> = {
  '399303.SZ': 'SZSE 2000',
  '883418.TI': 'Tonghuashun Micro-cap',
  '931082.CSI': 'CSI A500 Cash Flow',
  '931082CNY010.CSI': 'CSI A500 Cash Flow (gross total return)',
  '932000.CSI': 'CSI 2000',
  '932365.CSI': 'CSI All-Share Cash Flow',
  '932365CNY010.CSI': 'CSI All-Share Cash Flow (gross total return)',
  '932367.CSI': 'CSI 500 Cash Flow',
  '932367CNY010.CSI': 'CSI 500 Cash Flow (gross total return)',
  '932368.CSI': 'CSI 800 Cash Flow',
  '932368CNY010.CSI': 'CSI 800 Cash Flow (gross total return)',
  '932369.CSI': 'CSI 1000 Cash Flow',
  '932369CNY010.CSI': 'CSI 1000 Cash Flow (gross total return)',
  '980092.SZ': 'SZSE Free Cash Flow',
  '8841431.WI': 'Wind Micro-cap',
};
const englishLocale = () => typeof document === 'undefined' || document.documentElement.lang === 'en-US';
const text = (zh: string, en: string) => englishLocale() ? en : zh;
const seriesName = (row: {ts_code: string; name: string}) => englishLocale() ? seriesNamesEn[row.ts_code] ?? row.ts_code : row.name;
const percent = (value: number | null) => value == null || !Number.isFinite(value) ? text('样本不足', 'Insufficient sample') : `${(value * 100).toFixed(2)}%`;
const days = (value: number | null) => value == null ? text('尚无完整记录', 'No complete record') : `${value.toLocaleString(englishLocale() ? 'en-US' : 'zh-CN')} ${text('天', 'days')}`;


export default function RecoverySection({scope}: {scope: Scope}) {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    fetch(publicDataUrl('research/recovery.json', import.meta.env?.BASE_URL ?? '/'), {signal: controller.signal}).then(response => {
      if (!response.ok) throw new Error('Recovery snapshot unavailable');
      return response.json();
    }).then(value => {
      if (!isRecoverySnapshot(value)) throw new Error('Invalid recovery snapshot');
      setSnapshot(value);
    }).catch(error => { if (error.name !== 'AbortError') setError(true); });
    return () => controller.abort();
  }, []);
  if (error) return <section className="panel" role="alert"><h3>{text('回本与持有期风险', 'Recovery and holding-period risk')}</h3><p>{text('回本数据加载失败，请刷新重试。', 'Recovery data failed to load. Refresh and retry.')}</p></section>;
  if (!snapshot) return <section className="panel" role="status">{text('正在加载回本与持有期风险研究…', 'Loading recovery and holding-period risk research…')}</section>;
  return <RecoveryContent key={scope} scope={scope} snapshot={snapshot}/>;
}

export function RecoveryContent({scope, snapshot}: {scope: Scope; snapshot: Snapshot}) {
  const section = useRef<HTMLElement>(null);
  useEffect(() => {
    const scrollToRecovery = () => {
      if (window.location.hash === `#${scope}-recovery`) section.current?.scrollIntoView({block: 'start'});
    };
    scrollToRecovery();
    window.addEventListener('hashchange', scrollToRecovery);
    return () => window.removeEventListener('hashchange', scrollToRecovery);
  }, [scope, snapshot]);
  const [group, setGroup] = useState(scope === 'microcap' ? 'microcap_vendor_close' : 'cashflow_price');
  const [code, setCode] = useState(scope === 'microcap' ? '883418.TI' : '932368.CSI');
  const issues = snapshot.issues.filter(row => !row.group || row.group === group);
  const rows = issues.length ? [] : snapshot.series.filter(row => row.group === group);
  const selected = rows.find(row => row.ts_code === code) ?? rows[0];
  const choices = Object.entries(groups).filter(([key]) => scope === 'microcap' ? key === 'microcap_vendor_close' : key.startsWith('cashflow_'));
  const excluded = snapshot.excluded.filter(row => row.group === group);
  const sorted = selected ? [...selected.episodes].sort((a, b) => b.calendar_days - a.calendar_days) : [];
  // Keep ongoing episodes visible even when they are shorter than the top ten.
  const episodes = sorted.filter((row, index) => index < 10 || row.censored);
  const chartRows = [...episodes].reverse().map(row => ({label: `${row.peak_date}${row.censored ? text('（未回本）', ' (not recovered)') : text('（已回本）', ' (recovered)')}`, days: String(row.calendar_days)}));
  return <section ref={section} id={scope === 'cashflow' ? 'cashflow-recovery' : 'microcap-recovery'} className="recovery-section" aria-label={text('回本与持有期风险', 'Recovery and holding-period risk')}>
    <div className="section-heading"><h3>{text('回本与持有期风险', 'Recovery and holding-period risk')}</h3><p>{text('买入后多久能回本，长期持有又可能遇到什么风险？', 'How long does recovery take after entry, and what risks emerge over a long holding period?')}</p></div>
    <div className="panel">
      <div className="control-bar" aria-label={text('回本研究口径', 'Recovery research basis')}>{choices.map(([value]) => <button key={value} className={`choice ${group === value ? 'active' : ''}`} aria-pressed={group === value} onClick={() => setGroup(value)}>{groups[value][englishLocale() ? 1 : 0]}</button>)}</div>
      <p className="panel-note">{text('这里使用下列完整样本期，与其他图表的短期收益窗口分别查看。', 'This section uses the complete sample window separately from short-term return charts.')}{selected ? `${text('样本', 'Sample')} ${selected.start} ${text('至', 'to')} ${selected.end}${englishLocale() ? ', ' : '，'}${selected.observations.toLocaleString(englishLocale() ? 'en-US' : 'zh-CN')} ${text('个交易日观测。', 'trading-day observations.')} ` : ''}{text('这里按自然日计算指数低于此前高点的时间。样本结束时仍未回到高点的记录，只能说至少持续了这么久；之后何时回本还不知道（右删失）。', 'Duration is measured in calendar days below a previous high. If the index has not recovered by the end of the sample, we only know it lasted at least this long; the eventual recovery date is unknown (right-censored).')}</p>
      <p className="panel-note">{group === 'cashflow_price' ? text('价格回报不含分红。', 'Price returns exclude dividends.') : group === 'cashflow_gross_total_return' ? text('税前全收益计入分红再投资，分红计算沿用数据提供方的结果。', 'Gross total return includes reinvested dividends, using the data provider’s dividend calculations.') : text('分红口径还需核对。中证2000和国证2000用于观察规模稍大的小盘股。', 'Dividend treatment still needs review. CSI 2000 and Guozheng 2000 provide reference series for somewhat larger small-cap stocks.')} {text('统计未计税费、通胀和机会成本。部分历史由指数发布方事后计算，实际投资结果可能不同。', 'The statistics exclude taxes and fees, inflation, and opportunity costs. Some historical data was calculated retrospectively by index publishers, so actual investment results may differ.')}</p>
      {issues.length > 0 && <p role="status">{text('部分数据未通过检查，本次暂停展示。', 'Some data failed validation and is withheld.')} {issues.map(row => <code key={row.status}>{row.status}</code>)}</p>}
      {excluded.length > 0 && <p className="panel-note">{text('未纳入：', 'Excluded: ')}{excluded.map(row => `${seriesName(row)} (${row.status === 'missing' ? text('缺少日线', 'missing daily data') : text('未通过校验', 'validation failed')})`).join(text('、', ', '))}{englishLocale() ? '.' : '。'}</p>}
      {group === 'microcap_vendor_close' && <p className="panel-note">{text('自制400股版本缺少部分持仓报价，收益需要重算。本节回本统计暂不纳入这一版本。万得微盘目前只有年度资料，还不足以计算日频回本等待。', 'The 400-stock reconstruction has missing holding prices and requires recomputation. It is excluded here; the vendor micro-cap series has only annual data, which is insufficient for daily recovery timing.')}</p>}
      {!selected ? <p role="status">{text('暂无通过校验的回本数据，请查看数据检查结果。', 'No validated recovery data is available. Review the data checks.')}</p> : <>
        <div className="table-scroll"><table><caption>{text('历史最长与当前等待', 'Historical maximum and current wait')} · {groups[group][englishLocale() ? 1 : 0]}</caption><thead><tr><th>{text('指数', 'Index')}</th><th>{text('最长已完成', 'Longest completed')}</th><th>{text('最长已观察', 'Longest observed')}</th><th>{text('当前水下期', 'Current underwater period')}</th><th>{text('回本所需涨幅', 'Gain needed to recover')}</th><th>{text('样本区间', 'Sample window')}</th></tr></thead><tbody>{rows.map(row => <tr key={row.ts_code}><td>{seriesName(row)}</td><td>{days(row.longest_completed_underwater_calendar_days)}</td><td>{days(row.longest_observed_underwater_calendar_days)}</td><td>{row.currently_underwater ? `${text('至少', 'At least')} ${days(row.current_underwater_calendar_days)}` : text('不在水下', 'Not underwater')}</td><td>{percent(row.gain_needed_to_recover)}</td><td>{row.start} {text('至', 'to')} {row.end}</td></tr>)}</tbody></table></div>
        {<>
          <label className="recovery-selector">{text('查看指数', 'View index')} <select value={selected.ts_code} onChange={event => setCode(event.target.value)}>{rows.map(row => <option key={row.ts_code} value={row.ts_code}>{seriesName(row)}</option>)}</select></label>
          <div className="stat-grid recovery-stats"><Metric label={text('最长已完成水下期', 'Longest completed underwater period')} value={days(selected.longest_completed_underwater_calendar_days)} note={text('从前期高点跌落，到首次恢复的最长记录', 'Longest record from a prior high to first recovery')}/><Metric label={text('当前水下期', 'Current underwater period')} value={selected.currently_underwater ? `${text('至少', 'At least')} ${days(selected.current_underwater_calendar_days)}` : text('不在水下', 'Not underwater')} note={`${text('截至', 'Through')} ${selected.end}${text('，未回本时仅为下界', '; a lower bound while unrecovered')}`}/><Metric label={text('回本所需涨幅', 'Gain needed to recover')} value={percent(selected.gain_needed_to_recover)} note={text('回到样本内历史高点所需涨幅', 'Increase needed to return to the sample high')}/></div>
          <h4>{text('水下区间时长', 'Underwater duration')} · {seriesName(selected)}</h4><p className="panel-note">{text('显示等待最久的10个区间，并保留尚未回本的区间。横轴为自然日，左侧标注前期高点日期。尚未回本的记录只表示截至样本末已等待的时间。', 'Show the 10 longest waits and retain unrecovered intervals. The axis uses calendar days; unrecovered records are measured only through the sample end.')}</p>
          {episodes.length ? <><ResearchBarChart rows={chartRows} labelKey="label" valueKey="days" formatter={value => days(value)}/><div className="table-scroll"><table><caption>{text('水下区间明细', 'Underwater interval detail')}</caption><thead><tr><th>{text('前期高点', 'Prior high')}</th><th>{text('谷底', 'Trough')}</th><th>{text('首次回本或样本末日', 'First recovery or sample end')}</th><th>{text('状态', 'Status')}</th><th>{text('自然日', 'Calendar days')}</th><th>{text('交易日', 'Trading days')}</th><th>{text('区间最大回撤', 'Maximum drawdown')}</th></tr></thead><tbody>{episodes.map(row => <tr key={row.peak_date}><td>{row.peak_date}</td><td>{row.trough_date}</td><td>{row.recovery_date ?? row.observed_until}</td><td>{row.censored ? text('尚未回本', 'Not recovered') : text('已回本', 'Recovered')}</td><td>{row.censored ? `${text('至少', 'At least')} ` : ''}{days(row.calendar_days)}</td><td>{row.trading_sessions}</td><td>{percent(row.max_drawdown)}</td></tr>)}</tbody></table></div></> : <p>{text('样本内未观察到水下区间。', 'No underwater interval was observed in the sample.')}</p>}
          <h4>{text('固定持有期的历史结果', 'Historical results by fixed holding period')}</h4><p className="panel-note">{text('分别观察买入后1年、3年、5年和10年的结果。期限未满的记录单列。历史亏损比例只计算期限已满的记录，供回顾历史时参考。', 'Review results after 1, 3, 5, and 10 years. Immature observations are shown separately; loss rates use only mature observations.')}</p>
          <div className="table-scroll"><table><caption>{text('持有期统计', 'Holding-period statistics')} · {seriesName(selected)}</caption><thead><tr><th>{text('持有年数', 'Years')}</th><th>{text('期限已满', 'Mature')}</th><th>{text('期限未满', 'Immature')}</th><th>{text('历史亏损比例', 'Historical loss rate')}</th><th>{text('最差收益', 'Worst return')}</th><th>{text('中位收益', 'Median return')}</th></tr></thead><tbody>{selected.horizons.map(row => <tr key={row.years}><td>{row.years} {text('年', 'years')}</td><td>{row.mature_entries}</td><td>{row.immature_entries}</td><td>{percent(row.loss_fraction)}</td><td>{percent(row.worst_return)}</td><td>{percent(row.median_return)}</td></tr>)}</tbody></table></div>
          <details className="recovery-entries"><summary>{text('等待最久的买入日（最多 20 条）', 'Longest entry waits (up to 20)')}</summary><p className="panel-note">{text('首次回本不保证此后一直盈利。最后一个买入日没有后续观测，也标记未回本。', 'First recovery does not guarantee continued profit. The final entry has no later observation and is marked unrecovered.')}</p><div className="table-scroll"><table><thead><tr><th>{text('买入日', 'Entry date')}</th><th>{text('首次回本或样本末日', 'First recovery or sample end')}</th><th>{text('自然日', 'Calendar days')}</th><th>{text('交易日', 'Trading days')}</th><th>{text('回本前最差收益', 'Worst return before recovery')}</th><th>{text('状态', 'Status')}</th></tr></thead><tbody>{selected.entries.map(row => <tr key={row.entry_date}><td>{row.entry_date}</td><td>{row.breakeven_date ?? row.observed_until}</td><td>{row.censored ? `${text('至少', 'At least')} ` : ''}{days(row.calendar_days)}</td><td>{row.trading_sessions}</td><td>{percent(row.worst_return_before_breakeven)}</td><td>{row.censored ? text('尚未回本', 'Not recovered') : text('已回本', 'Recovered')}</td></tr>)}</tbody></table></div></details>
        </>}
      </>}
      <details className="recovery-method"><summary>{text('计算方法与阅读提示', 'Method and reading notes')}</summary>
        <p>{text('水下期从前期高点算起，到指数首次恢复至该高点为止，达到相同点位就算回本。自然日是两个日期相差的天数，交易日数按两个日期之间相隔的交易日计算。', 'An underwater period starts at a prior high and ends when the index first returns to that level. Calendar days are the difference between the dates; trading sessions count market sessions between them.')}</p>
        <p>{text('最长已完成统计已回本的区间。最长已观察也包括尚未回本的区间。尚未回本时，等待天数只是当前记录，未来还可能继续增加。', 'The longest completed period includes only recovered intervals. The longest observed period also includes unrecovered intervals. For an unrecovered interval, the wait is measured only through the sample end and may continue to grow.')}</p>
        <p>{text('逐日买入统计从买入后的下一个交易日起寻找首次回本日期。样本最后一天没有后续数据，也记为尚未回本。回本后仍可能再次亏损。', 'For each daily entry, the first recovery date is searched from the next trading session onward. An entry on the final sample day has no later observation and is marked unrecovered. Recovery does not rule out later losses.')}</p>
        <p>{text('固定持有期在买入日满1年、3年、5年或10年后的首个交易日计算，周年当天开市就采用当天。期限未满时显示样本不足。相邻买入日的持有期高度重叠，历史亏损比例不能直接用来预测未来。', 'Fixed holding periods use the first trading session on or after the 1-, 3-, 5-, or 10-year anniversary; if the market is open on the anniversary, that session is used. Immature periods are marked as insufficient. Adjacent entries have heavily overlapping holding periods, so historical loss rates are not forecasts.')}</p>
        <p>{text('回本所需涨幅等于前期高点除以当前点位，再减1。例如下跌50%后，需要上涨100%才能回本。', 'The gain needed to recover is the prior high divided by the current level, minus one. For example, a 50% loss requires a 100% gain to break even.')}</p>
        <p>{text('样本开始前的高点无法识别。历史最长等待不保证未来也能在同样时间内回本。价格指数不含分红，税前全收益计入分红再投资。税费、通胀、机会成本和实际买卖限制尚未计入。', 'Highs before the sample are not observable. The longest historical wait does not guarantee recovery within the same period in the future. Price indices exclude dividends; gross total return includes reinvested dividends. Taxes, inflation, opportunity cost, and practical trading constraints are not included.')}</p>
        <p>{text('来源为 Tushare 指数日线，交易日期已按上交所日历检查。这里只展示计算后的统计，完整输入和检查记录保存在研究环境中。', 'The source is Tushare index daily data, and trading dates were checked against the Shanghai Stock Exchange calendar. This page shows derived statistics; full inputs and audit records remain in the research environment.')}</p>
      </details>
      <p className="panel-note"><a href={scope === 'cashflow' ? `${withBase(PUBLIC_ROUTES.microcap, import.meta.env?.BASE_URL ?? '/')}#microcap-recovery` : withBase(PUBLIC_ROUTES.cashflowRecovery, import.meta.env?.BASE_URL ?? '/')}>{text('查看', 'View ')}{text(scope === 'cashflow' ? '小微盘' : '现金流', scope === 'cashflow' ? 'micro-cap' : 'cash-flow')}{text('回本研究 ↗', ' recovery research ↗')}</a></p>
    </div>
  </section>;
}

function Metric({label, value, note}: {label: string; value: string; note: string}) {
  return <article className="stat"><span>{label}</span><strong>{value}</strong><small>{note}</small></article>;
}
