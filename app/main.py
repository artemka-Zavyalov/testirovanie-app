import os
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
import yaml
from . import database, models

# Создаем таблицы в БД
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Автосервис API")


# Автозагрузка данных из fixtures.yml при старте
@app.on_event("startup")
def load_fixtures():
    db = database.SessionLocal()
    # Если база пустая — загружаем YAML
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

                # Сбрасываем счетчики ID, чтобы не было ошибки UniqueViolation
                tables = ["clients", "cars", "mechanics", "services", "orders"]
                for table in tables:
                    db.execute(
                        text(
                            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 1)) FROM {table};"
                        )
                    )
                db.commit()
    db.close()


# --- СХЕМЫ ДАННЫХ (Pydantic) ---
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


# ==========================================
# 1. КЛИЕНТЫ (GET + POST)
# ==========================================
@app.get("/clients/", tags=["1. Клиенты"])
def get_clients(db: Session = Depends(database.get_db)):
    """Получить всех клиентов"""
    return db.query(models.Client).all()


@app.post("/clients/", tags=["1. Клиенты"])
def create_client(
    client: ClientCreate, db: Session = Depends(database.get_db)
):
    """Добавить клиента"""
    db_client = models.Client(name=client.name, phone=client.phone)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


# ==========================================
# 2. МАШИНЫ (GET + POST)
# ==========================================
@app.get("/cars/", tags=["2. Машины"])
def get_cars(db: Session = Depends(database.get_db)):
    """Получить все машины"""
    return db.query(models.Car).all()


@app.post("/cars/", tags=["2. Машины"])
def create_car(car: CarCreate, db: Session = Depends(database.get_db)):
    """Добавить машину"""
    db_car = models.Car(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


# ==========================================
# 3. МЕХАНИКИ (GET + POST)
# ==========================================
@app.get("/mechanics/", tags=["3. Механики"])
def get_mechanics(db: Session = Depends(database.get_db)):
    """Получить всех механиков"""
    return db.query(models.Mechanic).all()


@app.post("/mechanics/", tags=["3. Механики"])
def create_mechanic(
    mech: MechanicCreate, db: Session = Depends(database.get_db)
):
    """Нанять нового механика"""
    db_mech = models.Mechanic(**mech.model_dump())
    db.add(db_mech)
    db.commit()
    db.refresh(db_mech)
    return db_mech


# ==========================================
# 4. УСЛУГИ (GET + POST)
# ==========================================
@app.get("/services/", tags=["4. Услуги"])
def get_services(db: Session = Depends(database.get_db)):
    """Получить прайс-лист услуг"""
    return db.query(models.Service).all()


@app.post("/services/", tags=["4. Услуги"])
def create_service(
    service: ServiceCreate, db: Session = Depends(database.get_db)
):
    """Добавить услугу в прайс-лист"""
    db_service = models.Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


# ==========================================
# 5. ЗАКАЗЫ (ПОЛНЫЙ CRUD)
# ==========================================
# [C - Create]
@app.post("/orders/", tags=["5. Заказы (CRUD)"])
def create_order(order: OrderCreate, db: Session = Depends(database.get_db)):
    """Создать новый заказ-наряд"""
    db_order = models.Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


# [R - Read All]
@app.get("/orders/", tags=["5. Заказы (CRUD)"])
def get_all_orders(db: Session = Depends(database.get_db)):
    """Получить список всех заказов"""
    return db.query(models.Order).all()


# [R - Read One]
@app.get("/orders/{order_id}", tags=["5. Заказы (CRUD)"])
def get_order_by_id(order_id: int, db: Session = Depends(database.get_db)):
    """Получить один конкретный заказ по его ID"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order


# [U - Update]
@app.patch("/orders/{order_id}/status", tags=["5. Заказы (CRUD)"])
def update_order_status(
    order_id: int, status: str, db: Session = Depends(database.get_db)
):
    """Обновить статус заказа (например: В работе -> Готов)"""
    db_order = (
        db.query(models.Order).filter(models.Order.id == order_id).first()
    )
    if not db_order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order


# [D - Delete]
@app.delete("/orders/{order_id}", tags=["5. Заказы (CRUD)"])
def delete_order(order_id: int, db: Session = Depends(database.get_db)):
    """Удалить заказ"""
    db_order = (
        db.query(models.Order).filter(models.Order.id == order_id).first()
    )
    if not db_order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    db.delete(db_order)
    db.commit()
    return {"message": f"Заказ с ID {order_id} успешно удален"}