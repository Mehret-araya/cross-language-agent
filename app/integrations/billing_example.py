
from decimal import Decimal, InvalidOperation


def calculate_total(
    unit_price: str,
    quantity: int,
) -> dict:
    """Calculate a billing total using validated decimal arithmetic."""
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be a whole number.")

    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    try:
        price = Decimal(unit_price)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("Unit price must be a valid number.") from exc

    if not price.is_finite():
        raise ValueError("Unit price must be a finite number.")

    if price < 0:
        raise ValueError("Unit price cannot be negative.")

    total = price * quantity

    return {
        "unit_price": str(price),
        "quantity": quantity,
        "total": str(total),
    }
