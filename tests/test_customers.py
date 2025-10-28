from __future__ import annotations

from fastapi.testclient import TestClient


def test_customer_upsert_by_phone(client: TestClient) -> None:
    payload = {"name": "Alice", "phone": "0123456789", "social_link": "https://zalo.me/alice"}
    response = client.post("/customers/upsert_by_phone", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["phone"] == "0123456789"
    customer_id = data["id"]

    update_payload = {"name": "Alice Updated", "phone": "0123456789", "social_link": "https://zalo.me/alice2"}
    response = client.post("/customers/upsert_by_phone", json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == customer_id
    assert updated["name"] == "Alice Updated"
    assert updated["social_link"] == "https://zalo.me/alice2"
