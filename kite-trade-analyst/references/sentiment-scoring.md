# Sentiment Scoring Guide

## Overview

Sentiment analysis combines two layers:
1. **Stock-specific sentiment** — News about the individual company
2. **Global macro signals** — FII flows, US markets, DXY, commodities, and Asian market cues

Both layers contribute to the final sentiment score.

---

## Stock-Specific Sentiment

### Search Query
Use WebSearch with:
> `"[SYMBOL] NSE stock news site:economictimes.com OR site:moneycontrol.com OR site:livemint.com"`

Fetch top 3 results. Read headlines and summaries.

### Keyword Scoring

**Strong Bullish (+2 each):**
- Results beat estimates / earnings surprise / record revenue
- New contract won / partnership signed / major order received
- Buyback announced / special dividend / promoter buying
- Upgrade by analyst / price target raised significantly
- FDA approval / regulatory clearance / key license obtained

**Mild Bullish (+1 each):**
- In-line results / steady guidance
- Minor contract or order win
- Management positive commentary
- Sector tailwind mentioned

**Neutral (0):**
- Routine filings / AGM news
- No significant news found

**Mild Bearish (−1 each):**
- Results slightly missed estimates
- Management cautious on outlook
- Minor regulatory query / show cause notice
- Key executive departure

**Strong Bearish (−2 each):**
- Results badly missed / guidance cut
- Fraud allegation / SEBI investigation / ED raid
- Promoter selling stake significantly
- Downgrade by analyst / target cut
- Plant shutdown / product recall / major litigation

### Stock Sentiment Score
Sum the keyword scores, then clamp to the range −4 to +4.

| Score | Label           |
|-------|-----------------|
| +3 to +4 | STRONG_BULLISH |
| +1 to +2 | BULLISH         |
| 0        | NEUTRAL         |
| −1 to −2 | BEARISH         |
| −3 to −4 | STRONG_BEARISH  |

Sentiment score contribution to final trade score:
- STRONG_BULLISH: +2.0
- BULLISH: +1.0
- NEUTRAL: 0
- BEARISH: −1.0
- STRONG_BEARISH: −2.0 (also flag the trade with a ⚠️ warning)

---

## Global Macro / FII Flow Signals

These signals affect the entire market and must be checked once per session (not per stock).

### Sources to check (WebSearch each morning)
1. **US Markets close:** Search `"Dow Jones Nasdaq S&P 500 closing yesterday"` or fetch https://finance.yahoo.com/markets/
2. **SGX Nifty / Gift Nifty:** Search `"Gift Nifty today"` — pre-market India indicator. Also check: https://in.tradingview.com/symbols/NSE-NIFTY/
3. **FII/DII data:** Search `"FII DII buying selling today NSE"` — net flow data. NSE publishes daily at https://www.nseindia.com/market-data/fii-dii-data
4. **Dollar Index (DXY):** Check https://in.tradingview.com/symbols/TVC-DXY/ — rising DXY = capital outflows from India
5. **Crude Oil (Brent):** Check https://in.tradingview.com/symbols/TVC-UKOIL/ — India imports ~85% of its oil; rising crude = inflation + current account pressure
6. **Asian Markets:** Search `"Nikkei Hang Seng Shanghai today"` or check https://in.tradingview.com/markets/indices/ — Asian cues affect Nifty open
7. **US 10-Year Bond Yield:** Check https://in.tradingview.com/symbols/TVC-US10Y/ — rising yields = FII outflows from India as US becomes more attractive
8. **India VIX:** Check https://in.tradingview.com/symbols/NSE-INDIAVIX/ — VIX > 20 = market fear, apply risk-off rules

**TradingView Heatmap (optional but useful):**
Use https://in.tradingview.com/heatmap/stock/?color=change&dataset=NSEBSE&group=sector&size=market_cap_basic to quickly see which NSE sectors are green/red today before diving into individual stocks.

### Global Macro Score

Rate each signal as +1 (positive), 0 (neutral), or −1 (negative):

| Signal              | Positive (+1)                        | Negative (−1)                       |
|---------------------|--------------------------------------|--------------------------------------|
| US Markets          | S&P 500 up > 0.5%                    | S&P 500 down > 0.5%                  |
| Gift Nifty          | Trading above prev. Nifty close      | Trading below prev. Nifty close      |
| FII Flow            | Net buying > ₹500 Cr                 | Net selling > ₹500 Cr                |
| DXY                 | DXY falling / below 104              | DXY rising / above 106               |
| Crude Oil (Brent)   | Brent below $80/barrel               | Brent above $88/barrel               |
| Asian Markets       | Majority of Asian indices green      | Majority of Asian indices red        |
| US 10Y Bond Yield   | Yield falling or below 4.2%          | Yield rising above 4.6%              |
| India VIX           | VIX below 14 (complacency / calm)    | VIX above 18 (fear / volatility)     |

Sum all 8 signals:
- Score ≥ +4: **GLOBAL_POSITIVE** — increase all trade scores by 0.5, reduce risk buffer requirement
- Score −3 to +3: **GLOBAL_NEUTRAL** — no adjustment
- Score ≤ −4: **GLOBAL_NEGATIVE** — decrease all trade scores by 1.0, apply risk-off rules from risk-management.md

### Reporting
Always show the global macro scorecard at the top of the analysis output, before individual stock recommendations.

---

## Final Sentiment Score (per stock)

Final sentiment score = Stock sentiment score contribution + Global macro adjustment

This is added to the technical score when ranking trades:
- **Final trade score = Technical score (0–10) + Final sentiment score (−3 to +3)**
- Cap final trade score at 10.
