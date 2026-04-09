# Decision Log Format

## Purpose

The decision log is a running record of every trade recommendation made — whether placed, skipped, or still open. It serves three functions:
1. Prevent double-entering a position
2. Track which setups worked and which didn't (improve the strategy over time)
3. Review recent stop-loss hits before re-entering a symbol

## Log File Location

`data/decision_log.json`

This file lives inside the skill folder and persists across sessions.

---

## JSON Schema

The file is a JSON array of decision objects:

```json
[
  {
    "id": "20240410-RELIANCE-001",
    "date": "2024-04-10",
    "symbol": "RELIANCE",
    "direction": "BUY",
    "entry_price": 2850.00,
    "target": 2995.00,
    "stoploss": 2793.00,
    "risk_reward": 2.54,
    "technical_score": 7.8,
    "sentiment": "BULLISH",
    "global_macro": "GLOBAL_POSITIVE",
    "reasoning": "RSI at 38 recovering from oversold, MACD bullish crossover, price bounced off EMA-50. FII net buying ₹1200 Cr. Strong crude fall positive for refining margins.",
    "status": "OPEN",
    "order_id": "230410000012345",
    "outcome": null,
    "exit_price": null,
    "exit_date": null,
    "pnl_pct": null
  }
]
```

---

## Field Definitions

| Field            | Type    | Values / Notes                                                  |
|------------------|---------|------------------------------------------------------------------|
| id               | string  | Format: `YYYYMMDD-SYMBOL-NNN`                                   |
| date             | string  | ISO date of when the recommendation was made                    |
| symbol           | string  | NSE ticker (e.g., RELIANCE, TCS, INFY)                          |
| direction        | string  | BUY / SELL / SKIP                                               |
| entry_price      | float   | Recommended entry price (null if SKIP)                          |
| target           | float   | Price target (null if SKIP)                                     |
| stoploss         | float   | Stop-loss level (null if SKIP)                                  |
| risk_reward      | float   | R/R ratio, e.g., 2.5 means 1:2.5                               |
| technical_score  | float   | Score from 0–10                                                 |
| sentiment        | string  | STRONG_BULLISH / BULLISH / NEUTRAL / BEARISH / STRONG_BEARISH  |
| global_macro     | string  | GLOBAL_POSITIVE / GLOBAL_NEUTRAL / GLOBAL_NEGATIVE             |
| reasoning        | string  | 2–3 sentence plain-English explanation of the setup             |
| status           | string  | OPEN / CLOSED / SKIPPED / STOP_HIT / TARGET_HIT                |
| order_id         | string  | Kite order ID if placed, "NA" if skipped                        |
| outcome          | string  | WIN / LOSS / BREAKEVEN / null (if still open)                  |
| exit_price       | float   | Price at which trade was closed (null if open)                  |
| exit_date        | string  | ISO date of exit (null if open)                                 |
| pnl_pct          | float   | % P&L on the trade, e.g., 3.2 means +3.2% (null if open)       |

---

## How Claude Uses the Log

**Before recommending a trade:**
- Check if `status == "OPEN"` for this symbol → skip (already in a position)
- Check if `status == "STOP_HIT"` in the last 5 days → flag and skip (too soon to re-enter)
- Check past `outcome` for this symbol → note win rate and average return in the recommendation

**After a session:**
- Append a new record for every stock analyzed (even SKIPs) so the history is complete

**Updating outcomes:**
- When a user reports that a trade hit its target or stop-loss, update the relevant record's `status`, `outcome`, `exit_price`, `exit_date`, and `pnl_pct`
