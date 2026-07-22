import pytest


@pytest.mark.asyncio
async def test_admin_can_create_product_after_login(client):
    signup_payload = {
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@ecommerce.com",
        "password": "AdminPass123!",
    }
    await client.post("/api/auth/signup", json=signup_payload)

    login_payload = {
        "email": "admin@ecommerce.com",
        "password": "AdminPass123!",
    }
    response = await client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    token = response.json()["access_token"]

    product_payload = {
        "name": "Admin Test Monitor",
        "brand": "AdminBrand",
        "category": "Televisions",
        "price": 549.99,
        "discount": 12.0,
        "description": "A test monitor created by admin.",
        "specifications": {"Display": "27-inch QHD", "Refresh Rate": "144Hz"},
        "rating": 4.8,
        "stock": 15,
        "images": ["/products/tvs/admin-test-monitor-1.jpg"],
    }

    response = await client.post(
        "/api/products",
        json=product_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == product_payload["name"]

    product_id = response.json()["id"]
    response = await client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id
