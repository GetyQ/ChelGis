import json
from flask import render_template, jsonify, request
from app import app, db
from models import Attraction
import hashlib
import hmac
import os

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
            # Существующие достопримечательности
            Attraction(
                name="Государственный исторический музей Южного Урала",
                description="Государственный исторический музей Южного Урала – современный комплекс, состоящий из нескольких экспозиций и богатых коллекций. Фонд музея насчитывает более 300 тысяч единиц хранения. Здесь представлены археологические находки, уникальные экспонаты природы, культуры и истории Южного Урала от древнейших времен до наших дней. В музее можно увидеть челябинский метеорит, коллекции оружия, нумизматики, этнографии, а также редкие документы и фотографии. Современные интерактивные экспозиции позволяют погрузиться в разные исторические эпохи.",
                lat=55.159388,
                lng=61.402429,
                address="ул. Труда, 100",
                category="Музей",
                image_url="https://avatars.mds.yandex.net/get-altay/6514916/2a00000184c6bacd3dd3d7ebc6e1f60a8d2b/XXL_height"
            ),
            Attraction(
                name="Театр оперы и балета им. М.И. Глинки",
                description="Челябинский театр оперы и балета им. М.И. Глинки – один из ведущих музыкальных театров России. Основанный в 1956 году, театр располагается в величественном здании, построенном в стиле советского неоклассицизма с элементами барокко. В репертуаре представлены классические оперы и балеты, современные постановки и экспериментальные работы. Театр является лауреатом многочисленных премий, включая престижную театральную премию «Золотая маска». Уникальная акустика и великолепная архитектура зрительного зала делают посещение спектаклей незабываемым культурным опытом.",
                lat=55.159806,
                lng=61.394305,
                address="пл. Ярославского, 1",
                category="Культура",
                image_url="https://cheldreateatr.ru/upload/000/u14/001/25a38c2b.jpg"
            ),
            Attraction(
                name="Парк им. Ю.А. Гагарина",
                description="Парк им. Ю.А. Гагарина – крупнейшая зона отдыха в Челябинске площадью более 120 гектаров. Основанный в 1936 году, парк включает в себя обширную лесопарковую зону с хвойными и лиственными деревьями, живописное озеро с лодочной станцией, спортивные площадки и аттракционы. На территории парка расположен экстрим-парк, хаски-центр, экологическая тропа и крупнейшее в регионе колесо обозрения. Парк является любимым местом отдыха челябинцев всех возрастов в любое время года: летом здесь катаются на велосипедах и роликах, а зимой работает один из лучших городских катков и прокладываются лыжные трассы.",
                lat=55.164165,
                lng=61.372882,
                address="ул. Коммуны, 98",
                category="Парк",
                image_url="https://www.tourprom.ru/site_media/images/upload/articles/2019/12/Изображение-30.png"
            ),
            Attraction(
                name="Челябинский областной краеведческий музей",
                description="Челябинский областной краеведческий музей является одним из старейших музеев Урала, основанным в 1923 году. Его коллекция насчитывает более 250 тысяч экспонатов. Экспозиции музея отражают природное богатство края, его геологическую историю, развитие промышленности, этнографию народов Южного Урала и важнейшие исторические события. Особую ценность представляют археологические находки, включая артефакты из древнего города Аркаим. В музее также представлена уникальная коллекция каслинского художественного литья и златоустовской гравюры на стали. Интерактивные экспозиции позволяют погрузиться в историю и природу Челябинской области.",
                lat=55.158631,
                lng=61.402026,
                address="ул. Труда, 100",
                category="Музей",
                image_url="https://avatars.mds.yandex.net/get-altay/5091492/2a00000181d30dd2b83c9c23133b9dec1c1c/XXXL"
            ),
            Attraction(
                name="Площадь Революции",
                description="Площадь Революции – главная историческая площадь Челябинска, сердце города и место проведения важнейших общественных мероприятий. Площадь была оформлена в середине XIX века и носила название Соборной площади до 1917 года. В центре площади установлен памятник В.И. Ленину, созданный скульптором В.И. Друзиным и архитектором Е.В. Александровым и торжественно открытый в 1959 году. Вокруг площади расположены знаковые здания города: Законодательное собрание Челябинской области, Городская дума, драматический театр и концертный зал имени С.С. Прокофьева. Площадь является отправной точкой для многих экскурсионных маршрутов и одной из главных достопримечательностей Челябинска.",
                lat=55.160300,
                lng=61.403119,
                address="Площадь Революции",
                category="Площадь",
                image_url="https://photocentra.ru/i/2018/06/21/3_photocentra_ru_19352037.jpg"
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
            ),
            
            # Новые достопримечательности
            Attraction(
                name="Челябинский государственный академический театр драмы им. Н. Орлова",
                description="Один из старейших драматических театров на Урале, основанный в 1921 году.",
                lat=55.159211,
                lng=61.398113,
                address="пл. Революции, 6",
                category="Культура",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Челябинский городской бор",
                description="Реликтовый сосновый бор, расположенный в черте города, любимое место отдыха горожан.",
                lat=55.153118,
                lng=61.367592,
                address="Челябинский городской бор",
                category="Парк",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Памятник «Сфера любви»",
                description="Современный символ города, известный также как памятник 'Орлёнок'.",
                lat=55.160466,
                lng=61.401102,
                address="Челябинск, площадь Революции",
                category="Памятник",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Челябинский театр кукол им. В. Вольховского",
                description="Уникальный театр кукол, где можно увидеть постановки для детей и взрослых.",
                lat=55.164339,
                lng=61.399531,
                address="ул. Кирова, 8",
                category="Культура",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Торговый центр «Куба»",
                description="Один из популярных торговых центров города, место шоппинга и развлечений.",
                lat=55.160775,
                lng=61.410347,
                address="ул. Цвиллинга, 25",
                category="Развлечения",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Ледовая арена «Трактор»",
                description="Современный спортивный комплекс, домашняя арена хоккейного клуба «Трактор».",
                lat=55.168365,
                lng=61.436694,
                address="ул. 250-летия Челябинска, 38",
                category="Спорт",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Кировка (Челябинский Арбат)",
                description="Пешеходная улица в центре города с множеством скульптур, магазинов и кафе.",
                lat=55.160300,
                lng=61.397841,
                address="ул. Кирова",
                category="Улица",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Музей изобразительных искусств",
                description="Музей с богатой коллекцией произведений искусства российских и зарубежных мастеров.",
                lat=55.163719,
                lng=61.419170,
                address="пл. Революции, 1",
                category="Музей",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Памятник добровольцам-танкистам",
                description="Мемориал, посвященный добровольцам-танкистам Челябинского корпуса времён Великой Отечественной войны.",
                lat=55.160001,
                lng=61.392651,
                address="ул. Коммуны",
                category="Памятник",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Челябинская филармония",
                description="Центр музыкальной культуры города, место проведения концертов классической музыки.",
                lat=55.162356,
                lng=61.399800,
                address="ул. Труда, 92а",
                category="Культура",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Парк «Алое поле»",
                description="Исторический парк с памятниками архитектуры и красивыми аллеями для прогулок.",
                lat=55.162733,
                lng=61.407356,
                address="ул. Красная",
                category="Парк",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Челябинский элеватор (Элеватор №1)",
                description="Архитектурный памятник конструктивизма, один из символов города.",
                lat=55.148753,
                lng=61.424689,
                address="Троицкий тракт, 46",
                category="Архитектура",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Свято-Троицкий храм",
                description="Один из красивейших православных храмов Челябинска.",
                lat=55.164562,
                lng=61.416195,
                address="ул. Кыштымская, 32",
                category="Религия",
                image_url="https://via.placeholder.com/150"
            ),
            Attraction(
                name="Челябинский цирк",
                description="Современное здание цирка, где проходят представления российских и зарубежных артистов.",
                lat=55.169108,
                lng=61.409302,
                address="ул. Кирова, 25",
                category="Развлечения",
                image_url="https://via.placeholder.com/150"
            )
        ]
        
        for attraction in attractions:
            db.session.add(attraction)
        
        db.session.commit()

# Предопределенные маршруты для достопримечательностей
PREDEFINED_ROUTES = [
    {
        "name": "Культурный маршрут",
        "description": "Маршрут по основным культурным достопримечательностям Челябинска",
        "points": ["Театр оперы и балета им. М.И. Глинки", "Челябинский государственный академический театр драмы им. Н. Орлова", 
                  "Челябинская филармония", "Челябинский театр кукол им. В. Вольховского", "Музей изобразительных искусств"]
    },
    {
        "name": "Исторический маршрут",
        "description": "Путешествие по историческим местам города",
        "points": ["Государственный исторический музей Южного Урала", "Челябинский областной краеведческий музей", 
                  "Площадь Революции", "Памятник добровольцам-танкистам", "Железнодорожный вокзал Челябинска"]
    },
    {
        "name": "Зеленый маршрут",
        "description": "Прогулка по паркам и зеленым зонам города",
        "points": ["Парк им. Ю.А. Гагарина", "Челябинский городской бор", "Сквер им. А.С. Пушкина", 
                  "Парк «Алое поле»", "Челябинский зоопарк"]
    },
    {
        "name": "Архитектурный маршрут",
        "description": "Знакомство с архитектурными памятниками Челябинска",
        "points": ["Церковь Александра Невского", "Свято-Троицкий храм", "Железнодорожный вокзал Челябинска", 
                  "Челябинский элеватор (Элеватор №1)", "Кировка (Челябинский Арбат)"]
    },
    {
        "name": "Семейный маршрут",
        "description": "Отличный маршрут для посещения с детьми",
        "points": ["Челябинский зоопарк", "Челябинский цирк", "Челябинский театр кукол им. В. Вольховского", 
                  "Парк им. Ю.А. Гагарина", "Торговый центр «Куба»"]
    },
    {
        "name": "Спортивный маршрут",
        "description": "Маршрут по спортивным объектам города",
        "points": ["Центральный стадион", "Ледовая арена «Трактор»", "Парк им. Ю.А. Гагарина"]
    }
]

# API для получения предопределенных маршрутов
@app.route('/api/predefined-routes')
def get_predefined_routes():
    """API для получения предопределенных маршрутов достопримечательностей"""
    return jsonify(PREDEFINED_ROUTES)

# API для получения информации о конкретном предопределенном маршруте
@app.route('/api/predefined-route/<int:route_id>')
def get_predefined_route(route_id):
    """API для получения информации о конкретном предопределенном маршруте"""
    if route_id < 0 or route_id >= len(PREDEFINED_ROUTES):
        return jsonify({"error": "Маршрут не найден"}), 404
    
    route = PREDEFINED_ROUTES[route_id]
    
    # Получаем полную информацию о точках маршрута
    route_points = []
    for point_name in route["points"]:
        attraction = Attraction.query.filter(Attraction.name.like(f"%{point_name}%")).first()
        if attraction:
            route_points.append(attraction.to_dict())
    
    result = {
        "name": route["name"],
        "description": route["description"],
        "points": route_points
    }
    
    return jsonify(result)

def verify_telegram_hash(init_data):
    """Verify Telegram Web App init data"""
    try:
        # Получаем BOT_TOKEN из переменных окружения
        bot_token = os.environ.get('BOT_TOKEN')
        if not bot_token:
            return False

        # Разбираем init_data
        init_data_dict = dict(param.split('=') for param in init_data.split('&'))
        hash_value = init_data_dict.pop('hash', '')
        
        # Сортируем параметры
        data_check_string = '\n'.join(
            f"{k}={v}" for k, v in sorted(init_data_dict.items())
        )
        
        # Создаем secret_key
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем хеш
        data_check_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return data_check_hash == hash_value
    except Exception:
        return False

@app.route('/telegram')
def telegram_app():
    """Маршрут для Telegram Mini App"""
    # Проверяем init_data от Telegram
    init_data = request.args.get('initData', '')
    if not init_data or not verify_telegram_hash(init_data):
        return 'Unauthorized', 401
    
    return render_template('telegram.html')

@app.route('/api/telegram/share', methods=['POST'])
def telegram_share():
    """API для обработки действий шаринга в Telegram"""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Здесь можно добавить логику обработки шаринга
    return jsonify({'success': True})

# Вызываем инициализацию базы данных при старте приложения
with app.app_context():
    initialize_db()
