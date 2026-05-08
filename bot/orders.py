"""
High-level order placement logic.
Sits between the CLI and the raw BinanceClient.
"""

from decimal import Decimal

from .client import BinanceClient
from .logging_config import get_logger
from .validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = get_logger(__name__)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> dict:
    """
    Validate inputs, build the order payload, and call the API.

    Returns the raw API response dict on success.
    Raises ValueError for bad inputs, httpx errors for API/network failures.
    """

    # --- Validate ---
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    qty: Decimal = validate_quantity(quantity)
    validated_price: Decimal | None = validate_price(price, order_type)
    validated_stop: Decimal | None = validate_stop_price(stop_price, order_type)

    # --- Build summary ---
    summary = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": str(qty),
    }
    if validated_price is not None:
        summary["price"] = str(validated_price)
    if validated_stop is not None:
        summary["stopPrice"] = str(validated_stop)

    logger.info("Order request summary: %s", summary)

    # --- Build API params ---
    params: dict = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": str(qty),
    }

    if order_type == "LIMIT":
        params["price"] = str(validated_price)
        params["timeInForce"] = "GTC"

    if order_type == "STOP":
        params["price"] = str(validated_price)       # limit price
        params["stopPrice"] = str(validated_stop)    # trigger price
        params["timeInForce"] = "GTC"

    if order_type == "STOP_MARKET":
        params["stopPrice"] = str(validated_stop)

    # --- Place order ---
    logger.info("Placing %s %s order for %s qty=%s", order_type, side, symbol, qty)

    if client is None:
        # Dry-run mode — simulate a realistic response
        import time, random
        fake_price = str(round(float(params.get("price", 62345.10)), 2))
        response = {
            "orderId": random.randint(1000000000, 9999999999),
            "symbol": symbol,
            "status": "FILLED" if order_type == "MARKET" else "NEW",
            "clientOrderId": f"dryrun_{int(time.time())}",
            "price": params.get("price", "0"),
            "avgPrice": fake_price if order_type == "MARKET" else "0",
            "origQty": str(qty),
            "executedQty": str(qty) if order_type == "MARKET" else "0",
            "timeInForce": params.get("timeInForce", "GTC"),
            "type": order_type,
            "side": side,
        }
        logger.info("[DRY-RUN] Simulated order response: %s", response)
        return response

    response = client.place_order(**params)
    logger.info("Order response: %s", response)
    return response


def format_response(response: dict) -> str:
    """Return a human-readable summary of an order response."""
    lines = [
        "─" * 50,
        "  ORDER RESPONSE",
        "─" * 50,
        f"  Order ID   : {response.get('orderId', 'N/A')}",
        f"  Symbol     : {response.get('symbol', 'N/A')}",
        f"  Side       : {response.get('side', 'N/A')}",
        f"  Type       : {response.get('type', 'N/A')}",
        f"  Status     : {response.get('status', 'N/A')}",
        f"  Qty Ordered: {response.get('origQty', 'N/A')}",
        f"  Qty Filled : {response.get('executedQty', 'N/A')}",
        f"  Avg Price  : {response.get('avgPrice', 'N/A')}",
        f"  Price      : {response.get('price', 'N/A')}",
        "─" * 50,
    ]
    return "\n".join(lines)
