from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.orders import OrderStatus
from app.db.models.skus import Sku, SkuBom


@pytest.fixture()
def template_sku(db_session: Session) -> Sku:
    template = Sku(
        code="BQT",
        name="Bouquet",
        is_template=True,
        unit="bunch",
        track_stock=True,
        base_price=150000,
        options_json={},
        is_active=True,
    )
    component = Sku(
        code="STEM",
        name="Flower Stem",
        is_template=False,
        unit="stem",
        track_stock=True,
        base_price=10000,
        options_json={},
        is_active=True,
    )
    db_session.add_all([template, component])
    db_session.flush()
    db_session.add(
        SkuBom(
            parent_sku_id=template.id,
            component_sku_id=component.id,
            qty=Decimal("3"),
            uom="stem",
        )
    )
    db_session.flush()
    return template


def _order_payload(sku: Sku, receive_at: datetime, include_items: bool = True) -> dict:
    payload = {
        "source": "MANUAL",
        "customer": {"name": "Bob", "phone": "0987654321"},
        "receiver": {"name": "Receiver", "phone": "0977777777"},
        "delivery": {
            "method": "DELIVERY",
            "receive_at_iso": receive_at.isoformat(),
            "address": "123 Flower Street",
        },
        "card_message": "Happy Birthday!",
        "deposit_amount": 0,
    }
    if include_items:
        payload["items"] = [
            {
                "sku_id": sku.id,
                "qty": 2,
                "unit_price": 200000,
                "options": {"color": "red"},
            }
        ]
    return payload


def test_create_order_with_items(client: TestClient, template_sku: Sku) -> None:
    receive_at = datetime.now(timezone.utc) + timedelta(hours=2)
    response = client.post("/orders", json=_order_payload(template_sku, receive_at))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OrderStatus.NEW.value
    assert data["total_amount"] == 400000
    assert data["remaining_amount"] == 400000
    assert data["customer"]["phone"] == "0987654321"
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["sku_id"] == template_sku.id
    assert item["unit_price"] == 200000
    assert item["line_total"] == 400000
    assert item["bom_snapshot"]


def test_create_order_without_items(client: TestClient, template_sku: Sku) -> None:
    receive_at = datetime.now(timezone.utc) + timedelta(hours=3)
    payload = _order_payload(template_sku, receive_at, include_items=False)
    response = client.post("/orders", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OrderStatus.CONFIRMING.value
    assert data["total_amount"] == 0
    assert data["deposit_amount"] == 0
    assert data["remaining_amount"] == 0


def test_order_status_transitions(client: TestClient, template_sku: Sku) -> None:
    receive_at = datetime.now(timezone.utc) + timedelta(hours=1)
    response = client.post("/orders", json=_order_payload(template_sku, receive_at))
    order = response.json()
    order_id = order["id"]

    for target in [
        OrderStatus.ASSIGNED.value,
        OrderStatus.IN_PROGRESS.value,
        OrderStatus.READY.value,
        OrderStatus.COMPLETED.value,
    ]:
        transition = client.post(f"/orders/{order_id}/status", json={"status": target})
        assert transition.status_code == 200
        assert transition.json()["status"] == target

    invalid = client.post(f"/orders/{order_id}/status", json={"status": OrderStatus.CANCELLED.value})
    assert invalid.status_code == 400


def test_invalid_status_transition(client: TestClient, template_sku: Sku) -> None:
    receive_at = datetime.now(timezone.utc) + timedelta(hours=1)
    response = client.post("/orders", json=_order_payload(template_sku, receive_at))
    order_id = response.json()["id"]

    invalid = client.post(f"/orders/{order_id}/status", json={"status": OrderStatus.READY.value})
    assert invalid.status_code == 400

    cancel = client.post(f"/orders/{order_id}/status", json={"status": OrderStatus.CANCELLED.value})
    assert cancel.status_code == 200
    assert cancel.json()["status"] == OrderStatus.CANCELLED.value
