# Risk Management Rules

## Capital Allocation

- **Max per trade:** 5% of total portfolio value
- **Max concurrent positions:** 5 open trades at any time
- **Max sector concentration:** No more than 15% of portfolio in a single sector
- **Cash buffer:** Always keep at least 20% in cash — never go fully invested

To calculate position size:
1. Get total portfolio value from Kite holdings + cash
2. Max risk per trade = 1% of portfolio (not 1% of position — 1% of total capital)
3. Position size = (Max risk in ₹) / (Entry price − Stop-loss price)

Example: ₹10L portfolio → max risk ₹10,000 per trade. Entry ₹500, stop-loss ₹490 → position size = 10,000 / 10 = 1,000 shares. Cap at 5% of portfolio (₹50,000 / ₹500 = 100 shares). Use the lower of the two.

---

## Stop-Loss Rules

- Every trade MUST have a stop-loss. No exceptions.
- Default stop-loss: 1.5% below entry for BUY trades
- Hard stop-loss: Never risk more than 2% below entry on any single trade
- If the nearest technical stop (below swing low) is more than 2% away, skip the trade
- Stop-losses should be set as GTT (Good Till Triggered) orders in Kite immediately after entry

---

## Risk/Reward Requirements

- Minimum R/R ratio: **1:2** (risk ₹1 to make ₹2)
- Preferred R/R ratio: 1:3 or better
- If R/R < 1:2 after calculating realistic target, do not recommend the trade

---

## Trade Filters (Auto-disqualify)

Skip any symbol that meets any of these conditions:
- Already has an open position logged in the decision log (avoid doubling up)
- Hit stop-loss within the last 5 trading days (let it settle)
- Earnings announcement within the next 3 trading days (too volatile)
- Daily volume < 500,000 shares (illiquid)
- No clear technical signal (score < 5.5)

---

## Exit Rules (for open positions — inform user)

If reviewing open positions from the decision log:
- **Take profit:** Alert user if price has reached or exceeded the original target
- **Stop-loss breach:** Alert user immediately if price is at or below stop-loss level
- **Trailing stop:** Once a trade is +3% in profit, suggest moving stop-loss to breakeven

---

## Global Risk-Off Warning

Flag all trade recommendations as HIGH RISK and reduce suggested position sizes by 50% if any of the following are true:
- VIX India (India VIX) > 20
- Major negative global macro news detected in the news search (rate hikes, war escalation, etc.)
- More than 3 of the last 5 Nifty 50 sessions were red (broad market downtrend)
