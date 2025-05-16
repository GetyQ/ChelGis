from app import db
import sqlite3
import os
import json
from datetime import datetime

class Attraction(db.Model):
    """Модель достопримечательности"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    lat = db.Column(db.Float, nullable=False)  # широта
    lng = db.Column(db.Float, nullable=False)  # долгота
    address = db.Column(db.String(200))
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(200))  # URL изображения (опционально)

    def to_dict(self):
        """Преобразует объект в словарь для передачи в JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'lat': self.lat,
            'lng': self.lng,
            'address': self.address,
            'category': self.category,
            'image_url': self.image_url
        }

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'chelgis.db')
    return sqlite3.connect(db_path)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Создаем таблицу избранного, если её нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            attraction_id INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (attraction_id) REFERENCES attraction(id),
            PRIMARY KEY (attraction_id)
        )
    """)
    
    # Создаем таблицу кэша
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def toggle_favorite(attraction_id):
    """Добавить/удалить достопримечательность из избранного"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже в избранном
    cursor.execute("SELECT 1 FROM favorites WHERE attraction_id = ?", (attraction_id,))
    exists = cursor.fetchone() is not None
    
    if exists:
        cursor.execute("DELETE FROM favorites WHERE attraction_id = ?", (attraction_id,))
    else:
        cursor.execute("INSERT INTO favorites (attraction_id) VALUES (?)", (attraction_id,))
    
    conn.commit()
    conn.close()
    return not exists

def get_favorites():
    """Получить список избранных достопримечательностей"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.id, a.name, a.description, a.category, a.lat, a.lng
        FROM attraction a
        JOIN favorites f ON a.id = f.attraction_id
        ORDER BY f.added_at DESC
    """)
    
    favorites = cursor.fetchall()
    conn.close()
    return favorites

def is_favorite(attraction_id):
    """Проверить, находится ли достопримечательность в избранном"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM favorites WHERE attraction_id = ?", (attraction_id,))
    is_fav = cursor.fetchone() is not None
    
    conn.close()
    return is_fav

def cache_data(key, data, ttl_hours=24):
    """Кэширование данных"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Сохраняем данные в JSON формате
    cursor.execute("""
        INSERT OR REPLACE INTO cache (key, value, timestamp)
        VALUES (?, ?, datetime('now'))
    """, (key, json.dumps(data)))
    
    conn.commit()
    conn.close()

def get_cached_data(key, ttl_hours=24):
    """Получение кэшированных данных"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT value FROM cache 
        WHERE key = ? AND 
        datetime(timestamp, '+' || ? || ' hours') > datetime('now')
    """, (key, ttl_hours))
    
    result = cursor.fetchone()
    conn.close()
    
    return json.loads(result[0]) if result else None

# Инициализируем базу данных при импорте модуля
init_db()
