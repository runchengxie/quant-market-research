/** Arithmetic scenarios, not empirical estimates. Rates are decimal fractions. */
export function annualCost(buyTurnover: number, sellTurnover: number, slippageBp: number, days = 250) {
  if (![buyTurnover, sellTurnover, slippageBp, days].every(Number.isFinite) || [buyTurnover, sellTurnover, slippageBp, days].some(v => v < 0)) throw new RangeError("Cost inputs must be finite and nonnegative");
  return days * (buyTurnover * (1 + slippageBp) + sellTurnover * (6 + slippageBp)) / 10000;
}
export const costScenarios = [0, 1, 3, 5, 10].map(bp => ({ bp, oneWay: annualCost(.6, .6, bp), twoWay: annualCost(.3, .3, bp) }));
