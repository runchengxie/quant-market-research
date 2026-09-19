import { defineConfig } from "astro/config";
import react from "@astrojs/react";

export default defineConfig({
  site: "https://runchengxie.github.io",
  base: "/quant-market-research",
  output: "static",
  outDir: "./dist",
  integrations: [react()],
  // React 18's Node pipeable renderer can emit NULs at UTF-8 chunk edges.
  // Keep streaming/Suspense and identifierPrefix, using its Web Streams renderer.
  // https://github.com/react/react/issues/31134
  vite: {
    resolve: {
      alias: [{ find: /^react-dom\/server$/, replacement: "react-dom/server.browser" }],
    },
  },
});
