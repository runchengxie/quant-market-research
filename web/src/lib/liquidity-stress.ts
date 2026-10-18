import { portfolioScenarioRange } from './liquidity-quality';

export function stressBudgets(normal:number|null,low:number|null,participation:number,days:number,holdings:number,minStocks:number) {
 const result=portfolioScenarioRange(normal,low,normal,participation,days,holdings,minStocks);
 return result?{normal:result.selected,stress:result.lower}:null;
}

export function scaleWindowBudget(budget:number,shares:Array<number|null>) {
 if(!Number.isFinite(budget)||budget<0||budget>1e15||shares.some(value=>value==null||!Number.isFinite(value)||value<0||value>1)) return null;
 const values=shares as number[];
 if(values.some((value,index)=>index>0&&value<values[index-1])) return null;
 return values.map(value=>value*budget);
}
