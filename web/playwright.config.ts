import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:4321/quant-market-research/",
    trace: "retain-on-failure",
    ...devices["Desktop Chrome"],
  },
  webServer: {
    command: "npm run serve:preview",
    url: "http://127.0.0.1:4321/quant-market-research/",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
