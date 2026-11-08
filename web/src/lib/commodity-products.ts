export function selectProductCases(products:Record<string,{cases:any[]}>,state:{fee:string;cash:string;basis:string}){
 if(!['0','10','50'].includes(state.fee)||!['0','0.5'].includes(state.cash)||!['market','nav'].includes(state.basis))throw new Error('unsupported product selection');
 return Object.entries(products).flatMap(([product,r])=>r.cases.filter(x=>x.fee_bps_per_side===Number(state.fee)&&x.cash_shibor_fraction===Number(state.cash)&&x.basis===state.basis).map(x=>({product,...x})));
}
