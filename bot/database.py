import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_path="data/cars.db"):
        """Инициализация базы данных - ТОЛЬКО ПОДКЛЮЧЕНИЕ"""
        self.db_path = db_path

        # Проверяем, существует ли БД
        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"❌ База данных не найдена: {db_path}\n"
                f"Создайте базу командой: python create_database.py"
            )

        print(f"✅ База данных подключена: {db_path}")

    def get_connection(self):
        """Создает соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Чтобы получать словари
        return conn

    def get_cars_by_filters(self, category, price_range, limit=5):
        """Получает автомобили по категории и бюджету (теперь по цене)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Определяем ценовые диапазоны в зависимости от выбранного бюджета
        if price_range == "budget":
            price_condition = "price <= 1500000"
        elif price_range == "medium":
            price_condition = "price > 1500000 AND price <= 2500000"
        elif price_range == "premium":
            price_condition = "price > 2500000"
        else:
            price_condition = "1=1"  # Если бюджет не определен, показываем все

        query = f"""
        SELECT * FROM cars 
        WHERE category = ? AND {price_condition}
        ORDER BY price
        LIMIT ?
        """

        cursor.execute(query, (category, limit))

        cars = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cars

    # Остальные методы остаются без изменений...
    def get_car_by_id(self, car_id):
        """Получает автомобиль по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
        car = cursor.fetchone()
        conn.close()

        return dict(car) if car else None

    def save_user(self, telegram_id, username=None):
        """Сохраняет или обновляет пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT OR IGNORE INTO users (telegram_id, username) 
        VALUES (?, ?)
        """, (telegram_id, username))

        conn.commit()
        conn.close()

    def save_query(self, user_id, category, budget_range, car_id=None):
        """Сохраняет запрос пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO queries (user_id, category, budget_range, car_id)
        VALUES (?, ?, ?, ?)
        """, (user_id, category, budget_range, car_id))

        conn.commit()
        conn.close()

    def add_to_favorites(self, user_id, car_id):
        """Добавляет автомобиль в избранное пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT OR IGNORE INTO favorites (user_id, car_id)
            VALUES (?, ?)
            """, (user_id, car_id))

            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении в избранное: {e}")
            return False
        finally:
            conn.close()

    def remove_from_favorites(self, user_id, car_id):
        """Удаляет автомобиль из избранного"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM favorites 
        WHERE user_id = ? AND car_id = ?
        """, (user_id, car_id))

        conn.commit()
        conn.close()

    def is_in_favorites(self, user_id, car_id):
        """Проверяет, есть ли авто в избранном у пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT COUNT(*) as count FROM favorites 
        WHERE user_id = ? AND car_id = ?
        """, (user_id, car_id))

        result = cursor.fetchone()
        conn.close()

        return result["count"] > 0 if result else False

    def get_user_favorites(self, user_id):
        """Получает все автомобили из избранного пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT c.* FROM cars c
        JOIN favorites f ON c.id = f.car_id
        WHERE f.user_id = ?
        ORDER BY f.added_at DESC
        """, (user_id,))

        cars = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cars


    def get_cars_by_price_range(self, category, min_price=None, max_price=None, limit=5):
        #Получает автомобили по конкретному ценовому диапазону
        conn = self.get_connection()
        cursor = conn.cursor()

        conditions = ["category = ?"]
        params = [category]

        if min_price is not None:
            conditions.append("price >= ?")
            params.append(min_price)

        if max_price is not None:
            conditions.append("price <= ?")
            params.append(max_price)

        where_clause = " AND ".join(conditions)
        params.append(limit)

        query = f"""
        SELECT * FROM cars 
        WHERE {where_clause}
        ORDER BY price
        LIMIT ?
        """

        cursor.execute(query, params)
        cars = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cars


def add_to_comparison(self, user_id, car_id):
    #Добавляет автомобиль к сравнению пользователя
    conn = self.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT OR IGNORE INTO comparisons (user_id, car_id)
        VALUES (?, ?)
        """, (user_id, car_id))

        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка при добавлении к сравнению: {e}")
        return False
    finally:
        conn.close()


def get_user_comparisons(self, user_id):
    #Получает все автомобили из сравнения пользователя
    conn = self.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT c.* FROM cars c
    JOIN comparisons comp ON c.id = comp.car_id
    WHERE comp.user_id = ?
    ORDER BY comp.added_at
    """, (user_id,))

    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cars


def clear_user_comparisons(self, user_id):
    #Очищает сравнение пользователя
    conn = self.get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM comparisons WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()


def remove_from_comparison(self, user_id, car_id):
    #Удаляет автомобиль из сравнения
    conn = self.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM comparisons 
    WHERE user_id = ? AND car_id = ?
    """, (user_id, car_id))

    conn.commit()
    conn.close()