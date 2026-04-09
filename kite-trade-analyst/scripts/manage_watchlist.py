#!/usr/bin/env python3
"""
manage_watchlist.py
Read and manage the NSE stock watchlist stored in data/watchlist.json.

Usage:
  python3 manage_watchlist.py --action read
  python3 manage_watchlist.py --action add --symbol TATAMOTORS
  python3 manage_watchlist.py --action remove --symbol TATAMOTORS
  python3 manage_watchlist.py --action list
"""

import json
import sys
import argparse
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WATCHLIST_FILE = os.path.join(SCRIPT_DIR, "..", "data", "watchlist.json")

DEFAULT_WATCHLIST = {
    "symbols": [
        "RELIANCE",
        "TCS",
        "HDFCBANK",
        "INFY",
        "ICICIBANK",
        "SBIN",
        "HINDUNILVR",
        "AXISBANK",
        "BAJFINANCE",
        "TATASTEEL",
        "WIPRO",
        "MARUTI",
        "SUNPHARMA",
        "TITAN",
        "ADANIENT"
    ],
    "notes": "Edit this file to customise your watchlist. Add/remove symbols as needed."
}


def load_watchlist() -> dict:
    if not os.path.exists(WATCHLIST_FILE):
        os.makedirs(os.path.dirname(WATCHLIST_FILE), exist_ok=True)
        save_watchlist(DEFAULT_WATCHLIST)
        return DEFAULT_WATCHLIST
    with open(WATCHLIST_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return DEFAULT_WATCHLIST


def save_watchlist(data: dict):
    os.makedirs(os.path.dirname(WATCHLIST_FILE), exist_ok=True)
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Manage NSE watchlist")
    parser.add_argument("--action", required=True, choices=["read", "add", "remove", "list"])
    parser.add_argument("--symbol", help="NSE ticker symbol")
    args = parser.parse_args()

    wl = load_watchlist()

    if args.action in ("read", "list"):
        print(json.dumps({"symbols": wl["symbols"], "count": len(wl["symbols"])}))

    elif args.action == "add":
        if not args.symbol:
            print(json.dumps({"error": "Symbol required for add action"}))
            sys.exit(1)
        sym = args.symbol.upper().strip()
        if sym in wl["symbols"]:
            print(json.dumps({"success": True, "message": f"{sym} already in watchlist"}))
        else:
            wl["symbols"].append(sym)
            save_watchlist(wl)
            print(json.dumps({"success": True, "added": sym, "total": len(wl["symbols"])}))

    elif args.action == "remove":
        if not args.symbol:
            print(json.dumps({"error": "Symbol required for remove action"}))
            sys.exit(1)
        sym = args.symbol.upper().strip()
        if sym not in wl["symbols"]:
            print(json.dumps({"error": f"{sym} not found in watchlist"}))
            sys.exit(1)
        wl["symbols"].remove(sym)
        save_watchlist(wl)
        print(json.dumps({"success": True, "removed": sym, "total": len(wl["symbols"])}))


if __name__ == "__main__":
    main()
