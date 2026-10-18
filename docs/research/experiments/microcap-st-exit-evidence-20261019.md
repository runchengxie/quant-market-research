# ST paired monthly comparison: missing exit evidence (2026-10-19)

The 235 failed selected rows represent 107 formation/issuer events. **Zero events were restored.** All 50 missing entry rows match dated suspensions. Of 220 missing endpoint rows, 205 match dated suspensions; the remaining 15 are five terminal events repeated across N=50/100/200. Suspension matches corroborate absence using the same provider; they do not establish fills. Baskets, dates, weights and returns remain unchanged. There is no new executable return or NAV.

This supplements the [original monthly study](microcap-st-paired-short-window-20261018.md). Complete pairs remain 15/13/9 out of 36 months for N=50/100/200, with mean include-minus-exclude differences of +0.202/−0.514/−1.028 percentage points. On the common nine months they remain −0.752/−0.927/−1.028 points. The N50 sign reversal illustrates conditional sample selection. Inputs remain retrospective 2026 snapshots with `revision_safe=false`.

## Five terminal events

|Formation|Security|Scheduled entry → endpoint|Last clean trade date, context only|Remaining blocker|
|---|---|---|---|---|
|20230131|600260 Kaile|20230201 → 20230301|20230202|Entry observed; terminal endpoint without verified settlement|
|20230228|600311 Ronghua|20230301 → 20230403|20230302|Entry observed; terminal endpoint without verified settlement|
|20250331|600070 Furun|20250401 → 20250506|20250410|Entry observed; terminal endpoint without verified settlement|
|20250331|300117 Jiayu|20250401 → 20250506|20250331|Entry already suspended; terminal endpoint|
|20250331|000040 Dongxu Azure|20250401 → 20250506|20250331|Entry already suspended; terminal endpoint|

The SSE decisions for [600260](https://www.sse.com.cn/disclosure/announcement/listing/stock/c/c_20230208_88298117.shtml), [600311](https://www.sse.com.cn/disclosure/announcement/listing/stock/c/c_20230320_88719293.shtml), and [600070](https://www.sse.com.cn/disclosure/announcement/listing/stock/c/c_20250428_10777920.shtml) establish trading-triggered termination without a delisting trading period and require arrangements for subsequent share transfer. They provide neither a tradable scheduled endpoint quote nor a cash settlement amount.

Jiayu's [delisting notice](https://static.cninfo.com.cn/finalpage/2025-04-29/1223411144.PDF) confirms April 30 removal, while its [April 1 notice](https://static.cninfo.com.cn/finalpage/2025-04-01/1222971960.PDF) states suspension starts at that day's open. Dongxu Azure's [issuer notice](https://disc.static.szse.cn/download/disc/disk03/finalpage/2025-04-30/c0354752-af8d-457d-996f-5e87ed3aff35.PDF) confirms April 30 removal and no delisting trading period. Its documents give differing decision/receipt/republication dates (April 25/28/29); those source differences are retained. They do not change the missing entry and endpoint evidence.

A last trade is not a prespecified exit. Share transfer is not cash repayment. Future transfer quotes, compensation terms or registration documents cannot be stitched into this protocol automatically. A separate protocol would need raw prices, share entitlements, successor securities and cash accounting, dated availability and execution rules. Terminal value alone cannot restore Jiayu or Dongxu Azure because their scheduled entries were already suspended.

## Beijing exchange identity checks

Four formation/issuer events initially lacked direct suspension matches: two for Guoyi and two for Guangdao. The [BSE code mapping](https://www.bse.cn/service/code_mapping.html) establishes 831039→920039 and 839680→920680. The owner's dated suspension table records S for 831039 on 20230301 and for 839680 on 20250701 and 20250901. The alias is used only to join suspension evidence. All four remain blocked; no price is substituted. Guoyi's [March 7, 2023 notice](https://www.bse.cn/disclosure/2023/2023-03-07/883fba82651a40a691f6d47e3a4733bd.pdf) also documents the March 1 suspension and its continuation.

## Reproduction and limits

`audit_st_paired_exits.py` verifies the frozen selection audit SHA256, then produces the 235 selected rows, 107 distinct events, five terminal evidence matches and an input/output hash receipt. It preserves both basket code and suspension evidence code. Resume (R) events never count as suspension (S); absence of S never proves tradability. See the [reviewed facts](st-exit-reviewed-facts-20261019.json) and the complete event inventory below. CSVs are retained in a dedicated external task directory; frozen outputs and shared aliases were not changed.

Run with the existing project Python environment (new uv environment downloads were blocked by the network sandbox), resolving DATA_ROOT from local workspace settings:

```bash
python scripts/audit_st_paired_exits.py \
  --source "$DATA_ROOT/quant/quant-market-research/research/st-paired-short-20261018/monthly-v1" \
  --suspensions "$DATA_ROOT/quant/quant-market-data-platform/assets/tushare/a_share/suspend_d_20260917/suspend_d.parquet" \
  --facts docs/research/experiments/st-exit-reviewed-facts-20261019.json \
  --output "$DATA_ROOT/quant/quant-market-research/research/st-exit-evidence-20261019/monthly-v2"
```

The output directory must be new. Existing owner terminal-document facts cover only 000562 and 601268, neither matching this sample. No new provider API was called; this audit does not certify comprehensive corporate-action coverage or account settlement. Every failed row remains unresolved, without zero, total-loss, stale-price or future-constituent substitution.

<details>
<summary>107 formation / issuer events · 107条形成日/发行人事件</summary>

|Formation|Entry|Endpoint|Security|N|Arms|Missing|Terminal|
|---|---|---|---|---|---|---|---|
|20230131|20230201|20230301|002499.SZ|50/100/200|I|end|False|
|20230131|20230201|20230301|600139.SH|100/200|I|end|False|
|20230131|20230201|20230301|600260.SH|50/100/200|I|end|True|
|20230131|20230201|20230301|920039.BJ|100/200|E/I|end|False|
|20230228|20230301|20230403|300309.SZ|200|I|end|False|
|20230228|20230301|20230403|600311.SH|50/100/200|I|end|True|
|20230228|20230301|20230403|920039.BJ|100/200|E/I|entry|False|
|20230331|20230403|20230504|000023.SZ|200|E/I|end|False|
|20230331|20230403|20230504|000150.SZ|200|I|end|False|
|20230331|20230403|20230504|000806.SZ|200|I|end|False|
|20230331|20230403|20230504|002417.SZ|100/200|I|end|False|
|20230331|20230403|20230504|002751.SZ|200|I|end|False|
|20230331|20230403|20230504|002781.SZ|100/200|I|end|False|
|20230331|20230403|20230504|300089.SZ|200|I|end|False|
|20230331|20230403|20230504|300297.SZ|200|I|end|False|
|20230331|20230403|20230504|300392.SZ|200|I|end|False|
|20230331|20230403|20230504|600242.SH|50/100/200|I|end|False|
|20230331|20230403|20230504|600781.SH|100/200|I|end|False|
|20230331|20230403|20230504|603030.SH|200|E/I|end|False|
|20230331|20230403|20230504|688086.SH|50/100/200|I|end|False|
|20230331|20230403|20230504|688555.SH|50/100/200|I|end|False|
|20230428|20230504|20230601|000023.SZ|200|E/I|entry|False|
|20230428|20230504|20230601|000606.SZ|100/200|I|entry,end|False|
|20230428|20230504|20230601|000806.SZ|200|I|entry,end|False|
|20230428|20230504|20230601|002751.SZ|200|I|entry,end|False|
|20230428|20230504|20230601|002781.SZ|50/100/200|I|entry,end|False|
|20230428|20230504|20230601|300089.SZ|50/100/200|I|entry,end|False|
|20230428|20230504|20230601|300273.SZ|200|I|entry,end|False|
|20230428|20230504|20230601|300392.SZ|50/100/200|I|entry,end|False|
|20230428|20230504|20230601|600122.SH|200|I|end|False|
|20230428|20230504|20230601|600242.SH|50/100/200|I|entry|False|
|20230428|20230504|20230601|600781.SH|100/200|I|entry|False|
|20230428|20230504|20230601|603030.SH|200|E/I|entry|False|
|20230531|20230601|20230703|000616.SZ|200|I|end|False|
|20230531|20230601|20230703|000691.SZ|200|E|end|False|
|20230531|20230601|20230703|000732.SZ|200|I|end|False|
|20230531|20230601|20230703|000918.SZ|200|I|entry,end|False|
|20230531|20230601|20230703|002113.SZ|200|I|end|False|
|20230531|20230601|20230703|002118.SZ|200|I|end|False|
|20230531|20230601|20230703|002504.SZ|100/200|I|end|False|
|20230531|20230601|20230703|300163.SZ|200|E|end|False|
|20230531|20230601|20230703|600077.SH|200|I|end|False|
|20230531|20230601|20230703|600393.SH|200|I|end|False|
|20230630|20230703|20230801|300163.SZ|200|E|entry|False|
|20231130|20231201|20240102|002776.SZ|50/100/200|I|end|False|
|20231130|20231201|20240102|600290.SH|50/100/200|I|end|False|
|20231229|20240102|20240201|002740.SZ|50/100/200|I|end|False|
|20240131|20240201|20240301|002089.SZ|200|I|end|False|
|20240131|20240201|20240301|603603.SH|200|I|end|False|
|20240229|20240301|20240401|000005.SZ|200|I|end|False|
|20240329|20240401|20240506|000416.SZ|50/100/200|I|end|False|
|20240329|20240401|20240506|000996.SZ|200|I|end|False|
|20240329|20240401|20240506|002087.SZ|100/200|I|end|False|
|20240329|20240401|20240506|002433.SZ|200|I|end|False|
|20240329|20240401|20240506|002699.SZ|200|I|end|False|
|20240329|20240401|20240506|300282.SZ|50/100/200|I|end|False|
|20240329|20240401|20240506|300742.SZ|50/100/200|I|end|False|
|20240329|20240401|20240506|603133.SH|200|I|end|False|
|20240430|20240506|20240603|300282.SZ|50/100/200|I|entry,end|False|
|20240430|20240506|20240603|300495.SZ|50/100/200|I|end|False|
|20240430|20240506|20240603|300742.SZ|50/100/200|I|entry,end|False|
|20240531|20240603|20240701|000836.SZ|100/200|I|end|False|
|20240531|20240603|20240701|000971.SZ|100/200|I|end|False|
|20240531|20240603|20240701|002288.SZ|200|I|end|False|
|20240531|20240603|20240701|002621.SZ|50/100/200|I|end|False|
|20240531|20240603|20240701|300262.SZ|50/100/200|I|end|False|
|20240531|20240603|20240701|600220.SH|200|I|end|False|
|20240531|20240603|20240701|600836.SH|50/100/200|I|end|False|
|20240628|20240701|20240801|000023.SZ|50/100/200|I|end|False|
|20240628|20240701|20240801|002325.SZ|100/200|I|entry,end|False|
|20240628|20240701|20240801|002341.SZ|200|I|end|False|
|20240628|20240701|20240801|002435.SZ|50/100/200|I|end|False|
|20240628|20240701|20240801|002502.SZ|200|I|end|False|
|20240628|20240701|20240801|600112.SH|50/100/200|I|end|False|
|20240731|20240801|20240902|002308.SZ|100/200|I|end|False|
|20241031|20241101|20241202|000929.SZ|200|E|entry|False|
|20241031|20241101|20241202|002656.SZ|50/100/200|I|end|False|
|20241031|20241101|20241202|600289.SH|100/200|I|end|False|
|20241129|20241202|20250102|002494.SZ|200|E/I|end|False|
|20241231|20250102|20250205|000040.SZ|200|I|end|False|
|20241231|20250102|20250205|600083.SH|50/100/200|I|end|False|
|20241231|20250102|20250205|600898.SH|50/100/200|I|end|False|
|20250127|20250205|20250303|603963.SH|50/100/200|I|end|False|
|20250228|20250303|20250401|300117.SZ|50/100/200|I|end|False|
|20250228|20250303|20250401|300630.SZ|50/100/200|I|end|False|
|20250228|20250303|20250401|605081.SH|50/100/200|E/I|end|False|
|20250331|20250401|20250506|000040.SZ|50/100/200|I|entry,end|True|
|20250331|20250401|20250506|000622.SZ|50/100/200|I|end|False|
|20250331|20250401|20250506|002750.SZ|50/100/200|I|end|False|
|20250331|20250401|20250506|300108.SZ|50/100/200|I|end|False|
|20250331|20250401|20250506|300117.SZ|50/100/200|I|entry,end|True|
|20250331|20250401|20250506|300208.SZ|200|I|end|False|
|20250331|20250401|20250506|600070.SH|50/100/200|I|end|True|
|20250331|20250401|20250506|600387.SH|200|I|end|False|
|20250331|20250401|20250506|600462.SH|50/100/200|I|end|False|
|20250430|20250506|20250603|000622.SZ|50/100/200|I|entry,end|False|
|20250430|20250506|20250603|002199.SZ|100/200|I|end|False|
|20250430|20250506|20250603|300208.SZ|50/100/200|I|entry,end|False|
|20250530|20250603|20250701|300478.SZ|200|E/I|end|False|
|20250530|20250603|20250701|920680.BJ|50/100/200|I|end|False|
|20250731|20250801|20250901|920680.BJ|50/100/200|I|end|False|
|20250829|20250901|20251009|000851.SZ|50/100/200|I|end|False|
|20250829|20250901|20251009|603843.SH|200|I|end|False|
|20251031|20251103|20251201|300379.SZ|50/100/200|I|end|False|
|20251031|20251103|20251201|600200.SH|50/100/200|I|end|False|
|20251031|20251103|20251201|603388.SH|50/100/200|I|end|False|
|20251128|20251201|20260105|920641.BJ|50/100/200|E/I|end|False|

I = include ST; E = exclude ST. Both arms retain original equal weights. / I为包含ST，E为排除ST，均保留原等权。

</details>
