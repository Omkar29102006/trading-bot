#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
    # Market BUY
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

    # Limit SELL
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 100000

    # Stop-Market BUY (bonus order type)
    python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 95000

Environment variables required:
    BINANCE_API_KEY     – your Binance Futures Testnet API key
    BINANCE_API_SECRET  – your Binance Futures Testnet API secret
"""

import argparse
import os
import sys

from bot.client import BinanceClient
from bot.logging_config import get_logger, setup_logging
from bot.orders import format_response, place_order

setup_logging()
logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       required=True, choices=["BUY", "SELL"], help="Order side")
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET", "STOP"],
        help="Order type",
    )
    parser.add_argument("--quantity",   required=True, help="Order quantity")
    parser.add_argument("--price",      default=None,  help="Limit price (required for LIMIT/STOP)")
    parser.add_argument("--stop-price", default=None,  dest="stop_price",
                        help="Trigger price (required for STOP / STOP_MARKET)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate order without hitting the API (no keys needed)")
    return parser


def get_credentials() -> tuple[str, str]:
    api_key    = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        print(
            "\n[ERROR] Missing API credentials.\n"
            "Set the following environment variables before running:\n"
            "  export BINANCE_API_KEY=<your_key>\n"
            "  export BINANCE_API_SECRET=<your_secret>\n"
        )
        sys.exit(1)
    return api_key, api_secret


def print_request_summary(args: argparse.Namespace) -> None:
    print("\n" + "─" * 50)
    print("  ORDER REQUEST SUMMARY")
    print("─" * 50)
    print(f"  Symbol     : {args.symbol.upper()}")
    print(f"  Side       : {args.side.upper()}")
    print(f"  Type       : {args.order_type.upper()}")
    print(f"  Quantity   : {args.quantity}")
    if args.price:
        print(f"  Price      : {args.price}")
    if args.stop_price:
        print(f"  Stop Price : {args.stop_price}")
    print("─" * 50 + "\n")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print_request_summary(args)

    if args.dry_run:
        print("⚠️  DRY-RUN mode — no real API call will be made.\n")
        logger.info("Running in DRY-RUN mode")
        client = None
    else:
        api_key, api_secret = get_credentials()
        client = BinanceClient(api_key=api_key, api_secret=api_secret)

    try:
        response = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
        print(format_response(response))
        print("\n✅  Order placed successfully!\n")
        logger.info("Order placed successfully. orderId=%s", response.get("orderId"))

    except ValueError as exc:
        print(f"\n❌  Validation error: {exc}\n")
        logger.error("Validation error: %s", exc)
        sys.exit(2)

    except Exception as exc:
        # httpx errors, JSON parse errors, unexpected issues
        print(f"\n❌  Failed to place order: {exc}\n")
        logger.exception("Unexpected error while placing order")
        sys.exit(3)


if __name__ == "__main__":
    main()
