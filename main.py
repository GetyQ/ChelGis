from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.chip import MDChip
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import Snackbar
from kivy.uix.scrollview import ScrollView
from kivy.garden.mapview import MapView, MapMarker
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
import sqlite3
import os
from models import toggle_favorite, is_favorite, get_favorites, cache_data, get_cached_data

class CategoryChip(MDBoxLayout):
    text = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = None
        self.width = dp(100)
    
    def on_select(self, instance, value):
        app = MDApp.get_running_app()
        screen = app.root.get_screen('main')
        screen.filter_attractions()

class AttractionCard(MDCard):
    def __init__(self, id, name, description, category, lat, lng, on_press, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.lat = lat
        self.lng = lng
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = dp(16)
        self.spacing = dp(8)
        self.elevation = 1
        self.radius = [dp(10)]
        self.ripple_behavior = True

        # Название
        name_label = MDLabel(
            text=name,
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        
        # Категория
        category_label = MDLabel(
            text=category,
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20)
        )
        
        # Описание
        desc_label = MDLabel(
            text=description[:150] + "..." if len(description) > 150 else description,
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(100)
        )
        
        # Кнопки действий
        buttons_layout = MDBoxLayout(
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40)
        )
        
        map_button = MDIconButton(
            icon="map-marker",
            on_press=lambda x: on_press(lat, lng)
        )
        
        share_button = MDIconButton(
            icon="share-variant",
            on_press=lambda x: self.share_location(name, lat, lng)
        )
        
        # Кнопка избранного
        self.favorite_button = MDIconButton(
            icon="heart-outline",
            on_press=self.toggle_favorite
        )
        self.update_favorite_icon()
        
        buttons_layout.add_widget(map_button)
        buttons_layout.add_widget(share_button)
        buttons_layout.add_widget(self.favorite_button)
        
        # Добавляем все элементы
        self.add_widget(name_label)
        self.add_widget(category_label)
        self.add_widget(desc_label)
        self.add_widget(buttons_layout)
    
    def update_favorite_icon(self):
        """Обновить иконку избранного"""
        is_fav = is_favorite(self.id)
        self.favorite_button.icon = "heart" if is_fav else "heart-outline"
    
    def toggle_favorite(self, instance):
        """Добавить/удалить из избранного"""
        is_fav = toggle_favorite(self.id)
        self.favorite_button.icon = "heart" if is_fav else "heart-outline"
        
        # Показываем уведомление
        text = "Добавлено в избранное" if is_fav else "Удалено из избранного"
        Snackbar(text=text).open()
    
    def share_location(self, name, lat, lng):
        """Поделиться местоположением"""
        from kivy.utils import platform
        if platform == 'android':
            from android.content import Intent
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')
            
            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.setType('text/plain')
            
            text = f"Посетите {name} в Челябинске!\nКоординаты: {lat}, {lng}\nhttps://maps.google.com/?q={lat},{lng}"
            intent.putExtra(Intent.EXTRA_TEXT, String(text))
            
            currentActivity = PythonActivity.mActivity
            currentActivity.startActivity(intent)

class AttractionListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        # Основной layout
        self.layout = MDBoxLayout(orientation='vertical')
        
        # Спиннер загрузки
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': .5, 'center_y': .5},
            active=False
        )
        
        # Верхняя панель
        self.toolbar = MDTopAppBar(
            title="ЧелГис",
            elevation=4,
            right_action_items=[
                ["heart", lambda x: self.show_favorites()],
                ["refresh", lambda x: self.load_attractions()],
                ["map", lambda x: self.toggle_map()]
            ]
        )
        self.layout.add_widget(self.toolbar)
        
        # Добавляем поисковую строку
        self.search_bar = SearchBar()
        self.layout.add_widget(self.search_bar)
        
        # Контейнер для карты и списка
        self.content = MDBoxLayout(orientation='vertical')
        
        # Карта
        self.map = MapView(
            zoom=12,
            lat=55.159388,  # Центр Челябинска
            lon=61.402429,
            size_hint_y=0.4
        )
        self.content.add_widget(self.map)
        
        # Список достопримечательностей
        self.scroll = ScrollView()
        self.cards_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            padding=dp(16),
            adaptive_height=True
        )
        self.scroll.add_widget(self.cards_layout)
        self.content.add_widget(self.scroll)
        
        self.layout.add_widget(self.content)
        self.add_widget(self.layout)
        
        # Загружаем категории и данные
        self.load_categories()
        self.load_attractions()
        
        # Флаг видимости карты
        self.map_visible = True
        
        # Сохраняем все достопримечательности
        self.all_attractions = []

    def show_loading(self, show=True):
        """Показать/скрыть индикатор загрузки"""
        if show:
            if not self.spinner.parent:
                self.add_widget(self.spinner)
            self.spinner.active = True
        else:
            if self.spinner.parent:
                self.remove_widget(self.spinner)
            self.spinner.active = False
    
    def load_categories(self):
        """Загрузка категорий из базы данных"""
        self.show_loading()
        Clock.schedule_once(lambda dt: self._load_categories(), 0)
    
    def _load_categories(self):
        """Асинхронная загрузка категорий"""
        try:
            categories_box = self.search_bar.ids.categories_box
            
            db_path = os.path.join(os.path.dirname(__file__), 'chelgis.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT category FROM attraction ORDER BY category")
            categories = cursor.fetchall()
            
            for category in categories:
                chip = CategoryChip(text=category[0])
                categories_box.add_widget(chip)
            
            conn.close()
        finally:
            self.show_loading(False)
    
    def filter_attractions(self, search_text=""):
        """Фильтрация достопримечательностей по поиску и категориям"""
        # Получаем выбранные категории
        categories_box = self.search_bar.ids.categories_box
        selected_categories = [
            chip.text for chip in categories_box.children 
            if isinstance(chip, CategoryChip) and chip.children[0].active
        ]
        
        # Очищаем текущий список
        self.cards_layout.clear_widgets()
        self.map.remove_all_markers()
        
        # Фильтруем достопримечательности
        for attraction in self.all_attractions:
            name, description, category, lat, lng = attraction
            
            # Проверяем соответствие поиску и категориям
            matches_search = (
                search_text.lower() in name.lower() or 
                search_text.lower() in description.lower()
            )
            matches_category = (
                not selected_categories or 
                category in selected_categories
            )
            
            if matches_search and matches_category:
                # Добавляем маркер на карту
                marker = MapMarker(lat=lat, lon=lng)
                self.map.add_marker(marker)
                
                # Создаем карточку
                card = AttractionCard(
                    id=attraction[0],
                    name=attraction[1],
                    description=attraction[2],
                    category=attraction[3],
                    lat=attraction[4],
                    lng=attraction[5],
                    on_press=self.center_map
                )
                self.cards_layout.add_widget(card)

    def load_attractions(self):
        """Загрузка достопримечательностей из базы данных"""
        self.show_loading()
        Clock.schedule_once(lambda dt: self._load_attractions(), 0)
    
    def _load_attractions(self):
        """Асинхронная загрузка достопримечательностей"""
        try:
            # Пробуем загрузить из кэша
            cached_data = get_cached_data('attractions')
            if cached_data:
                self.all_attractions = cached_data
            else:
                # Загружаем из базы данных
                db_path = os.path.join(os.path.dirname(__file__), 'chelgis.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, description, category, lat, lng 
                    FROM attraction
                """)
                
                self.all_attractions = cursor.fetchall()
                conn.close()
                
                # Кэшируем данные
                cache_data('attractions', self.all_attractions)
            
            # Применяем текущие фильтры
            search_text = self.search_bar.ids.search_field.text
            self.filter_attractions(search_text)
        finally:
            self.show_loading(False)

    def toggle_map(self):
        """Переключение видимости карты"""
        if self.map_visible:
            self.map.size_hint_y = 0
            self.map.height = 0
        else:
            self.map.size_hint_y = 0.4
        self.map_visible = not self.map_visible

    def center_map(self, lat, lon):
        """Центрирует карту на выбранной достопримечательности"""
        self.map.center_on(lat, lon)
        self.map.zoom = 15
        # Убеждаемся, что карта видима
        if not self.map_visible:
            self.toggle_map()

    def show_favorites(self):
        """Показать избранные достопримечательности"""
        self.cards_layout.clear_widgets()
        self.map.remove_all_markers()
        
        favorites = get_favorites()
        
        for id, name, description, category, lat, lng in favorites:
            # Добавляем маркер на карту
            marker = MapMarker(lat=lat, lon=lng)
            self.map.add_marker(marker)
            
            # Создаем карточку
            card = AttractionCard(
                id=id,
                name=name,
                description=description,
                category=category,
                lat=lat,
                lng=lng,
                on_press=self.center_map
            )
            self.cards_layout.add_widget(card)

class ChelgisApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return AttractionListScreen()

if __name__ == '__main__':
    ChelgisApp().run()
