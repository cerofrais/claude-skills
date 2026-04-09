---
name: kite-trade-analyst
description: >
  Runs a full NSE equity trading analysis using technical indicators (RSI, MACD, Moving Averages), news sentiment, and a history of past trade decisions. Fetches live market data and holdings via Kite, scores each stock, and presents ranked trade recommendations with entry price, target, and stop-loss. Places orders via Kite upon user approval. Logs every decision for future reference. Trigger with: "run trade analysis", "what should I trade today", "analyze my stocks", "trading suggestions", "check my watchlist", "any good trades today", or "market analysis".
---

## Overview

This skill runs a structured trading analysis across your NSE watchlist and current Kite holdings each morning. It combines technical signals, news sentiment, and your own trading history to surface the best setups — then hands control back to you before placing anything.

---

## Workflow

### Step 1 — Load the universe of stocks
1. Run `scripts/manage_watchlist.py --action read` to get the fixed watchlist
2. Call `mcp__kite__get_holdings` to get current holdings
3. Merge both lists (deduplicate). This is your analysis universe for today.

### Step 2 — Fetch market data from Kite
For each symbol in the universe:
- Call `mcp__kite__get_historical_data` with:
  - `instrument_token`: look up via `mcp__kite__search_instruments` if needed
  - `from_date`: 200 trading days back (for EMA-200 accuracy)
  - `to_date`: today
  - `interval`: "day"
- Store the candles array (format: `[timestamp, open, high, low, close, volume]`) for each symbol

### Step 3 — Compute technical indicators
For each symbol, pass its candles to the script:
```
python3 scripts/compute_indicators.py --candles '<json_array>'
```
The script outputs a JSON object with:
- `rsi_14`: current RSI value
- `macd_line`, `signal_line`, `histogram`: current MACD values
- `ema_20`, `ema_50`, `ema_200`: current EMA values
- `close`: latest close price
- `signal_summary`: one of STRONG_BUY / BUY / NEUTRAL / SELL / STRONG_SELL

Refer to `references/trading-strategy.md` for how to interpret these values.

### Step 4 — Fetch news sentiment
For each symbol in the universe, use WebSearch to search:
> `"[SYMBOL] NSE stock news site:economictimes.com OR site:moneycontrol.com OR site:livemint.com"`

Summarize the top 3 results per symbol. Score sentiment per `references/sentiment-scoring.md`.

### Step 5 — Review past decisions
Run: `python3 scripts/log_decision.py --action read --symbol ALL --last 20`

Review recent decisions. Note:
- Symbols where a stop-loss was hit (avoid re-entering too soon)
- Positions already entered that are still open (don't double-enter)
- Patterns in what's been working vs not

Refer to `references/decision-log-format.md` for the log schema.

### Step 6 — Score and rank trade ideas
For each symbol, combine:
- Technical signal score (from Step 3, per trading-strategy.md)
- Sentiment score (from Step 4, per sentiment-scoring.md)
- Past decision context (from Step 5)

Apply risk filters from `references/risk-management.md`:
- Skip any symbol with risk/reward below 1:2
- Skip any symbol where you already hold an open position logged in the decision log
- Flag any symbol that hit a stop-loss in the last 5 trading days

Rank remaining symbols by combined score, highest first.

### Step 7 — Present recommendations
Show the top 3–5 trade ideas in a clean table:

```
SYMBOL | Direction | Entry | Target | Stop-Loss | R/R | Technical Signal | Sentiment | Reasoning
```

After the table, write 2–3 sentences per trade explaining the setup in plain English.

### Step 8 — Ask for approval
Ask the user: "Which trade(s) would you like to place? Type the symbol(s) or say 'none'."

For each approved trade:
- Confirm: symbol, direction (BUY/SELL), quantity (suggest based on risk-management.md), order type (MARKET or LIMIT)
- Ask: "Place this order: BUY [QTY] [SYMBOL] at [PRICE]? (yes / no)"

### Step 9 — Place approved orders
For each confirmed order, call:
- `mcp__kite__place_order` with the confirmed parameters
- Confirm success and show the order ID

### Step 10 — Log decisions
For each trade presented (whether placed or skipped), run:
```
python3 scripts/log_decision.py --action append \
  --symbol SYMBOL \
  --direction BUY/SELL/SKIP \
  --entry_price PRICE \
  --target TARGET \
  --stoploss STOPLOSS \
  --reasoning "brief reasoning" \
  --order_id ORDER_ID_OR_NA
```

---

## Hard Rules

- NEVER place an order without explicit user confirmation ("yes") on each trade
- NEVER recommend more than 5 trades in a single session
- NEVER skip the stop-loss calculation — every recommendation must have one
- If Kite returns an error at any step, report it clearly and continue with the remaining symbols
- If fewer than 3 stocks pass the risk filter, say so and explain which ones were filtered and why
- Always present the decision log review (Step 5) findings before showing recommendations
