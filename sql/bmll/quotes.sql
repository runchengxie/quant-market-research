WITH ref AS (SELECT reference_date,ticker,instrument_id,listing_id,instrument_type FROM bmll_data_feed.market_data.reference_prod WHERE reference_date IN (DATE '2025-03-18',DATE '2025-03-19',DATE '2025-04-03',DATE '2025-04-04',DATE '2025-04-07',DATE '2025-04-08',DATE '2025-04-09') AND ticker IN ('AVIR','AWRE','DOW','HCSG','IDYA','INTT','KOSS','NDSN','OFIX','REKR','IWM','SPY') AND mic='@SIP' AND is_alive), windows(label,start_time,end_time) AS (VALUES ('open','09:30:00','10:00:00'),('midday','11:00:00','11:30:00'),('close','15:30:00','16:00:00')),
raw AS (
 SELECT r.ticker,q.trade_date,from_utc_timestamp(q.event_timestamp,'America/New_York') ts,
 q.bid_price,q.ask_price,q.bid_size_shares,q.ask_size_shares,q.bmll_sequence_no
 FROM bmll_data_feed.market_data.nbbo_prod q JOIN ref r ON r.reference_date=q.trade_date AND r.listing_id=q.bmll_object_id
 WHERE q.trade_date IN (DATE '2025-03-18',DATE '2025-03-19',DATE '2025-04-03',DATE '2025-04-04',DATE '2025-04-07',DATE '2025-04-08',DATE '2025-04-09') AND q.mic='@SIP'
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
