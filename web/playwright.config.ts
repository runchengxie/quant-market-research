import { defineConfig, devices } from "@playwright/test";

const port = process.env.PORT ?? "4321";
const baseURL = `http://127.0.0.1:${port}/quant-market-research/`;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL,
    trace: "retain-on-failure",
    ...devices["Desktop Chrome"],
  },
  webServer: {
    command: "npm run serve:preview",
    url: baseURL,
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
