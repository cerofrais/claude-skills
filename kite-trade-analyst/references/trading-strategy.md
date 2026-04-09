# Trading Strategy Reference

## Indicator Parameters
- RSI: 14-period
- MACD: Fast 12 / Slow 26 / Signal 9
- EMAs: 20-period, 50-period, 200-period

---

## RSI Rules

| RSI Value     | Signal        | Notes                                        |
|---------------|---------------|----------------------------------------------|
| < 30          | Bullish setup | Oversold — watch for reversal confirmation   |
| 30–45         | Mild bullish  | Coming out of oversold territory             |
| 45–55         | Neutral       | No directional bias                          |
| 55–70         | Mild bearish  | Overbought territory approaching             |
| > 70          | Bearish setup | Overbought — watch for rejection candle      |

**RSI Divergence (stronger signal):**
- Bullish divergence: price makes a lower low, RSI makes a higher low → strong buy signal
- Bearish divergence: price makes a higher high, RSI makes a lower high → strong sell signal

---

## MACD Rules

**MACD Crossover (primary signal):**
- MACD line crosses ABOVE signal line → BUY signal
- MACD line crosses BELOW signal line → SELL signal

**Histogram momentum:**
- Histogram expanding positively → strengthening bullish momentum
- Histogram shrinking from positive → momentum fading, consider exit
- Histogram expanding negatively → strengthening bearish momentum

**Zero-line cross:**
- MACD crosses above zero → confirmed uptrend
- MACD crosses below zero → confirmed downtrend

---

## EMA Rules

**Trend identification:**
- Price above EMA-200 → long-term uptrend (only take BUY trades)
- Price below EMA-200 → long-term downtrend (only take SELL/short trades, or stay out)

**EMA crossovers:**
- EMA-20 crosses above EMA-50 → medium-term bullish signal (Golden cross on short timeframe)
- EMA-20 crosses below EMA-50 → medium-term bearish signal

**Price vs EMA-20:**
- Price pulling back to EMA-20 in an uptrend → good entry point for long
- Price bouncing off EMA-50 in an uptrend → stronger support, stronger entry

---

## Signal Scoring (0–10 per indicator)

### RSI Score
- RSI 25–35 (strong oversold): 9–10
- RSI 35–45 (mild oversold): 6–8
- RSI 45–55 (neutral): 5
- RSI 55–65 (mild overbought): 3–4
- RSI > 65 (overbought): 1–2

### MACD Score
- Fresh bullish crossover + expanding histogram: 9–10
- Bullish crossover (histogram flat): 6–8
- MACD above signal, positive histogram: 5–6
- MACD below signal: 2–4
- Fresh bearish crossover + expanding negative histogram: 1–2

### EMA Score
- Price above EMA-20 > EMA-50 > EMA-200 (all aligned bullish): 10
- Price above EMA-50 and EMA-200: 7–8
- Price above EMA-200 only: 5
- Price below EMA-200: 2–3
- Price below all EMAs: 1

### Combined Technical Score
Average the three scores → scale to 0–10 → round to 1 decimal place.
Score ≥ 7.0: STRONG_BUY
Score 5.5–6.9: BUY
Score 4.0–5.4: NEUTRAL
Score 2.5–3.9: SELL
Score < 2.5: STRONG_SELL

---

## Entry, Target, and Stop-Loss

**Entry:**
- BUY: Enter at current market price or limit slightly below the last close
- SELL (short): Enter at current market price or limit slightly above the last close

**Stop-Loss:**
- BUY trade: Place stop-loss 1.5% below entry, or just below the most recent swing low (whichever is tighter)
- SELL trade: Place stop-loss 1.5% above entry, or just above the most recent swing high

**Target:**
- Minimum target = entry ± (2 × stop-loss distance) to ensure 1:2 R/R
- Preferred target = next major resistance (BUY) or support (SELL) level based on the price history
- Maximum target = 8% above entry for short-term trades

---

## Trade Validity

A trade setup is valid only when:
1. Technical score ≥ 5.5 (BUY or better)
2. Risk/reward ≥ 1:2
3. Price is above EMA-200 (for BUY trades)
4. At least 2 of the 3 indicators agree on direction
