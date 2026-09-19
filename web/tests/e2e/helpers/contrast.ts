export function contrastRatio(foreground: string, background: string): number {
  const parse = (value: string) => (value.match(/\d+(?:\.\d+)?/g) ?? []).slice(0, 3).map(Number).map((channel) => { const c = channel / 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; });
  const luminance = (value: string) => { const [r, g, b] = parse(value); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const a = luminance(foreground); const b = luminance(background); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}
