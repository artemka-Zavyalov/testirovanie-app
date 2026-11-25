# app/calculations.py


# Расчет 1: НДС (22%) от суммы
def calculate_vat(price: float) -> float:
    return round(price * 0.22, 2)


# Расчет 2: Скидка клиента в зависимости от количества его авто (0% или 10%)
def calculate_discount(cars_count: int) -> int:
    return 10 if cars_count >= 2 else 0


# Расчет 3: Итоговая стоимость с учетом скидки
def calculate_final_price(base_price: float, discount_percent: int) -> float:
    discount_amount = base_price * (discount_percent / 100)
    return round(base_price - discount_amount, 2)


# Расчет 4: Доля механика за работу (35% от стоимости услуги)
def calculate_mechanic_salary(service_price: float) -> float:
    return round(service_price * 0.35, 2)


# Расчет 5: Штраф/неустойка при отмене заказа (15% от стоимости)
def calculate_cancellation_penalty(order_price: float) -> float:
    return round(order_price * 0.15, 2)


# Расчет 6: Сумма возврата клиенту при отмене заказа
def calculate_refund(
    order_price: float, penalty: float
) -> float:
    return round(order_price - penalty, 2)


# Расчет 7: Срок гарантии на работу (дней): если услуга дороже 3000 руб — 90 дней, иначе 30
def calculate_warranty_days(price: float) -> int:
    return 90 if price >= 3000 else 30


# Расчет 8: Почасовая ставка механика в зависимости от квалификации
def calculate_hourly_rate(specialty: str) -> int:
    if "моторист" in specialty.lower():
        return 2000
    if "электрик" in specialty.lower():
        return 1800
    return 1300


# Расчет 9: Начисление бонусных баллов клиенту (3% кэшбэк)
def calculate_bonus_points(spent_amount: float) -> int:
    return int(spent_amount * 0.03)


# Расчет 10: Средний чек по списку заказов
def calculate_average_check(total_revenue: float, orders_count: int) -> float:
    if orders_count == 0:
        return 0.0
    return round(total_revenue / orders_count, 2)