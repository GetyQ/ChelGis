import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# создаем приложение
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "челгис-секретный-ключ")

# настройка базы данных (используем SQLite для простоты)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///chelgis.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# инициализируем приложение с расширением
db.init_app(app)

with app.app_context():
    # Импортируем модели здесь, чтобы их таблицы создались
    import models  # noqa: F401
    
    db.create_all()
