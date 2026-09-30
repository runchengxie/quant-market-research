import { useEffect, useState } from "react";
import { applyTheme, persistThemeChoice, readThemeChoice, type ThemeChoice } from "../../theme";

const choices: ThemeChoice[] = ["system", "light", "dark"];
const labels: Record<"en-US" | "zh-CN", Record<ThemeChoice, string>> = {
  "en-US": { system: "System", light: "Light", dark: "Dark" },
  "zh-CN": { system: "跟随系统", light: "浅色", dark: "深色" },
};

export default function ThemeToggle() {
  const [choice, setChoice] = useState<ThemeChoice>("system");
  const [locale, setLocale] = useState<"en-US" | "zh-CN">("en-US");

  useEffect(() => {
    setLocale(document.documentElement.lang === "zh-CN" ? "zh-CN" : "en-US");
    const storedChoice = readThemeChoice(window.localStorage);
    setChoice(storedChoice);
    applyTheme(storedChoice, window.matchMedia("(prefers-color-scheme: dark)").matches, document.documentElement);
  }, []);

  function cycleTheme() {
    const next = choices[(choices.indexOf(choice) + 1) % choices.length];
    setChoice(next);
    persistThemeChoice(window.localStorage, next);
    applyTheme(next, window.matchMedia("(prefers-color-scheme: dark)").matches, document.documentElement);
  }

  const label = labels[locale][choice];
  const text = locale === "en-US" ? `Theme: ${label}` : `主题：${label}`;
  const ariaLabel = locale === "en-US" ? `Theme: ${label}` : `切换主题，当前为${label}`;
  return <button className="theme-toggle" type="button" onClick={cycleTheme} aria-label={ariaLabel}>{text}</button>;
}
