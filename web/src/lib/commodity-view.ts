export type CommodityState={policy:string;weight:string;horizon:string};
export function commoditySelection<T>(cases:Record<string,T>, state:CommodityState):T{
 if(!['monthly','annual'].includes(state.policy)||!['10','20','30','40'].includes(state.weight)||!['60','120'].includes(state.horizon))throw new Error('unsupported commodity selection');
 const value=cases[`${state.policy}_${state.weight}_${state.horizon}`];
 if(!value)throw new Error('missing reviewed commodity case');
 return value;
}
