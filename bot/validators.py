"""
Input validation for order parameters.
Raises ValueError with descriptive messages on invalid input.
"""

from decimal import Decimal, InvalidOperation

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET", "STOP"}


def validate_symbol(symbol: str) -> str:
    """Ensure symbol is non-empty uppercase string."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValueError(f"Symbol '{symbol}' contains invalid characters.")
    return symbol


def validate_side(side: str) -> str:
    """Ensure side is BUY or SELL."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Side must be one of {VALID_SIDES}, got '{side}'.")
    return side


def validate_order_type(order_type: str) -> str:
    """Ensure order type is supported."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be one of {VALID_ORDER_TYPES}, got '{order_type}'.")
    return order_type


def validate_quantity(quantity: str) -> Decimal:
    """Ensure quantity is a positive number."""
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0, got {qty}.")
    return qty


def validate_price(price: str | None, order_type: str) -> Decimal | None:
    """Ensure price is provided (and positive) for LIMIT/STOP orders."""
    if order_type in {"LIMIT", "STOP"}:
        if price is None:
            raise ValueError(f"Price is required for {order_type} orders.")
        try:
            p = Decimal(str(price))
        except InvalidOperation:
            raise ValueError(f"Price '{price}' is not a valid number.")
        if p <= 0:
            raise ValueError(f"Price must be greater than 0, got {p}.")
        return p
    return None  # not needed for MARKET / STOP_MARKET


def validate_stop_price(stop_price: str | None, order_type: str) -> Decimal | None:
    """Ensure stopPrice is provided for STOP orders."""
    if order_type in {"STOP", "STOP_MARKET"}:
        if stop_price is None:
            raise ValueError(f"stopPrice is required for {order_type} orders.")
        try:
            sp = Decimal(str(stop_price))
        except InvalidOperation:
            raise ValueError(f"stopPrice '{stop_price}' is not a valid number.")
        if sp <= 0:
            raise ValueError(f"stopPrice must be greater than 0, got {sp}.")
        return sp
    return None
