import { extText as t, percent } from '../content/rotation-extension-display';
import type { Metrics } from '../content/rotation-extension';
type Theme = {
    status: string;
    metrics: {
        baseline: Metrics;
        overlay: Metrics;
        difference: {
            total_return_pp: number;
            cagr_pp: number;
        };
    } | null;
};
export default function RotationThemeEvidence({ theme }: {
    theme: Theme;
}) {
    return <div data-testid="theme-evidence"><p>{theme.status === 'diagnostic' ? t('themeDiagnostic') : t('themeBlocked')}</p>
  {theme.status === 'diagnostic' && theme.metrics && <div className="table-scroll"><table><thead><tr><th>{t('configuration')}</th><th>{t('total_return')}</th><th>{t('cagr')}</th><th>{t('max_drawdown')}</th></tr></thead><tbody>{(['baseline', 'overlay'] as const).map(k => <tr key={k}><td>{t(k)}</td><td>{percent(theme.metrics![k].total_return)}</td><td>{percent(theme.metrics![k].cagr)}</td><td>{percent(theme.metrics![k].max_drawdown)}</td></tr>)}</tbody></table></div>}
 </div>;
}
