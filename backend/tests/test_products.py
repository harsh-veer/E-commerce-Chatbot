import pytest


@pytest.mark.asyncio
async def test_create_list_get_product(client):
    product_payload = {
        "name": "Test Laptop 101",
        "brand": "TestBrand",
        "category": "Laptops",
        "price": 1299.99,
        "discount": 10.0,
        "description": "A test laptop for validation.",
        "specifications": {"Processor": "Intel Core i7", "RAM": "16GB", "Storage": "512GB SSD"},
        "rating": 4.5,
        "stock": 50,
        "images": ["/products/test-laptop-101-1.jpg"],
    }

    response = await client.post("/api/products", json=product_payload)
    assert response.status_code == 401

    response = await client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == []
