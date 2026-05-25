from typing import Dict, Any

from framework import app
from middleware import audit_log, login_required, role_required
from validators import (
    validate_customer_input,
    validate_product_input,
    validate_order_input,
)
from models import (
    get_all_customers, create_customer,
    get_all_products, create_product,
    get_all_orders, create_order,
)
from templates import render_json, render_error

JSON_HEADERS = {"Content-Type": "application/json"}


#GET /customers
@app.get("/customers")
@audit_log
@login_required
def list_customers(request: Dict[str, Any]) -> Dict[str, Any]:
    data = get_all_customers()
    return {"status_code": 200, "body": render_json(data), "headers": JSON_HEADERS}


#POST /customers
@app.post("/customers")
@audit_log
@role_required("admin")
def create_customer_view(request: Dict[str, Any]) -> Dict[str, Any]:
    body = request.get("body", {})
    valid, msg = validate_customer_input(body)
    if not valid:
        return {"status_code": 400, "body": render_error(msg), "headers": JSON_HEADERS}
    customer = create_customer(body["name"], body["email"])
    return {"status_code": 201, "body": render_json(customer), "headers": JSON_HEADERS}


#GET /products
@app.get("/products")
@audit_log
def list_products(request: Dict[str, Any]) -> Dict[str, Any]:
    data = get_all_products()
    return {"status_code": 200, "body": render_json(data), "headers": JSON_HEADERS}


#POST /products
@app.post("/products")
@audit_log
@role_required("admin")
def create_product_view(request: Dict[str, Any]) -> Dict[str, Any]:
    body = request.get("body", {})
    valid, msg = validate_product_input(body)
    if not valid:
        return {"status_code": 400, "body": render_error(msg), "headers": JSON_HEADERS}
    product = create_product(body["name"], body["price"])
    return {"status_code": 201, "body": render_json(product), "headers": JSON_HEADERS}


#POST /orders
@app.post("/orders")
@audit_log
@login_required
def create_order_view(request: Dict[str, Any]) -> Dict[str, Any]:
    body = request.get("body", {})
    valid, msg = validate_order_input(body)
    if not valid:
        return {"status_code": 400, "body": render_error(msg), "headers": JSON_HEADERS}
    order = create_order(body["customer_id"], body["product_id"], body["quantity"])
    if order is None:
        return {"status_code": 400, "body": render_error("Invalid customer_id or product_id"), "headers": JSON_HEADERS}
    return {"status_code": 201, "body": render_json(order), "headers": JSON_HEADERS}


#GET /orders
@app.get("/orders")
@audit_log
@role_required("admin")
def list_orders(request: Dict[str, Any]) -> Dict[str, Any]:
    data = get_all_orders()
    return {"status_code": 200, "body": render_json(data), "headers": JSON_HEADERS}
