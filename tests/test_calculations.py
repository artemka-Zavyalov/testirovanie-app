from app.calculations import (
    calculate_average_check,
    calculate_bonus_points,
    calculate_cancellation_penalty,
    calculate_discount,
    calculate_final_price,
    calculate_hourly_rate,
    calculate_mechanic_salary,
    calculate_refund,
    calculate_vat,
    calculate_warranty_days,
)


def test_calculate_vat():
    assert calculate_vat(1000) == 200.0


def test_calculate_discount():
    assert calculate_discount(1) == 0
    assert calculate_discount(2) == 10
    assert calculate_discount(5) == 10


def test_calculate_final_price():
    assert calculate_final_price(2000, 10) == 1800.0
    assert calculate_final_price(1000, 0) == 1000.0


def test_calculate_mechanic_salary():
    assert calculate_mechanic_salary(2000) == 700.0


def test_calculate_cancellation_penalty():
    assert calculate_cancellation_penalty(1000) == 150.0


def test_calculate_refund():
    assert calculate_refund(1000, 150) == 850.0


def test_calculate_warranty_days():
    assert calculate_warranty_days(4000) == 90
    assert calculate_warranty_days(1500) == 30


def test_calculate_hourly_rate():
    assert calculate_hourly_rate("Главный Моторист") == 2000
    assert calculate_hourly_rate("Автоэлектрик") == 1800
    assert calculate_hourly_rate("Подмастерье") == 1300


def test_calculate_bonus_points():
    assert calculate_bonus_points(10000) == 300


def test_calculate_average_check():
    assert calculate_average_check(10000, 2) == 5000.0
    assert calculate_average_check(0, 0) == 0.0