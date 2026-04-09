#!/usr/bin/env python3
"""
compute_indicators.py
Computes RSI(14), MACD(12,26,9), and EMA(20,50,200) from Kite OHLC candle data.

Usage:
  python3 compute_indicators.py --candles '<json_array>'

Input format (Kite historical data candles):
  [[timestamp, open, high, low, close, volume], ...]

Output: JSON with indicator values and a signal summary.
"""

import json
import sys
import argparse


def compute_ema(prices: list, period: int) -> list:
    """Compute Exponential Moving Average."""
    k = 2.0 / (period + 1)
    ema = [None] * len(prices)
    # Seed with SMA for the first period
    if len(prices) < period:
        return ema
    sma = sum(prices[:period]) / period
    ema[period - 1] = sma
    for i in range(period, len(prices)):
        ema[i] = prices[i] * k + ema[i - 1] * (1 - k)
    return ema


def compute_rsi(prices: list, period: int = 14) -> list:
    """Compute RSI using Wilder's smoothing method."""
    rsi = [None] * len(prices)
    if len(prices) < period + 1:
        return rsi

    gains = []
    losses = []
    for i in range(1, period + 1):
        delta = prices[i] - prices[i - 1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    for i in range(period, len(prices)):
        if i > period:
            delta = prices[i] - prices[i - 1]
            gain = max(delta, 0)
            loss = max(-delta, 0)
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            rsi[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i] = round(100.0 - (100.0 / (1.0 + rs)), 2)

    return rsi


def compute_macd(prices: list, fast: int = 12, slow: int = 26, signal: int = 9):
    """Compute MACD line, signal line, and histogram."""
    ema_fast = compute_ema(prices, fast)
    ema_slow = compute_ema(prices, slow)

    macd_line = [None] * len(prices)
    for i in range(len(prices)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line[i] = round(ema_fast[i] - ema_slow[i], 4)

    # Signal line = EMA(9) of MACD line
    macd_values = [v if v is not None else 0 for v in macd_line]
    # Find first non-None index
    first_valid = next((i for i, v in enumerate(macd_line) if v is not None), None)
    if first_valid is None:
        return macd_line, [None] * len(prices), [None] * len(prices)

    signal_line = [None] * len(prices)
    # EMA of macd_line starting from first_valid
    valid_macd = [(i, macd_line[i]) for i in range(len(macd_line)) if macd_line[i] is not None]
    if len(valid_macd) < signal:
        return macd_line, signal_line, [None] * len(prices)

    k = 2.0 / (signal + 1)
    seed_idx = valid_macd[signal - 1][0]
    seed_val = sum(v for _, v in valid_macd[:signal]) / signal
    signal_line[seed_idx] = round(seed_val, 4)

    for i in range(seed_idx + 1, len(prices)):
        if macd_line[i] is not None and signal_line[i - 1] is not None:
            signal_line[i] = round(macd_line[i] * k + signal_line[i - 1] * (1 - k), 4)

    histogram = [None] * len(prices)
    for i in range(len(prices)):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram[i] = round(macd_line[i] - signal_line[i], 4)

    return macd_line, signal_line, histogram


def score_rsi(rsi: float) -> float:
    if rsi is None:
        return 5.0
    if rsi < 25:
        return 10.0
    elif rsi < 30:
        return 9.0
    elif rsi < 35:
        return 8.0
    elif rsi < 45:
        return 7.0
    elif rsi < 55:
        return 5.0
    elif rsi < 65:
        return 3.5
    elif rsi < 70:
        return 2.5
    else:
        return 1.5


def score_macd(macd_val: float, signal_val: float, hist: float, prev_hist: float) -> float:
    if macd_val is None or signal_val is None:
        return 5.0
    above = macd_val > signal_val
    fresh_cross = (hist is not None and prev_hist is not None and
                   ((hist > 0 and prev_hist <= 0) or (hist < 0 and prev_hist >= 0)))
    expanding = hist is not None and prev_hist is not None and abs(hist) > abs(prev_hist)

    if above and fresh_cross and expanding:
        return 9.5
    elif above and expanding:
        return 8.0
    elif above:
        return 6.5
    elif not above and fresh_cross and expanding:
        return 1.5
    elif not above and expanding:
        return 2.5
    else:
        return 3.5


def score_ema(close: float, ema20, ema50, ema200) -> float:
    if close is None:
        return 5.0
    above_200 = ema200 is not None and close > ema200
    above_50 = ema50 is not None and close > ema50
    above_20 = ema20 is not None and close > ema20
    ema_aligned = (ema20 is not None and ema50 is not None and ema200 is not None and
                   ema20 > ema50 > ema200)

    if above_20 and above_50 and above_200 and ema_aligned:
        return 10.0
    elif above_50 and above_200:
        return 7.5
    elif above_200:
        return 5.5
    elif above_50:
        return 4.0
    else:
        return 2.0


def signal_label(score: float) -> str:
    if score >= 7.0:
        return "STRONG_BUY"
    elif score >= 5.5:
        return "BUY"
    elif score >= 4.0:
        return "NEUTRAL"
    elif score >= 2.5:
        return "SELL"
    else:
        return "STRONG_SELL"


def main():
    parser = argparse.ArgumentParser(description="Compute trading indicators from Kite OHLC candles")
    parser.add_argument("--candles", required=True, help="JSON array of candles [[ts,o,h,l,c,v],...]")
    args = parser.parse_args()

    try:
        candles = json.loads(args.candles)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    if not candles or len(candles) < 30:
        print(json.dumps({"error": f"Need at least 30 candles, got {len(candles)}"}))
        sys.exit(1)

    closes = [float(c[4]) for c in candles]

    rsi_series = compute_rsi(closes, 14)
    macd_line, signal_line, histogram = compute_macd(closes, 12, 26, 9)
    ema20_series = compute_ema(closes, 20)
    ema50_series = compute_ema(closes, 50)
    ema200_series = compute_ema(closes, 200)

    # Get most recent valid values
    n = len(closes)
    rsi_val = next((rsi_series[i] for i in range(n - 1, -1, -1) if rsi_series[i] is not None), None)
    macd_val = macd_line[n - 1]
    sig_val = signal_line[n - 1]
    hist_val = histogram[n - 1]
    prev_hist = histogram[n - 2] if n >= 2 else None
    ema20_val = ema20_series[n - 1]
    ema50_val = ema50_series[n - 1]
    ema200_val = ema200_series[n - 1]
    close_val = closes[n - 1]

    rsi_score = score_rsi(rsi_val)
    macd_score = score_macd(macd_val, sig_val, hist_val, prev_hist)
    ema_score = score_ema(close_val, ema20_val, ema50_val, ema200_val)

    combined_score = round((rsi_score + macd_score + ema_score) / 3, 1)

    result = {
        "close": round(close_val, 2),
        "rsi_14": rsi_val,
        "macd_line": macd_val,
        "signal_line": sig_val,
        "histogram": hist_val,
        "ema_20": round(ema20_val, 2) if ema20_val else None,
        "ema_50": round(ema50_val, 2) if ema50_val else None,
        "ema_200": round(ema200_val, 2) if ema200_val else None,
        "rsi_score": rsi_score,
        "macd_score": macd_score,
        "ema_score": ema_score,
        "technical_score": combined_score,
        "signal_summary": signal_label(combined_score)
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
