from typing import Any, Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    if not isinstance(email, str):
        return False, "Email must be a string"
    if "@" not in email or "." not in email:
        return False, "Email must contain '@' and '.'"
    return True, ""


def validate_positive_number(value: Any) -> Tuple[bool, str]:
    if not isinstance(value, (int, float)):
        return False, "Value must be a number"
    if value <= 0:
        return False, "Value must be positive"
    return True, ""


def validate_customer_input(data: dict) -> Tuple[bool, str]:
    if not data.get("name"):
        return False, "Name is required"
    valid, msg = validate_email(data.get("email", ""))
    if not valid:
        return False, msg
    return True, ""


def validate_product_input(data: dict) -> Tuple[bool, str]:
    if not data.get("name"):
        return False, "Name is required"
    valid, msg = validate_positive_number(data.get("price"))
    if not valid:
        return False, f"Price error: {msg}"
    return True, ""


def validate_order_input(data: dict) -> Tuple[bool, str]:
    if not isinstance(data.get("customer_id"), int):
        return False, "customer_id must be an integer"
    if not isinstance(data.get("product_id"), int):
        return False, "product_id must be an integer"
    valid, msg = validate_positive_number(data.get("quantity"))
    if not valid:
        return False, f"Quantity error: {msg}"
    return True, ""
