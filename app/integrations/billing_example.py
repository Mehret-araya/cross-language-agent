
from decimal import Decimal


def calculate_total(
    unit_price: str,
    quantity: int,
) -> dict:
    """Calculate a billing total using decimal arithmetic."""
    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    price = Decimal(unit_price)

    if price < 0:
        raise ValueError("Unit price cannot be negative.")

    total = price * quantity

    return {
        "unit_price": str(price),
        "quantity": quantity,
        "total": str(total),
    }
