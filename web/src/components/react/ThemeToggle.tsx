import { useEffect, useState } from "react";
import { applyTheme, persistThemeChoice, readThemeChoice, type ThemeChoice } from "../../theme";

const choices: ThemeChoice[] = ["system", "light", "dark"];
const labels: Record<ThemeChoice, string> = { system: "跟随系统", light: "浅色", dark: "深色" };

export default function ThemeToggle() {
  const [choice, setChoice] = useState<ThemeChoice>("system");

  useEffect(() => {
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

  return <button className="theme-toggle" type="button" onClick={cycleTheme} aria-label={`切换主题，当前为${labels[choice]}`}>主题：{labels[choice]}</button>;
}
