import { lazy, Suspense, useState } from "react";
import { Loading } from "./research-shared";

const MicrocapPage = lazy(() => import("./microcap-page").then((module) => ({ default: module.MicrocapPage })));
const StylePage = lazy(() => import("./style-page").then((module) => ({ default: module.StylePage })));
const CashflowPage = lazy(() => import("./cashflow-page").then((module) => ({ default: module.CashflowPage })));
const LiquidityPage = lazy(() => import("./liquidity-page").then((module) => ({ default: module.LiquidityPage })));

export type ResearchRouteKey = "cashflow" | "cashflowRecovery" | "microcap" | "microcapRecovery" | "crossMarketLiquidity" | "indices" | "styleFactors" | "liquidity";

export function ResearchRoute({ route }: { route: ResearchRouteKey }) {
  const [microcapScope, setMicrocapScope] = useState<"a-share" | "cross-market">(route === "crossMarketLiquidity" ? "cross-market" : "a-share");
  const page = route === "microcap" || route === "microcapRecovery" || route === "crossMarketLiquidity"
    ? <MicrocapPage scope={microcapScope} onScopeChange={setMicrocapScope}/>
    : route === "styleFactors"
      ? <StylePage scope="barra"/>
      : route === "indices"
        ? <StylePage scope="indices"/>
        : route === "cashflow" || route === "cashflowRecovery"
          ? <CashflowPage/>
          : <LiquidityPage/>;
  return <Suspense fallback={<Loading />}>{page}</Suspense>;
}
