import json
from flask import render_template, jsonify, request
from app import app, db
from models import Attraction

@app.route('/')
def index():
    """Главная страница приложения"""
    return render_template('index.html')

@app.route('/about')
def about():
    """Страница с информацией о приложении"""
    return render_template('about.html')

@app.route('/api/attractions')
def get_attractions():
    """API для получения всех достопримечательностей"""
    attractions = Attraction.query.all()
    return jsonify([attraction.to_dict() for attraction in attractions])

@app.route('/api/attraction/<int:attraction_id>')
def get_attraction(attraction_id):
    """API для получения информации о конкретной достопримечательности"""
    attraction = Attraction.query.get_or_404(attraction_id)
    return jsonify(attraction.to_dict())

@app.route('/api/categories')
def get_categories():
    """API для получения списка всех категорий достопримечательностей"""
    categories = db.session.query(Attraction.category).distinct().all()
    return jsonify([category[0] for category in categories if category[0]])

@app.route('/api/search')
def search_attractions():
    """API для поиска достопримечательностей по названию"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    attractions = Attraction.query.filter(
        Attraction.name.ilike(f'%{query}%')
    ).all()
    
    return jsonify([attraction.to_dict() for attraction in attractions])

# Функция инициализации базы данных тестовыми данными
def initialize_db():
    """Инициализация базы данных, если она пуста"""
    if Attraction.query.count() == 0:
        # Основные достопримечательности Челябинска
        attractions = [
            Attraction(
                name="Государственный исторический музей Южного Урала",
                description="Один из крупнейших музеев Урала с богатой коллекцией исторических артефактов.",
                lat=55.159388,
                lng=61.402429,
                address="ул. Труда, 100",
                category="Музей",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Театр оперы и балета им. М.И. Глинки",
                description="Знаменитый оперный театр, одна из архитектурных жемчужин Челябинска.",
                lat=55.159806,
                lng=61.394305,
                address="пл. Ярославского, 1",
                category="Культура",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Парк им. Ю.А. Гагарина",
                description="Крупнейший парк города с аттракционами, зоопарком и местами для отдыха.",
                lat=55.164165,
                lng=61.372882,
                address="ул. Коммуны, 98",
                category="Парк",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Челябинский областной краеведческий музей",
                description="Музей, посвященный природе и истории Челябинской области.",
                lat=55.158631,
                lng=61.402026,
                address="ул. Труда, 100",
                category="Музей",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Площадь Революции",
                description="Центральная площадь Челябинска с памятником В.И. Ленину.",
                lat=55.160300,
                lng=61.403119,
                address="Площадь Революции",
                category="Площадь",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Сквер им. А.С. Пушкина",
                description="Уютный сквер в центре города с фонтаном и памятником Пушкину.",
                lat=55.155966,
                lng=61.392933,
                address="ул. Пушкина",
                category="Парк",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Челябинский зоопарк",
                description="Зоопарк с разнообразной коллекцией животных со всего мира.",
                lat=55.163543,
                lng=61.367906,
                address="ул. Труда, 191",
                category="Зоопарк",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Церковь Александра Невского",
                description="Красивый православный храм, построенный в конце XIX века.",
                lat=55.151906,
                lng=61.379844,
                address="ул. Цвиллинга, 62",
                category="Религия",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Железнодорожный вокзал Челябинска",
                description="Историческое здание вокзала, архитектурный памятник города.",
                lat=55.150811,
                lng=61.414520,
                address="Привокзальная площадь, 1",
                category="Архитектура",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Центральный стадион",
                description="Главная спортивная арена города Челябинска.",
                lat=55.163173,
                lng=61.390619,
                address="ул. Коммуны, 98",
                category="Спорт",
                image_url="https://via.placeholder.com/150"
            )
        ]
        
        for attraction in attractions:
            db.session.add(attraction)
        
        db.session.commit()

# Вызываем инициализацию базы данных при старте приложения
with app.app_context():
    initialize_db()
