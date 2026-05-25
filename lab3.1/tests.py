import pytest
from framework import app, _routes
from main import dispatch
from middleware import transaction_log
from models import db


def reset_state():
    transaction_log.clear()
    _routes.clear()
    db["customers"] = []
    db["products"] = []
    db["orders"] = []
    import importlib
    import views
    importlib.reload(views)


def test_route_registration_integrity():
    reset_state()
    assert ('GET', '/customers') in _routes
    assert ('POST', '/orders') in _routes


def test_validation_email_format():
    reset_state()
    request = {
        "method": "POST",
        "path": "/customers",
        "session": {"user_id": 1, "role": "admin"},
        "body": {"name": "test_name", "email": "invalid-email"},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 400
    assert len(db["customers"]) == 0


def test_validation_positive_price():
    reset_state()
    request = {
        "method": "POST",
        "path": "/products",
        "session": {"user_id": 1, "role": "admin"},
        "body": {"name": "Laptop", "price": -100},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 400
    assert len(db["products"]) == 0


def test_relational_integrity_valid_order():
    reset_state()
    db["customers"].append({"id": 1, "name": "test_name", "email": "a@test.com"})
    db["products"].append({"id": 1, "name": "Laptop", "price": 1000})
    request = {
        "method": "POST",
        "path": "/orders",
        "session": {"user_id": 1, "role": "user"},
        "body": {"customer_id": 1, "product_id": 1, "quantity": 2},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 201
    assert len(db["orders"]) == 1
    assert db["orders"][0]["total"] == 2000


def test_relational_integrity_invalid_order():
    reset_state()
    request = {
        "method": "POST",
        "path": "/orders",
        "session": {"user_id": 1, "role": "user"},
        "body": {"customer_id": 999, "product_id": 999, "quantity": 1},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 400
    assert len(db["orders"]) == 0


def test_audit_log_capture_relational():
    reset_state()
    db["customers"].append({"id": 1, "name": "test_name", "email": "a@test.com"})
    db["products"].append({"id": 1, "name": "Laptop", "price": 1000})
    request = {
        "method": "POST",
        "path": "/orders",
        "session": {"user_id": 1, "role": "user"},
        "body": {"customer_id": 1, "product_id": 1, "quantity": 1},
        "query": {}
    }
    dispatch(request)
    assert len(transaction_log) == 1
    entry = transaction_log[0]
    assert entry['path'] == '/orders'
    assert entry['status_code'] == 201


# --- Additional tests ---

def test_unauthorized_without_session():
    reset_state()
    request = {
        "method": "GET",
        "path": "/customers",
        "session": {},
        "body": {},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 401


def test_forbidden_wrong_role():
    reset_state()
    request = {
        "method": "POST",
        "path": "/customers",
        "session": {"user_id": 1, "role": "user"},
        "body": {"name": "Alice", "email": "alice@example.com"},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 403


def test_404_unknown_route():
    reset_state()
    request = {
        "method": "GET",
        "path": "/unknown",
        "session": {"user_id": 1, "role": "admin"},
        "body": {},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 404


def test_create_customer_success():
    reset_state()
    request = {
        "method": "POST",
        "path": "/customers",
        "session": {"user_id": 1, "role": "admin"},
        "body": {"name": "Alice", "email": "alice@example.com"},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 201
    assert len(db["customers"]) == 1


def test_list_products_public():
    reset_state()
    db["products"].append({"id": 1, "name": "Laptop", "price": 1000})
    request = {
        "method": "GET",
        "path": "/products",
        "session": {},
        "body": {},
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 200
