from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# 1. Тест: Клиенты
def test_clients_flow():
    # Создание клиента
    res_create = client.post(
        "/clients/",
        json={"name": "Тестовый Клиент", "phone": "+70001112233"},
    )
    assert res_create.status_code == 200
    data = res_create.json()
    assert "client" in data
    assert data["welcome_bonus_points"] == 150  # 5000 * 0.03 = 150

    # Получение списка клиентов
    res_get = client.get("/clients/")
    assert res_get.status_code == 200
    assert any(c["name"] == "Тестовый Клиент" for c in res_get.json())


# 2. Тест: Машины
def test_cars_flow():
    # Создаем машину
    res_create = client.post(
        "/cars/",
        json={
            "brand": "Audi",
            "model": "A6",
            "vin": "WAUZZZ12345TEST",
            "client_id": 1,
        },
    )
    assert res_create.status_code == 200
    assert res_create.json()["brand"] == "Audi"

    # Получаем все машины
    res_get = client.get("/cars/")
    assert res_get.status_code == 200
    assert isinstance(res_get.json(), list)


# 3. Тест: Механики
def test_mechanics_flow():
    # Нанимаем механика
    res_create = client.post(
        "/mechanics/",
        json={"name": "Игорь Электрик", "specialty": "Автоэлектрик диагност"},
    )
    assert res_create.status_code == 200

    # Получаем механиков и проверяем расчет часовой ставки
    res_get = client.get("/mechanics/")
    assert res_get.status_code == 200
    mechs = res_get.json()
    assert len(mechs) > 0
    # Для электрика ставка должна быть 1800
    electrician = next(m for m in mechs if m["name"] == "Игорь Электрик")
    assert electrician["hourly_rate"] == 1800


# 4. Тест: Услуги (проверяем НДС 22%)
def test_services_flow():
    # Добавляем услугу
    res_create = client.post(
        "/services/",
        json={"title": "Шиномонтаж R16", "price": 2000},
    )
    assert res_create.status_code == 200

    # Получаем услуги и проверяем НДС 22%
    res_get = client.get("/services/")
    assert res_get.status_code == 200
    services = res_get.json()
    service = next(s for s in services if s["title"] == "Шиномонтаж R16")
    assert service["vat_22"] == 440.0  # 2000 * 0.22 = 440.0
    assert service["warranty_days"] == 30  # так как цена < 3000


# 5. Тест: Заказы (Полный цикл CRUD + Расчеты)
def test_orders_full_crud():
    # [C] Создаем заказ
    res_create = client.post(
        "/orders/",
        json={"car_id": 1, "mechanic_id": 1, "service_id": 1},
    )
    assert res_create.status_code == 200
    order_data = res_create.json()
    order_id = order_data["order"]["id"]
    assert "final_price" in order_data

    # [R - All] Читаем все заказы + средний чек
    res_all = client.get("/orders/")
    assert res_all.status_code == 200
    assert "average_check" in res_all.json()
    assert res_all.json()["orders_count"] > 0

    # [R - One] Читаем конкретный заказ + расчет зарплаты мастера
    res_one = client.get(f"/orders/{order_id}")
    assert res_one.status_code == 200
    assert "mechanic_payout" in res_one.json()

    # [U] Обновляем статус
    res_patch = client.patch(
        f"/orders/{order_id}/status", params={"status": "Выполнен"}
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["new_status"] == "Выполнен"

    # [D] Удаляем заказ с расчетом неустойки и возврата
    res_delete = client.delete(f"/orders/{order_id}")
    assert res_delete.status_code == 200
    del_data = res_delete.json()
    assert "penalty_fee" in del_data
    assert "refund_amount" in del_data


# 6. Тесты ошибок (404 Not Found)
def test_order_not_found():
    # Попытка получить несуществующий заказ
    res = client.get("/orders/999999")
    assert res.status_code == 404

    # Попытка удалить несуществующий заказ
    res_del = client.delete("/orders/999999")
    assert res_del.status_code == 404