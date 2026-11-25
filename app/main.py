import os
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
import yaml
from . import calculations, database, models

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Автосервис API с расчетами")


@app.on_event("startup")
def load_fixtures():
    db = database.SessionLocal()
    if db.query(models.Client).count() == 0:
        fixture_path = "fixtures.yml"
        if os.path.exists(fixture_path):
            with open(fixture_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                for item in data.get("clients", []):
                    db.add(models.Client(**item))
                for item in data.get("cars", []):
                    db.add(models.Car(**item))
                for item in data.get("mechanics", []):
                    db.add(models.Mechanic(**item))
                for item in data.get("services", []):
                    db.add(models.Service(**item))
                db.commit()
                for item in data.get("orders", []):
                    db.add(models.Order(**item))
                db.commit()
                tables = ["clients", "cars", "mechanics", "services", "orders"]
                for table in tables:
                    db.execute(
                        text(
                            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 1)) FROM {table};"
                        )
                    )
                db.commit()
    db.close()


# Схемы
class ClientCreate(BaseModel):
    name: str
    phone: str


class CarCreate(BaseModel):
    brand: str
    model: str
    vin: str
    client_id: int


class MechanicCreate(BaseModel):
    name: str
    specialty: str


class ServiceCreate(BaseModel):
    title: str
    price: int


class OrderCreate(BaseModel):
    car_id: int
    mechanic_id: int
    service_id: int


# ================= КЛИЕНТЫ =================
# Метод 1: [GET] Список клиентов с расчетом скидки
@app.get("/clients/", tags=["1. Клиенты"])
def get_clients(db: Session = Depends(database.get_db)):
    clients = db.query(models.Client).all()
    res = []
    for c in clients:
        discount = calculations.calculate_discount(len(c.cars))
        res.append(
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "cars_count": len(c.cars),
                "personal_discount": f"{discount}%",
            }
        )
    return res


# Метод 2: [POST] Добавить клиента (с расчетом приветственного бонуса)
@app.post("/clients/", tags=["1. Клиенты"])
def create_client(
    client: ClientCreate, db: Session = Depends(database.get_db)
):
    db_client = models.Client(name=client.name, phone=client.phone)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return {
        "client": db_client,
        "welcome_bonus_points": calculations.calculate_bonus_points(5000),
    }


# ================= МАШИНЫ =================
# Метод 3: [GET] Все машины
@app.get("/cars/", tags=["2. Машины"])
def get_cars(db: Session = Depends(database.get_db)):
    return db.query(models.Car).all()


# Метод 4: [POST] Добавить машину
@app.post("/cars/", tags=["2. Машины"])
def create_car(car: CarCreate, db: Session = Depends(database.get_db)):
    db_car = models.Car(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


# ================= МЕХАНИКИ =================
# Метод 5: [GET] Список механиков с расчетом почасовой ставки
@app.get("/mechanics/", tags=["3. Механики"])
def get_mechanics(db: Session = Depends(database.get_db)):
    mechs = db.query(models.Mechanic).all()
    res = []
    for m in mechs:
        res.append(
            {
                "id": m.id,
                "name": m.name,
                "specialty": m.specialty,
                "hourly_rate": calculations.calculate_hourly_rate(m.specialty),
            }
        )
    return res


# Метод 6: [POST] Нанять механика
@app.post("/mechanics/", tags=["3. Механики"])
def create_mechanic(
    mech: MechanicCreate, db: Session = Depends(database.get_db)
):
    db_mech = models.Mechanic(**mech.model_dump())
    db.add(db_mech)
    db.commit()
    db.refresh(db_mech)
    return db_mech


# ================= УСЛУГИ =================
# Метод 7: [GET] Прайс-лист с расчетом НДС 22% и гарантией
@app.get("/services/", tags=["4. Услуги"])
def get_services(db: Session = Depends(database.get_db)):
    services = db.query(models.Service).all()
    res = []
    for s in services:
        res.append(
            {
                "id": s.id,
                "title": s.title,
                "price": s.price,
                "vat_22": calculations.calculate_vat(s.price),  # НДС 22%
                "warranty_days": calculations.calculate_warranty_days(s.price),
            }
        )
    return res


# Метод 8: [POST] Добавить услугу
@app.post("/services/", tags=["4. Услуги"])
def create_service(
    service: ServiceCreate, db: Session = Depends(database.get_db)
):
    db_service = models.Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


# ================= ЗАКАЗЫ (CRUD + РАСЧЕТЫ) =================
# Метод 9: [POST] Создать заказ (расчет итоговой цены со скидкой)
@app.post("/orders/", tags=["5. Заказы"])
def create_order(order: OrderCreate, db: Session = Depends(database.get_db)):
    service = (
        db.query(models.Service)
        .filter(models.Service.id == order.service_id)
        .first()
    )
    car = db.query(models.Car).filter(models.Car.id == order.car_id).first()
    if not service or not car:
        raise HTTPException(status_code=400, detail="Машина или услуга не найдена")

    client_cars = (
        db.query(models.Car).filter(models.Car.client_id == car.client_id).all()
    )
    discount = calculations.calculate_discount(len(client_cars))
    final_price = calculations.calculate_final_price(service.price, discount)

    db_order = models.Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return {
        "order": db_order,
        "base_price": service.price,
        "applied_discount": f"{discount}%",
        "final_price": final_price,
    }


# Метод 10: [GET] Все заказы + расчет общей выручки и среднего чека
@app.get("/orders/", tags=["5. Заказы"])
def get_all_orders(db: Session = Depends(database.get_db)):
    orders = db.query(models.Order).all()
    total_rev = sum(
        db.query(models.Service)
        .filter(models.Service.id == o.service_id)
        .first()
        .price
        for o in orders
        if o.service_id
    )
    avg_check = calculations.calculate_average_check(total_rev, len(orders))
    return {
        "orders_count": len(orders),
        "total_revenue": total_rev,
        "average_check": avg_check,
        "orders": orders,
    }


# Метод 11: [GET/{id}] Получить заказ с расчетом зарплаты мастера
@app.get("/orders/{order_id}", tags=["5. Заказы"])
def get_order_by_id(order_id: int, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    service = (
        db.query(models.Service)
        .filter(models.Service.id == order.service_id)
        .first()
    )
    salary = calculations.calculate_mechanic_salary(service.price)
    return {"order": order, "service_price": service.price, "mechanic_payout": salary}


# Метод 12: [PATCH] Обновить статус
@app.patch("/orders/{order_id}/status", tags=["5. Заказы"])
def update_order_status(
    order_id: int, status: str, db: Session = Depends(database.get_db)
):
    db_order = (
        db.query(models.Order).filter(models.Order.id == order_id).first()
    )
    if not db_order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    db_order.status = status
    db.commit()
    return {"order_id": order_id, "new_status": status}


# Метод 13: [DELETE] Отмена заказа с расчетом неустойки и возврата
@app.delete("/orders/{order_id}", tags=["5. Заказы"])
def delete_order(order_id: int, db: Session = Depends(database.get_db)):
    db_order = (
        db.query(models.Order).filter(models.Order.id == order_id).first()
    )
    if not db_order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    service = (
        db.query(models.Service)
        .filter(models.Service.id == db_order.service_id)
        .first()
    )
    penalty = calculations.calculate_cancellation_penalty(service.price)
    refund = calculations.calculate_refund(service.price, penalty)

    db.delete(db_order)
    db.commit()
    return {
        "message": "Заказ отменен",
        "service_price": service.price,
        "penalty_fee": penalty,
        "refund_amount": refund,
    }