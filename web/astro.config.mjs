import { defineConfig } from "astro/config";
import react from "@astrojs/react";

export default defineConfig({
  site: "https://runchengxie.github.io",
  base: "/quant-market-research",
  output: "static",
  outDir: "./dist",
  integrations: [react()],
});
