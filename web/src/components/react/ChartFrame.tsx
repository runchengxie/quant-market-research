import type { ReactNode } from 'react';
import type { ChartMeta } from '../../lib/chart-presentation';

export type ChartFrameProps = ChartMeta & { children: ReactNode; data?: ReactNode };

export default function ChartFrame({ id, title, unit, sample, boundary, explanation, methodHref, children, data }: ChartFrameProps) {
  return <section className="chart-frame" id={id} aria-labelledby={`${id}-title`}>
    <header className="chart-frame-header"><div><h2 id={`${id}-title`}>{title}</h2><p>{explanation}</p></div><span className="chart-unit">{unit}</span></header>
    <div className="chart-frame-plot">{children}</div>
    <div className="chart-frame-meta"><span>样本：{sample}</span><span>边界：{boundary}</span>{methodHref && <a href={methodHref}>查看方法</a>}</div>
    {data && <details className="chart-frame-values"><summary>查看数值</summary>{data}</details>}
  </section>;
}
