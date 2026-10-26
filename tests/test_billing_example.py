import pytest

from app.integrations.billing_example import calculate_total


def test_calculate_total_with_valid_inputs():
    result = calculate_total("12.50", 4)

    assert result == {
        "unit_price": "12.50",
        "quantity": 4,
        "total": "50.00",
    }


def test_rejects_negative_quantity():
    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        calculate_total("12.50", -1)


def test_rejects_negative_unit_price():
    with pytest.raises(ValueError, match="Unit price cannot be negative"):
        calculate_total("-2.50", 3)


def test_rejects_invalid_unit_price():
    with pytest.raises(ValueError, match="Unit price must be a valid number"):
        calculate_total("abc", 2)


@pytest.mark.parametrize("price", ["NaN", "Infinity", "-Infinity"])
def test_rejects_non_finite_unit_price(price):
    with pytest.raises(ValueError, match="finite number"):
        calculate_total(price, 2)


@pytest.mark.parametrize("quantity", [True, 2.5, "3"])
def test_rejects_non_integer_quantity(quantity):
    with pytest.raises(ValueError, match="Quantity must be a whole number"):
        calculate_total("12.50", quantity)
