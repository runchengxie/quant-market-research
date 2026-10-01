import os from "node:os";
import path from "node:path";

export function resolveMarketResearchOutputRoot({ env = process.env, home = os.homedir() } = {}) {
  if (env.MARKET_RESEARCH_OUTPUT_ROOT) {
    return path.resolve(env.MARKET_RESEARCH_OUTPUT_ROOT);
  }

  const quantDataRoot = env.QUANT_DATA_ROOT || path.join(home, "data", "quant");
  return path.join(quantDataRoot, "quant-market-research", "outputs");
}
