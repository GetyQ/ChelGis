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

# настройка базы данных SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'chelgis.db')}"
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

if __name__ == '__main__':
    # Запускаем в режиме разработки
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
