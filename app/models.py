from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


# 1. Таблица Клиентов
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    cars = relationship("Car", back_populates="owner")


# 2. Таблица Автомобилей
class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    model = Column(String)
    vin = Column(String)
    client_id = Column(Integer, ForeignKey("clients.id"))
    owner = relationship("Client", back_populates="cars")


# 3. Таблица Механиков
class Mechanic(Base):
    __tablename__ = "mechanics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    specialty = Column(String)


# 4. Таблица Услуг
class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Integer)


# 5. Таблица Заказов
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    mechanic_id = Column(Integer, ForeignKey("mechanics.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    status = Column(String, default="В работе")