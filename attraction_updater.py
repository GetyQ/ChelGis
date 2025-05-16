import os
import time
import json
import trafilatura
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

def get_website_text_content(url):
    """
    Извлечь основной текстовый контент веб-страницы
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        return None
    except Exception as e:
        print(f"Ошибка при скрапинге {url}: {e}")
        return None

def search_attraction_info(attraction_name):
    """
    Поиск информации о достопримечательности в Интернете
    """
    query = f"{attraction_name} Челябинск официальный сайт"
    encoded_query = quote(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Пытаемся найти первую ссылку результатов поиска
            search_results = soup.select('.yuRUbf a')
            if not search_results:
                search_results = soup.select('.g .rc .r a')
            if not search_results:
                search_results = soup.select('a[href^="http"]')
                
            if search_results:
                # Отбрасываем поисковые и неподходящие сайты
                for result in search_results:
                    link = result.get('href')
                    if link and link.startswith('http') and not any(domain in link for domain in [
                        'google.com', 'youtube.com', 'facebook.com', 'instagram.com', 
                        'wikipedia.org', 'twitter.com', 'vk.com'
                    ]):
                        return link
    except Exception as e:
        print(f"Ошибка при поиске информации о {attraction_name}: {e}")
    
    # Если поиск не дал результатов, пробуем википедию
    query = f"{attraction_name} Челябинск site:ru.wikipedia.org"
    encoded_query = quote(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            wiki_links = [a.get('href') for a in soup.select('a[href^="https://ru.wikipedia.org/wiki/"]')]
            if wiki_links:
                return wiki_links[0]
    except Exception as e:
        print(f"Ошибка при поиске в Wikipedia для {attraction_name}: {e}")
    
    return None

def get_attraction_description(attraction_name):
    """
    Получить подробное описание достопримечательности из найденных источников
    """
    website_url = search_attraction_info(attraction_name)
    if not website_url:
        print(f"Не удалось найти информацию о {attraction_name}")
        return None
    
    print(f"Найден источник для {attraction_name}: {website_url}")
    
    # Извлекаем текст с найденной страницы
    content = get_website_text_content(website_url)
    if not content:
        print(f"Не удалось получить контент с {website_url}")
        return None
    
    # Извлекаем наиболее релевантную информацию
    # Ограничиваем описание 1000 символами, чтобы оно было информативным, но не слишком длинным
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    relevant_paragraphs = []
    for p in paragraphs:
        # Исключаем короткие параграфы и те, которые содержат контактную информацию
        if len(p) > 50 and not any(keyword in p.lower() for keyword in [
            'тел.', 'телефон', 'адрес', 'режим работы', 'как добраться', 'контакты'
        ]):
            relevant_paragraphs.append(p)
    
    if not relevant_paragraphs:
        print(f"Не удалось выделить релевантные параграфы для {attraction_name}")
        return None
    
    # Составляем описание из первых релевантных параграфов
    description = ' '.join(relevant_paragraphs[:3])
    if len(description) > 1000:
        description = description[:997] + '...'
    
    return description

def get_better_image_url(attraction_name):
    """
    Поиск лучшего изображения достопримечательности
    """
    query = f"{attraction_name} Челябинск фото"
    encoded_query = quote(query)
    
    # Предопределенные URL изображений для ключевых достопримечательностей
    predefined_images = {
        "Кировка": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Kirovka_Chelyabinsk.jpg/1200px-Kirovka_Chelyabinsk.jpg",
        "Театр оперы и балета": "https://cheldreateatr.ru/upload/000/u14/001/25a38c2b.jpg",
        "Государственный исторический музей": "https://avatars.mds.yandex.net/get-altay/6514916/2a00000184c6bacd3dd3d7ebc6e1f60a8d2b/XXL_height",
        "Челябинский зоопарк": "https://chelzoo.ru/images/uploads/afishi/2017/18082017/DSC_0243-min.JPG",
        "Парк имени Гагарина": "https://www.tourprom.ru/site_media/images/upload/articles/2019/12/Изображение-30.png",
        "Памятник Курчатову": "https://photos.wikimapia.org/p/00/06/13/80/41_big.jpg",
        "Краеведческий музей": "https://avatars.mds.yandex.net/get-altay/5091492/2a00000181d30dd2b83c9c23133b9dec1c1c/XXXL",
        "Площадь Революции": "https://photocentra.ru/i/2018/06/21/3_photocentra_ru_19352037.jpg"
    }
    
    # Проверяем, есть ли предопределенное изображение
    for key, url in predefined_images.items():
        if key.lower() in attraction_name.lower():
            return url
    
    # Если нет предопределенного, возвращаем хотя бы какое-то изображение
    default_images = {
        "Музей": "https://avatars.mds.yandex.net/get-altay/5091492/2a00000181d30dd2b83c9c23133b9dec1c1c/XXXL",
        "Театр": "https://cheldreateatr.ru/upload/000/u14/001/25a38c2b.jpg",
        "Парк": "https://www.tourprom.ru/site_media/images/upload/articles/2019/12/Изображение-30.png",
        "Памятник": "https://photos.wikimapia.org/p/00/06/13/80/41_big.jpg",
        "Храм": "https://aif-s3.aif.ru/images/019/507/41fc7d95e78ae3d6c5457420d9ddcc4c.jpg",
        "Церковь": "https://aif-s3.aif.ru/images/019/507/41fc7d95e78ae3d6c5457420d9ddcc4c.jpg",
        "Площадь": "https://photocentra.ru/i/2018/06/21/3_photocentra_ru_19352037.jpg",
        "Музыка": "https://i.ytimg.com/vi/mYdOWuqpLG4/maxresdefault.jpg"
    }
    
    for category, url in default_images.items():
        if category.lower() in attraction_name.lower():
            return url
    
    # Если не нашли подходящего изображения, возвращаем универсальное изображение Челябинска
    return "https://www.tourprom.ru/site_media/images/upload/articles/2019/09/chelyabinsk.jpg"

def update_attraction_info(name, current_description):
    """
    Обновляет информацию о достопримечательности: описание и изображение
    """
    better_description = get_attraction_description(name)
    better_image_url = get_better_image_url(name)
    
    result = {
        "name": name,
        "description": better_description if better_description else current_description,
        "image_url": better_image_url
    }
    
    return result

if __name__ == "__main__":
    # Список достопримечательностей для обновления
    attractions = [
        {"name": "Государственный исторический музей Южного Урала", "description": "Один из крупнейших музеев Урала с богатой коллекцией исторических артефактов."},
        {"name": "Театр оперы и балета им. М.И. Глинки", "description": "Знаменитый оперный театр, одна из архитектурных жемчужин Челябинска."},
        {"name": "Краеведческий музей", "description": "Один из старейших музеев на Урале, основанный в 1923 году."},
        {"name": "Парк имени Гагарина", "description": "Крупнейший парк Челябинска с развлечениями для всей семьи."},
        {"name": "Кировка (Челябинский Арбат)", "description": "Пешеходная улица в центре города с множеством скульптур, магазинов и кафе."},
        {"name": "Музей изобразительных искусств", "description": "Музей с богатой коллекцией произведений искусства российских и зарубежных мастеров."},
        {"name": "Памятник добровольцам-танкистам", "description": "Мемориал, посвященный добровольцам-танкистам Челябинского корпуса времён Великой Отечественной войны."},
        {"name": "Челябинская филармония", "description": "Центр музыкальной культуры города, место проведения концертов классической музыки."},
        {"name": "Парк «Алое поле»", "description": "Исторический парк с памятниками архитектуры и красивыми аллеями для прогулок."}
    ]
    
    # Обновляем информацию по каждой достопримечательности
    updated_attractions = []
    for attraction in attractions:
        print(f"\nОбновление информации о {attraction['name']}")
        updated_info = update_attraction_info(attraction["name"], attraction["description"])
        updated_attractions.append(updated_info)
        # Делаем паузу, чтобы не перегружать серверы запросами
        time.sleep(2)
    
    # Сохраняем результаты в JSON-файл
    with open('updated_attractions.json', 'w', encoding='utf-8') as f:
        json.dump(updated_attractions, f, ensure_ascii=False, indent=4)
    
    print(f"\nОбновленная информация сохранена в файл updated_attractions.json")