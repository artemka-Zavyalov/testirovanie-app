from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import database, models

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Автосервис API")


# Схемы данных
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


# --- 10 ОПЕРАЦИЙ ---


# 1. Создать клиента
@app.post("/clients/", tags=["Клиенты"])
def create_client(
    client: ClientCreate, db: Session = Depends(database.get_db)
):
    db_client = models.Client(name=client.name, phone=client.phone)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


# 2. Получить список всех клиентов
@app.get("/clients/", tags=["Клиенты"])
def get_clients(db: Session = Depends(database.get_db)):
    return db.query(models.Client).all()


# 3. Добавить машину
@app.post("/cars/", tags=["Машины"])
def create_car(car: CarCreate, db: Session = Depends(database.get_db)):
    db_car = models.Car(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


# 4. Получить машины клиента
@app.get("/cars/client/{client_id}", tags=["Машины"])
def get_cars_by_client(client_id: int, db: Session = Depends(database.get_db)):
    return (
        db.query(models.Car).filter(models.Car.client_id == client_id).all()
    )


# 5. Добавить механика
@app.post("/mechanics/", tags=["Механики"])
def create_mechanic(
    mech: MechanicCreate, db: Session = Depends(database.get_db)
):
    db_mech = models.Mechanic(**mech.model_dump())
    db.add(db_mech)
    db.commit()
    db.refresh(db_mech)
    return db_mech


# 6. Добавить услугу
@app.post("/services/", tags=["Услуги"])
def create_service(
    service: ServiceCreate, db: Session = Depends(database.get_db)
):
    db_service = models.Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


# 7. Изменить цену услуги
@app.put("/services/{service_id}", tags=["Услуги"])
def update_service_price(
    service_id: int, new_price: int, db: Session = Depends(database.get_db)
):
    db_service = (
        db.query(models.Service)
        .filter(models.Service.id == service_id)
        .first()
    )
    if not db_service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    db_service.price = new_price
    db.commit()
    return db_service


# 8. Создать заказ
@app.post("/orders/", tags=["Заказы"])
def create_order(order: OrderCreate, db: Session = Depends(database.get_db)):
    db_order = models.Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


# 9. Изменить статус заказа
@app.patch("/orders/{order_id}/status", tags=["Заказы"])
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
    return db_order


# 10. Удалить заказ
@app.delete("/orders/{order_id}", tags=["Заказы"])
def delete_order(order_id: int, db: Session = Depends(database.get_db)):
    db_order = (
        db.query(models.Order).filter(models.Order.id == order_id).first()
    )
    if not db_order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    db.delete(db_order)
    db.commit()
    return {"message": "Заказ удален"}