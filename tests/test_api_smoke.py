from io import BytesIO

from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image

import backend.main as main


client = TestClient(main.app)


def make_test_image_bytes() -> bytes:
    image = BytesIO()
    Image.new("RGB", (10, 20), "white").save(image, format="PNG")
    return image.getvalue()


def test_root_endpoint_returns_health_message():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "AI Virtual Try-On API (Async) is running"}


def test_catalog_returns_paginated_results():
    response = client.get("/api/v1/catalog")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 6
    assert data["total_count"] >= len(data["garments"]) > 0


def test_recommendations_returns_styling_tip_for_catalog_item():
    catalog_response = client.get("/api/v1/catalog")
    garment_id = catalog_response.json()["garments"][0]["id"]

    response = client.get(f"/api/v1/recommendations/{garment_id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["recommendations"], list)
    assert data["styling_tip"]


def test_try_on_returns_service_unavailable_when_queue_is_down(monkeypatch):
    def raise_queue_unavailable():
        raise HTTPException(status_code=503, detail=main.QUEUE_UNAVAILABLE_ERROR)

    monkeypatch.setattr(main, "ensure_queue_available", raise_queue_unavailable)

    response = client.post(
        "/api/v1/try-on",
        files={"user_image": ("user.png", make_test_image_bytes(), "image/png")},
        data={"garment_id": "shirt-1"},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": main.QUEUE_UNAVAILABLE_ERROR}


def test_task_status_returns_service_unavailable_when_queue_is_down(monkeypatch):
    def raise_queue_unavailable():
        raise HTTPException(status_code=503, detail=main.QUEUE_UNAVAILABLE_ERROR)

    monkeypatch.setattr(main, "ensure_queue_available", raise_queue_unavailable)

    response = client.get("/api/v1/tasks/test-task-id")

    assert response.status_code == 503
    assert response.json() == {"detail": main.QUEUE_UNAVAILABLE_ERROR}
