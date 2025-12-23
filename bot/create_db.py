# create_database.py (обновленная версия)
import sqlite3
import os
import random

# Данные автомобилей с годами выпуска (добавили год выпуска как 12-й параметр)
cars_data = [
    # Такси - бюджет (5 машин)
    ("Kia Rio", "taxi", "budget", 1350000, 7.8, 4.6, 4.3, None,
     "Идеален для городских поездок", "Низкое ТО, доступные запчасти, просторный салон", 2022),

    ("Hyundai Solaris", "taxi", "budget", 1450000, 7.5, 4.4, 4.1, None,
     "Бюджетный вариант для такси", "Экономичный, надежный, недорогой в обслуживании", 2023),

    ("Renault Logan", "taxi", "budget", 1250000, 8.2, 4.2, 4.0, None,
     "Простой и надежный", "Дешевый в обслуживании, хорошая проходимость", 2021),

    ("Lada Vesta", "taxi", "budget", 1400000, 7.9, 4.3, 4.1, None,
     "Отечественный вариант", "Недорогие запчасти, неприхотливый", 2022),

    ("Skoda Fabia", "taxi", "budget", 1480000, 7.4, 4.5, 4.2, None,
     "Европейское качество", "Надежность, комфорт, экономичность", 2023),

    # Такси - средний (5 машин)
    ("Volkswagen Polo", "taxi", "medium", 1850000, 7.9, 4.7, 4.5, None,
     "Хороший выбор для такси", "Комфорт, безопасность, высокое качество сборки", 2022),

    ("Skoda Rapid", "taxi", "medium", 1680000, 7.6, 4.5, 4.2, None,
     "Сбалансированный вариант", "Надежность, экономичность, европейское качество", 2021),

    ("Kia Cerato", "taxi", "medium", 1950000, 8.1, 4.8, 4.6, None,
     "Комфортный седан", "Просторный салон, богатая комплектация", 2023),

    ("Hyundai Elantra", "taxi", "medium", 1780000, 7.8, 4.6, 4.4, None,
     "Современный дизайн", "Технологичность, надежность, комфорт", 2022),

    ("Toyota Corolla", "taxi", "medium", 2200000, 8.3, 4.9, 4.7, None,
     "Мировой бестселлер", "Высочайшая надежность, отличная экономичность", 2023),

    # Такси - премиум (5 машин)
    ("Toyota Camry", "taxi", "premium", 2850000, 8.2, 4.8, 4.7, None,
     "Комфорт бизнес-класса", "Надежность, комфорт, статус, высокие технологии", 2023),

    ("Skoda Octavia", "taxi", "premium", 2650000, 8.0, 4.7, 4.6, None,
     "Практичный премиум", "Простор, комфорт, технологии", 2022),

    ("Volkswagen Passat", "taxi", "premium", 2950000, 8.3, 4.9, 4.8, None,
     "Немецкое качество", "Комфорт, безопасность, статус", 2023),

    ("Hyundai Sonata", "taxi", "premium", 2750000, 8.1, 4.8, 4.7, None,
     "Корейский премиум", "Технологии, дизайн, комфорт", 2022),

    ("Kia K5", "taxi", "premium", 2800000, 8.2, 4.9, 4.8, None,
     "Спортивный седан", "Динамика, дизайн, технологии", 2023),

    # Курьерские - бюджет (5 машин)
    ("Lada Largus", "courier", "budget", 1650000, 7.2, 4.5, 3.9, 3.3,
     "Идеален для доставки мелких грузов", "Вместительный багажник, проходимость, дешевое ТО", 2021),

    ("Renault Sandero Stepway", "courier", "budget", 1550000, 7.5, 4.3, 4.0, 2.8,
     "Для городской доставки", "Проходимость, экономичность, надежность", 2022),

    ("Datsun mi-DO", "courier", "budget", 1250000, 7.8, 4.0, 3.8, 2.5,
     "Минимальный бюджет", "Экономичность, маневренность в городе", 2020),

    ("Lada Granta Liftback", "courier", "budget", 1350000, 7.6, 4.2, 3.9, 2.9,
     "Универсальный вариант", "Низкая цена, доступность запчастей", 2021),

    ("Chevrolet Aveo", "courier", "budget", 1480000, 7.4, 4.4, 4.1, 3.1,
     "Для небольших грузов", "Надежность, экономичность, комфорт", 2022),

    # Курьерские - средний (5 машин)
    ("Citroen Berlingo", "courier", "medium", 1950000, 7.6, 4.3, 4.1, 3.7,
     "Мощный вариант для частых поездок", "Мощный двигатель, большой объем, комфорт", 2022),

    ("Volkswagen Caddy", "courier", "medium", 2100000, 7.9, 4.5, 4.3, 3.9,
     "Немецкая практичность", "Качество, надежность, вместительность", 2023),

    ("Peugeot Partner", "courier", "medium", 1880000, 7.7, 4.4, 4.2, 3.6,
     "Французский подход", "Комфорт, экономичность, практичность", 2021),

    ("Fiat Doblo", "courier", "medium", 1850000, 7.5, 4.3, 4.1, 3.8,
     "Итальянский дизайн", "Вместительность, экономичность, надежность", 2022),

    ("Skoda Roomster", "courier", "medium", 1980000, 7.8, 4.6, 4.3, 3.5,
     "Универсальный транспорт", "Гибкое пространство, комфорт, экономичность", 2021),

    # Курьерские - премиум (5 машин)
    ("Ford Transit Connect", "courier", "premium", 2150000, 8.1, 4.6, 4.2, 3.9,
     "Для крупных грузов", "Максимальный объем, надежность, удобство", 2023),

    ("Mercedes-Benz Citan", "courier", "premium", 2850000, 8.4, 4.8, 4.6, 4.1,
     "Премиум-курьер", "Качество, комфорт, статус", 2023),

    ("Volkswagen Transporter", "courier", "premium", 3200000, 8.3, 4.7, 4.5, 4.3,
     "Легендарная модель", "Надежность, вместимость, комфорт", 2022),

    ("Peugeot Expert", "courier", "premium", 2750000, 8.2, 4.7, 4.4, 4.2,
     "Профессиональный транспорт", "Мощность, вместимость, экономичность", 2023),

    ("Toyota Proace City", "courier", "premium", 2650000, 8.3, 4.8, 4.5, 4.0,
     "Японское качество", "Надежность, комфорт, практичность", 2023),
]


def create_database():
    """Создает базу данных и таблицы"""

    # Создаем папку data, если её нет
    os.makedirs("data", exist_ok=True)

    # Подключаемся к БД
    conn = sqlite3.connect("data/cars.db")
    cursor = conn.cursor()

    # Удаляем старую таблицу если существует
    cursor.execute("DROP TABLE IF EXISTS cars")

    # Создаем таблицу автомобилей с полем year
    cursor.execute("""
    CREATE TABLE cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price_range TEXT NOT NULL,
        price INTEGER NOT NULL,
        fuel_consumption REAL,
        reliability REAL,
        comfort REAL,
        cargo_volume REAL,
        description TEXT,
        advantages TEXT,
        year INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Создаем другие таблицы (если их нет)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        budget_range TEXT NOT NULL,
        car_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (car_id) REFERENCES cars (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (car_id) REFERENCES cars (id),
        UNIQUE(user_id, car_id)
    )
    """)

    # Вставляем данные автомобилей
    for car in cars_data:
        cursor.execute("""
        INSERT INTO cars (
            name, category, price_range, price, fuel_consumption,
            reliability, comfort, cargo_volume, description, advantages, year
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, car)

    # Сохраняем изменения
    conn.commit()
    conn.close()

    print("✅ База данных успешно создана!")
    print(f"✅ Добавлено {len(cars_data)} автомобилей с годами выпуска")


if __name__ == "__main__":
    create_database()