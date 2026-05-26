CREATE DATABASE IF NOT EXISTS evalops;

CREATE TABLE IF NOT EXISTS evalops.trace_events_ch
(
  timestamp DateTime,
  trace_id String,
  span_id String,
  component String,
  prompt Nullable(String),
  completion Nullable(String),
  tokens_in UInt32,
  tokens_out UInt32,
  latency_ms UInt32,
  metadata String
)
ENGINE = MergeTree
ORDER BY (timestamp, trace_id, span_id);
