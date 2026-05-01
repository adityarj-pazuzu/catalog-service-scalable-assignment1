import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import main


@pytest.fixture
def client():
    """Create a test client with a temporary catalog database."""
    with TemporaryDirectory() as directory:
        main.DATABASE_PATH = str(Path(directory) / "catalog.db")
        main.initialize_database()
        yield TestClient(main.app)


def create_product(client, stock=5):
    """Create a sample product for catalog tests."""
    return client.post(
        "/products",
        json={
            "name": "Laptop",
            "description": "Student laptop",
            "price": 55000,
            "stock": stock,
        },
    )


def test_health_check(client):
    """Verify that the health endpoint returns service status."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "catalog-service"}


def test_create_and_list_products(client):
    """Verify that a created product appears in the product list."""
    created = create_product(client)

    assert created.status_code == 201
    assert created.json()["name"] == "Laptop"

    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["stock"] == 5


def test_get_product_by_id(client):
    """Verify that an existing product can be fetched by ID."""
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_update_stock(client):
    """Verify that product stock can be updated."""
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.patch(f"/products/{product_id}/stock", json={"stock": 12})

    assert response.status_code == 200
    assert response.json()["stock"] == 12


def test_reserve_product_stock(client):
    """Verify that reserving stock reduces the available quantity."""
    created = create_product(client)
    product_id = created.json()["id"]

    reserved = client.post(f"/products/{product_id}/reserve", json={"quantity": 2})

    assert reserved.status_code == 200
    assert reserved.json()["stock"] == 3


def test_get_missing_product_returns_404(client):
    """Verify that requesting a missing product returns 404."""
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_reserve_more_than_available_returns_409(client):
    """Verify that over-reserving stock returns a conflict."""
    created = create_product(client, stock=1)
    product_id = created.json()["id"]

    response = client.post(f"/products/{product_id}/reserve", json={"quantity": 2})

    assert response.status_code == 409
    assert response.json()["detail"] == "Not enough stock available"


def test_create_product_validation_error(client):
    """Verify that invalid product data returns a validation error."""
    response = client.post(
        "/products",
        json={"name": "A", "description": "", "price": -1, "stock": -1},
    )

    assert response.status_code == 422
