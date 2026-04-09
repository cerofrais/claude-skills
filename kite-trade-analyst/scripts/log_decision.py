#!/usr/bin/env python3
"""
log_decision.py
Read and write trade decisions to data/decision_log.json.

Usage:
  # Append a new decision
  python3 log_decision.py --action append --symbol RELIANCE --direction BUY \
    --entry_price 2850 --target 2995 --stoploss 2793 --risk_reward 2.54 \
    --technical_score 7.8 --sentiment BULLISH --global_macro GLOBAL_POSITIVE \
    --reasoning "RSI recovering from oversold, MACD bullish crossover." \
    --order_id 230410000012345

  # Read last N decisions (ALL or specific symbol)
  python3 log_decision.py --action read --symbol ALL --last 20
  python3 log_decision.py --action read --symbol RELIANCE --last 5

  # Update an existing record's status/outcome
  python3 log_decision.py --action update --id 20240410-RELIANCE-001 \
    --status TARGET_HIT --outcome WIN --exit_price 2995 --exit_date 2024-04-15 --pnl_pct 5.09
"""

import json
import sys
import argparse
import os
from datetime import datetime, date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "..", "data", "decision_log.json")


def load_log() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_log(log: list):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def generate_id(symbol: str, log: list) -> str:
    today = date.today().strftime("%Y%m%d")
    prefix = f"{today}-{symbol.upper()}"
    existing = [r["id"] for r in log if r["id"].startswith(prefix)]
    seq = len(existing) + 1
    return f"{prefix}-{seq:03d}"


def action_append(args, log: list):
    entry = {
        "id": generate_id(args.symbol, log),
        "date": date.today().isoformat(),
        "symbol": args.symbol.upper(),
        "direction": args.direction.upper(),
        "entry_price": float(args.entry_price) if args.entry_price else None,
        "target": float(args.target) if args.target else None,
        "stoploss": float(args.stoploss) if args.stoploss else None,
        "risk_reward": float(args.risk_reward) if args.risk_reward else None,
        "technical_score": float(args.technical_score) if args.technical_score else None,
        "sentiment": args.sentiment or "NEUTRAL",
        "global_macro": args.global_macro or "GLOBAL_NEUTRAL",
        "reasoning": args.reasoning or "",
        "status": "OPEN" if args.direction.upper() in ("BUY", "SELL") else "SKIPPED",
        "order_id": args.order_id or "NA",
        "outcome": None,
        "exit_price": None,
        "exit_date": None,
        "pnl_pct": None
    }
    log.append(entry)
    save_log(log)
    print(json.dumps({"success": True, "id": entry["id"]}))


def action_read(args, log: list):
    symbol = args.symbol.upper() if args.symbol else "ALL"
    last_n = int(args.last) if args.last else 20

    if symbol == "ALL":
        filtered = log
    else:
        filtered = [r for r in log if r["symbol"] == symbol]

    result = filtered[-last_n:]

    # Summary stats
    open_positions = [r for r in filtered if r["status"] == "OPEN"]
    recent_stop_hits = [
        r for r in filtered
        if r["status"] == "STOP_HIT" and r["date"] >= (
            datetime.today().date().__class__.fromordinal(
                date.today().toordinal() - 7
            ).isoformat()
        )
    ]

    print(json.dumps({
        "records": result,
        "total_records": len(filtered),
        "open_positions": [r["symbol"] for r in open_positions],
        "recent_stop_hits": [r["symbol"] for r in recent_stop_hits],
        "showing": len(result)
    }, indent=2))


def action_update(args, log: list):
    record = next((r for r in log if r["id"] == args.id), None)
    if not record:
        print(json.dumps({"error": f"Record {args.id} not found"}))
        sys.exit(1)

    if args.status:
        record["status"] = args.status
    if args.outcome:
        record["outcome"] = args.outcome
    if args.exit_price:
        record["exit_price"] = float(args.exit_price)
    if args.exit_date:
        record["exit_date"] = args.exit_date
    if args.pnl_pct:
        record["pnl_pct"] = float(args.pnl_pct)

    save_log(log)
    print(json.dumps({"success": True, "updated": record["id"]}))


def main():
    parser = argparse.ArgumentParser(description="Manage trade decision log")
    parser.add_argument("--action", required=True, choices=["append", "read", "update"])
    parser.add_argument("--symbol", help="Stock symbol (or ALL for read)")
    parser.add_argument("--direction", help="BUY / SELL / SKIP")
    parser.add_argument("--entry_price")
    parser.add_argument("--target")
    parser.add_argument("--stoploss")
    parser.add_argument("--risk_reward")
    parser.add_argument("--technical_score")
    parser.add_argument("--sentiment")
    parser.add_argument("--global_macro")
    parser.add_argument("--reasoning")
    parser.add_argument("--order_id")
    parser.add_argument("--last", default="20", help="Number of records to return")
    parser.add_argument("--id", help="Decision ID for update action")
    parser.add_argument("--status", help="New status for update")
    parser.add_argument("--outcome", help="WIN / LOSS / BREAKEVEN")
    parser.add_argument("--exit_price")
    parser.add_argument("--exit_date")
    parser.add_argument("--pnl_pct")
    args = parser.parse_args()

    log = load_log()

    if args.action == "append":
        action_append(args, log)
    elif args.action == "read":
        action_read(args, log)
    elif args.action == "update":
        action_update(args, log)


if __name__ == "__main__":
    main()
