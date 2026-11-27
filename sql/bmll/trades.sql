WITH ref AS (SELECT reference_date,ticker,instrument_id,listing_id,instrument_type FROM bmll_data_feed.market_data.reference_prod WHERE reference_date IN (DATE '2025-03-18',DATE '2025-03-19',DATE '2025-04-03',DATE '2025-04-04',DATE '2025-04-07',DATE '2025-04-08',DATE '2025-04-09') AND ticker IN ('AVIR','AWRE','DOW','HCSG','IDYA','INTT','KOSS','NDSN','OFIX','REKR','IWM','SPY') AND mic='@SIP' AND is_alive), raw AS (
 SELECT r.ticker,r.instrument_type,t.* FROM bmll_data_feed.market_data.trades_plus_prod t
 JOIN ref r ON r.reference_date=t.trade_date AND r.listing_id=t.listing_id
 WHERE t.trade_date IN (DATE '2025-03-18',DATE '2025-03-19',DATE '2025-04-03',DATE '2025-04-04',DATE '2025-04-07',DATE '2025-04-08',DATE '2025-04-09') AND t.mic='@SIP'
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
