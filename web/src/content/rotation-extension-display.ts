import { extensionCopy, codeCopy } from './rotation-extension-copy';
import { weeklyRows, type Copy } from './rotation-research';
export const isEnglish = () => typeof document === 'undefined' || document.documentElement.lang !== 'zh-CN';
export const localized = (v: Copy) => v[isEnglish() ? 0 : 1];
export const extText = (key: keyof typeof extensionCopy) => localized(extensionCopy[key]);
export const codeText = (code: string) => codeCopy[code] ? localized(codeCopy[code]) : extText('unavailable');
export const experimentText = (id: string) => { const row = weeklyRows.find(r => r.id === id); return row ? localized(row.label) : id; };
export const percent = (value: number | null) => value === null ? '—' : new Intl.NumberFormat(isEnglish() ? 'en-US' : 'zh-CN', { style: 'percent', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
export const decimal = (value: number | null) => value === null ? '—' : new Intl.NumberFormat(isEnglish() ? 'en-US' : 'zh-CN', { maximumFractionDigits: 3 }).format(value);
export const dateText = (value: string) => new Intl.DateTimeFormat(isEnglish() ? 'en-US' : 'zh-CN', { timeZone: 'UTC', year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(value.length === 10 ? `${value}T00:00:00Z` : value));
export function windowText(id: string) {
    if (id === 'common' || id === 'last_252' || id === 'last_756')
        return extText(id);
    if (id.startsWith('year_'))
        return `${extText('year')} ${id.slice(5)}`;
    const match = /^rolling_(252|756)_(.+)$/.exec(id);
    return match ? `${match[1]} · ${extText('rolling')} ${dateText(match[2])}` : id;
}
