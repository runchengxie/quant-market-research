import json
import pathlib
import re
from datetime import date

p = pathlib.Path(__file__).resolve().parents[1]
c = json.loads((p / "configs/bmll/pilot.json").read_text())
for identifier in [c["catalog"], c["schema"]]:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise ValueError("Invalid catalog/schema identifier")
for symbol in c["symbols"]:
    if not re.fullmatch(r"[A-Za-z0-9.\-]+", symbol):
        raise ValueError("Invalid pilot symbol")
for day in c["baseline_dates"] + c["comparison_dates"]:
    date.fromisoformat(day)
prefix = c["catalog"] + "." + c["schema"]
dates = ",".join("DATE '" + d + "'" for d in c["baseline_dates"] + c["comparison_dates"])
syms = ",".join("'" + s + "'" for s in c["symbols"])
ref = f"SELECT reference_date,ticker,instrument_id,listing_id,instrument_type FROM {prefix}.reference_prod WHERE reference_date IN ({dates}) AND ticker IN ({syms}) AND mic='@SIP' AND is_alive"
(p / "sql/bmll/reference.sql").write_text(ref + " ORDER BY reference_date,ticker;\n")
trades = f"""WITH ref AS ({ref}), raw AS (
 SELECT r.ticker,r.instrument_type,t.* FROM {prefix}.trades_plus_prod t
 JOIN ref r ON r.reference_date=t.trade_date AND r.listing_id=t.listing_id
 WHERE t.trade_date IN ({dates}) AND t.mic='@SIP'
 AND CAST(t.local_trade_timestamp AS DATE)=t.trade_date
 AND date_format(t.local_trade_timestamp,'HH:mm:ss')>='09:30:00'
 AND date_format(t.local_trade_timestamp,'HH:mm:ss')<'16:00:00'
 AND t.market_state='CONTINUOUS_TRADING'
), marked AS (
 SELECT *,max(CASE WHEN size<0 OR modification_indicator<>'-' THEN 1 ELSE 0 END)
 OVER(PARTITION BY listing_id,trade_date,execution_venue,trade_id) corrected,
 (best_bid_price+best_ask_price)/2 mid,
 CASE aggressor_side WHEN 1 THEN 1 WHEN 2 THEN -1 END direction
 FROM raw
), scored AS (
 SELECT *,price>0 AND size>0 AND corrected=0 AND best_bid_price>0 AND best_ask_price>=best_bid_price valid,
 CASE WHEN hour(local_trade_timestamp)<10 THEN 'open' WHEN hour(local_trade_timestamp)>=15 THEN 'close' ELSE 'middle' END session
 FROM marked
)
SELECT ticker,instrument_type,trade_date,session,count(*) events,sum(size) signed_shares,sum(price*size) signed_notional,
count_if(size<0) cancellation_events,count_if(corrected=1) correction_group_events,
count_if(valid) valid_quote_events,count_if(valid AND direction IS NOT NULL) directional_events,
count_if(valid AND direction IS NULL) unknown_direction_events,
count_if(valid AND direction IS NOT NULL AND post_trade_mid_1000ms>0) markout_1s_events,
count_if(valid AND direction IS NOT NULL AND post_trade_mid_60000ms>0) markout_60s_events,
percentile_approx(CASE WHEN valid THEN price END,0.5) median_price,
percentile_approx(CASE WHEN valid THEN (best_ask_price-best_bid_price)/mid*10000 END,0.5) trade_time_spread_bps,
avg(CASE WHEN valid THEN 2*abs(price-mid)/mid*10000 END) absolute_effective_spread_bps,
avg(CASE WHEN valid AND direction IS NOT NULL THEN 2*direction*(price-mid)/mid*10000 END) signed_effective_spread_bps,
avg(CASE WHEN valid AND direction IS NOT NULL AND post_trade_mid_1000ms>0 THEN direction*(post_trade_mid_1000ms-price)/mid*10000 END) taker_markout_1s_bps,
avg(CASE WHEN valid AND direction IS NOT NULL AND post_trade_mid_60000ms>0 THEN direction*(post_trade_mid_60000ms-price)/mid*10000 END) taker_markout_60s_bps,
percentile_approx(CASE WHEN valid THEN (best_ask_price-best_bid_price)/mid*10000 END,0.95) p95_trade_time_spread_bps
FROM scored GROUP BY ticker,instrument_type,trade_date,session ORDER BY ticker,trade_date,session
"""
(p / "sql/bmll/trades.sql").write_text(trades)
windows = ",".join("('" + n + "','" + a + "','" + b + "')" for n, a, b in c["windows"])
quotes = f"""WITH ref AS ({ref}), windows(label,start_time,end_time) AS (VALUES {windows}),
raw AS (
 SELECT r.ticker,q.trade_date,from_utc_timestamp(q.event_timestamp,'America/New_York') ts,
 q.bid_price,q.ask_price,q.bid_size_shares,q.ask_size_shares,q.bmll_sequence_no
 FROM {prefix}.nbbo_prod q JOIN ref r ON r.reference_date=q.trade_date AND r.listing_id=q.bmll_object_id
 WHERE q.trade_date IN ({dates}) AND q.mic='@SIP'
), spans AS (
 SELECT *,lead(ts,1,CAST(concat(trade_date,' 16:00:00') AS TIMESTAMP)) OVER(PARTITION BY ticker,trade_date ORDER BY ts,bmll_sequence_no) end_ts FROM raw
), clipped AS (
 SELECT *,greatest(ts,CAST(concat(trade_date,' ',start_time) AS TIMESTAMP)) t0,
 least(end_ts,CAST(concat(trade_date,' ',end_time) AS TIMESTAMP)) t1
 FROM spans CROSS JOIN windows
 WHERE end_ts>CAST(concat(trade_date,' ',start_time) AS TIMESTAMP) AND ts<CAST(concat(trade_date,' ',end_time) AS TIMESTAMP)
), weighted AS (
 SELECT *,timestampdiff(MICROSECOND,t0,t1)/1000000.0 seconds,
 greatest(0,timestampdiff(MICROSECOND,t0,least(t1,ts+INTERVAL 60 SECONDS)))/1000000.0 fresh_seconds,
 bid_price>0 AND ask_price>=bid_price valid,
 (ask_price-bid_price)/((ask_price+bid_price)/2)*10000 spread_bps
 FROM clipped WHERE t1>t0
)
SELECT ticker,trade_date,label,sum(seconds) covered_seconds,
sum(CASE WHEN valid THEN seconds ELSE 0 END) valid_seconds,
sum(CASE WHEN valid THEN fresh_seconds ELSE 0 END) fresh60_seconds,
sum(CASE WHEN valid THEN seconds*spread_bps END)/nullif(sum(CASE WHEN valid THEN seconds END),0) tw_spread_bps,
sum(CASE WHEN valid THEN fresh_seconds*spread_bps END)/nullif(sum(CASE WHEN valid THEN fresh_seconds END),0) fresh60_tw_spread_bps,
sum(CASE WHEN valid AND bid_size_shares>=0 THEN seconds*bid_price*bid_size_shares END)/nullif(sum(CASE WHEN valid AND bid_size_shares>=0 THEN seconds END),0) tw_best_bid_dollars,
sum(CASE WHEN valid AND ask_size_shares>=0 THEN seconds*ask_price*ask_size_shares END)/nullif(sum(CASE WHEN valid AND ask_size_shares>=0 THEN seconds END),0) tw_best_ask_dollars,
sum(CASE WHEN valid AND bid_price*bid_size_shares>=1000 THEN seconds ELSE 0 END)/nullif(sum(CASE WHEN valid AND bid_size_shares>=0 THEN seconds END),0) bid_covers_1000_fraction,
sum(CASE WHEN valid AND bid_size_shares>=0 THEN seconds ELSE 0 END) bid_size_seconds,
sum(CASE WHEN valid AND ask_size_shares>=0 THEN seconds ELSE 0 END) ask_size_seconds,
sum(CASE WHEN valid AND bid_price*bid_size_shares>=10000 THEN seconds ELSE 0 END)/nullif(sum(CASE WHEN valid AND bid_size_shares>=0 THEN seconds END),0) bid_covers_10000_fraction
FROM weighted GROUP BY ticker,trade_date,label ORDER BY ticker,trade_date,label
"""
(p / "sql/bmll/quotes.sql").write_text(quotes)
