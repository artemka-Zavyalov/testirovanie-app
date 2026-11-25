import pytest
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


# --- 1. Тесты НДС 22% ---
def test_calculate_vat_standard():
    assert calculate_vat(1000.0) == 220.0


def test_calculate_vat_fractional():
    # 3550 * 0.22 = 781.0
    assert calculate_vat(3550.0) == 781.0


def test_calculate_vat_zero():
    assert calculate_vat(0.0) == 0.0


# --- 2. Тесты Скидок (0% или 10%) ---
def test_calculate_discount_zero_cars():
    assert calculate_discount(0) == 0


def test_calculate_discount_one_car():
    assert calculate_discount(1) == 0


def test_calculate_discount_two_cars_threshold():
    assert calculate_discount(2) == 10


def test_calculate_discount_many_cars():
    assert calculate_discount(10) == 10


# --- 3. Тесты Итоговой цены со скидкой ---
def test_calculate_final_price_with_discount():
    assert calculate_final_price(2000.0, 10) == 1800.0


def test_calculate_final_price_no_discount():
    assert calculate_final_price(1500.0, 0) == 1500.0


# --- 4. Тесты Зарплаты механика (35%) ---
def test_calculate_mechanic_salary_standard():
    assert calculate_mechanic_salary(2000.0) == 700.0


def test_calculate_mechanic_salary_odd_amount():
    # 1333 * 0.35 = 466.55
    assert calculate_mechanic_salary(1333.0) == 466.55


# --- 5 и 6. Тесты Неустойки (15%) и Возврата ---
def test_calculate_cancellation_penalty():
    assert calculate_cancellation_penalty(1000.0) == 150.0


def test_calculate_refund():
    assert calculate_refund(1000.0, 150.0) == 850.0


def test_penalty_plus_refund_equals_total():
    price = 4500.0
    penalty = calculate_cancellation_penalty(price)
    refund = calculate_refund(price, penalty)
    assert penalty + refund == price


# --- 7. Тесты Гарантии (граница 3000 руб) ---
def test_warranty_under_threshold():
    assert calculate_warranty_days(2999.0) == 30


def test_warranty_exact_threshold():
    assert calculate_warranty_days(3000.0) == 90


def test_warranty_above_threshold():
    assert calculate_warranty_days(10000.0) == 90


# --- 8. Тесты Ставки механика (проверка регистра и ролей) ---
def test_hourly_rate_motorist():
    assert calculate_hourly_rate("Главный Моторист") == 2000
    assert calculate_hourly_rate("моторист-стажер") == 2000


def test_hourly_rate_electrician():
    assert calculate_hourly_rate("АВТОЭЛЕКТРИК") == 1800


def test_hourly_rate_default():
    assert calculate_hourly_rate("Слесарь ходовой части") == 1300


# --- 9. Тесты Бонусных баллов (3%) ---
def test_bonus_points_standard():
    assert calculate_bonus_points(10000.0) == 300


def test_bonus_points_small_amount():
    assert calculate_bonus_points(25.0) == 0  # 25 * 0.03 = 0.75 -> int 0


# --- 10. Тесты Среднего чека ---
def test_average_check_standard():
    assert calculate_average_check(9000.0, 3) == 3000.0


def test_average_check_zero_division():
    # Проверка защиты от деления на 0
    assert calculate_average_check(0.0, 0) == 0.0