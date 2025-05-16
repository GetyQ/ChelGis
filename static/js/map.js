// Объект для работы с картой
const ChelMap = {
    // Объект карты
    map: null,
    
    // Группа маркеров достопримечательностей
    attractionsLayer: null,
    
    // Слой для маршрута
    routeLayer: null,
    
    // Центр Челябинска
    center: [55.160283, 61.400856],
    
    // Инициализация карты
    init: function() {
        // Создаем карту с центром в Челябинске
        this.map = L.map('map').setView(this.center, 13);
        
        // Добавляем слой OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);
        
        // Создаем группу для маркеров достопримечательностей
        this.attractionsLayer = L.layerGroup().addTo(this.map);
        
        // Создаем слой для маршрута
        this.routeLayer = L.layerGroup().addTo(this.map);
        
        // Загружаем достопримечательности
        this.loadAttractions();
        
        // Обработчик изменения размера экрана
        window.addEventListener('resize', function() {
            ChelMap.map.invalidateSize();
        });
    },
    
    // Загрузка достопримечательностей с сервера
    loadAttractions: function() {
        fetch('/api/attractions')
            .then(response => response.json())
            .then(data => {
                this.displayAttractions(data);
            })
            .catch(error => {
                console.error('Ошибка при загрузке достопримечательностей:', error);
                document.getElementById('error-message').textContent = 'Ошибка загрузки данных. Пожалуйста, попробуйте позже.';
                document.getElementById('error-container').style.display = 'block';
            });
    },
    
    // Отображение достопримечательностей на карте
    displayAttractions: function(attractions) {
        // Очищаем слой с достопримечательностями
        this.attractionsLayer.clearLayers();
        
        // Добавляем каждую достопримечательность на карту
        attractions.forEach(attraction => {
            const marker = L.marker([attraction.lat, attraction.lng], {
                title: attraction.name,
                id: attraction.id
            });
            
            // Создаем всплывающее окно с информацией
            const popupContent = `
                <div class="attraction-popup">
                    <h5>${attraction.name}</h5>
                    <p class="text-muted">${attraction.category}</p>
                    <p>${attraction.address}</p>
                    <button class="btn btn-sm btn-outline-info" onclick="showAttractionDetails(${attraction.id})">
                        Подробнее
                    </button>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            marker.on('click', function() {
                ChelMap.map.setView([attraction.lat, attraction.lng], 15);
            });
            
            // Добавляем маркер в слой
            marker.addTo(this.attractionsLayer);
        });
        
        // Обновляем список достопримечательностей
        this.updateAttractionsList(attractions);
    },
    
    // Обновление списка достопримечательностей в боковой панели
    updateAttractionsList: function(attractions) {
        const listContainer = document.getElementById('attractions-list');
        listContainer.innerHTML = '';
        
        attractions.forEach(attraction => {
            const item = document.createElement('div');
            item.className = 'attraction-item mb-2 p-2 border-bottom';
            item.innerHTML = `
                <h5>${attraction.name}</h5>
                <p class="text-muted small">${attraction.category}</p>
                <div class="d-flex justify-content-between">
                    <button class="btn btn-sm btn-outline-info" 
                            onclick="showAttractionDetails(${attraction.id})">
                        Подробнее
                    </button>
                    <button class="btn btn-sm btn-outline-primary"
                            onclick="ChelMap.zoomToAttraction(${attraction.lat}, ${attraction.lng})">
                        <i class="fas fa-map-marker-alt"></i>
                    </button>
                </div>
            `;
            listContainer.appendChild(item);
        });
    },
    
    // Приближение к конкретной достопримечательности
    zoomToAttraction: function(lat, lng) {
        this.map.setView([lat, lng], 16);
        
        // Находим и открываем всплывающее окно маркера
        this.attractionsLayer.eachLayer(function(layer) {
            if (layer.getLatLng().lat === lat && layer.getLatLng().lng === lng) {
                layer.openPopup();
            }
        });
    },
    
    // Показать подробную информацию о достопримечательности
    showAttractionDetails: function(id) {
        fetch(`/api/attraction/${id}`)
            .then(response => response.json())
            .then(attraction => {
                const detailsContainer = document.getElementById('attraction-details');
                
                detailsContainer.innerHTML = `
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">${attraction.name}</h5>
                            <button type="button" class="btn-close" 
                                    onclick="document.getElementById('attraction-details').style.display='none'"></button>
                        </div>
                        <div class="card-body">
                            <p class="text-muted">${attraction.category}</p>
                            <p><strong>Адрес:</strong> ${attraction.address}</p>
                            <p>${attraction.description}</p>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-primary" 
                                        onclick="ChelMap.zoomToAttraction(${attraction.lat}, ${attraction.lng})">
                                    Показать на карте
                                </button>
                                <button class="btn btn-success" 
                                        onclick="RouteManager.addToRoute(${attraction.id}, '${attraction.name}')">
                                    Добавить в маршрут
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                detailsContainer.style.display = 'block';
            })
            .catch(error => {
                console.error('Ошибка при загрузке информации о достопримечательности:', error);
            });
    },
    
    // Фильтрация достопримечательностей по категории
    filterByCategory: function(category) {
        fetch(`/api/attractions`)
            .then(response => response.json())
            .then(attractions => {
                let filtered;
                
                if (category === 'all') {
                    filtered = attractions;
                } else {
                    filtered = attractions.filter(a => a.category === category);
                }
                
                this.displayAttractions(filtered);
            })
            .catch(error => {
                console.error('Ошибка при фильтрации достопримечательностей:', error);
            });
    },
    
    // Поиск достопримечательностей
    searchAttractions: function(query) {
        if (!query || query.trim() === '') {
            this.loadAttractions();
            return;
        }
        
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(attractions => {
                this.displayAttractions(attractions);
                
                if (attractions.length === 0) {
                    document.getElementById('search-no-results').style.display = 'block';
                } else {
                    document.getElementById('search-no-results').style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Ошибка при поиске достопримечательностей:', error);
            });
    },
    
    // Отображение маршрута на карте
    displayRoute: function(routePoints) {
        this.routeLayer.clearLayers();
        
        if (routePoints.length < 2) {
            return;
        }
        
        // Создаем линию маршрута
        const routeLine = L.polyline(routePoints.map(p => [p.lat, p.lng]), {
            color: '#4285F4',
            weight: 5,
            opacity: 0.7
        }).addTo(this.routeLayer);
        
        // Настраиваем вид карты, чтобы был виден весь маршрут
        this.map.fitBounds(routeLine.getBounds(), {
            padding: [50, 50]
        });
    },
    
    // Очистка маршрута
    clearRoute: function() {
        this.routeLayer.clearLayers();
    },
    
    // Подгонка карты, чтобы показать все точки маршрута
    fitMapToRoutePoints: function(routePoints) {
        if (!routePoints || routePoints.length === 0) return;
        
        // Создаем границы
        const bounds = L.latLngBounds();
        
        // Добавляем каждую точку в границы
        routePoints.forEach(point => {
            bounds.extend([point.lat, point.lng]);
        });
        
        // Подгоняем карту с небольшим отступом
        this.map.flyToBounds(bounds, {
            padding: [50, 50],
            duration: 1
        });
    }
};

// Функция для отображения деталей достопримечательности
function showAttractionDetails(id) {
    ChelMap.showAttractionDetails(id);
}

// Инициализация карты при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    ChelMap.init();
    
    // Загрузка категорий для фильтра
    fetch('/api/categories')
        .then(response => response.json())
        .then(categories => {
            const filterSelect = document.getElementById('category-filter');
            
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                filterSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке категорий:', error);
        });
    
    // Обработчик изменения фильтра категорий
    document.getElementById('category-filter').addEventListener('change', function() {
        ChelMap.filterByCategory(this.value);
    });
    
    // Обработчик поиска
    document.getElementById('search-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        ChelMap.searchAttractions(searchInput.value);
    });
});
