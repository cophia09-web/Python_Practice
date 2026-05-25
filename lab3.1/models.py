from typing import Any, Dict, List, Optional

db: Dict[str, List[Dict[str, Any]]] = {
    "customers": [],
    "products": [],
    "orders": []
}


def _next_id(collection: str) -> int:
    items = db[collection]
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


# --- Customers ---

def get_all_customers() -> List[Dict[str, Any]]:
    return db["customers"]


def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    return next((c for c in db["customers"] if c["id"] == customer_id), None)


def create_customer(name: str, email: str) -> Dict[str, Any]:
    customer = {"id": _next_id("customers"), "name": name, "email": email}
    db["customers"].append(customer)
    return customer


# --- Products ---

def get_all_products() -> List[Dict[str, Any]]:
    return db["products"]


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    return next((p for p in db["products"] if p["id"] == product_id), None)


def create_product(name: str, price: float) -> Dict[str, Any]:
    product = {"id": _next_id("products"), "name": name, "price": price}
    db["products"].append(product)
    return product


# --- Orders ---

def get_all_orders() -> List[Dict[str, Any]]:
    return db["orders"]


def create_order(customer_id: int, product_id: int, quantity: int) -> Optional[Dict[str, Any]]:
    customer = get_customer_by_id(customer_id)
    product = get_product_by_id(product_id)
    if customer is None or product is None:
        return None
    total = product["price"] * quantity
    order = {
        "id": _next_id("orders"),
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "total": total
    }
    db["orders"].append(order)
    return order
