from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_clients():
    response = client.get("/clients/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_services():
    response = client.get("/services/")
    assert response.status_code == 200
    # Проверяем, что в ответе есть расчет НДС
    if len(response.json()) > 0:
        assert "vat_20" in response.json()[0]


def test_get_mechanics_rates():
    response = client.get("/mechanics/")
    assert response.status_code == 200
    if len(response.json()) > 0:
        assert "hourly_rate" in response.json()[0]


def test_get_all_orders():
    response = client.get("/orders/")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "average_check" in data