// Менеджер маршрутов
const RouteManager = {
    // Точки маршрута
    routePoints: [],
    
    // Текущее название маршрута
    currentRouteName: null,
    
    // Добавление достопримечательности в маршрут
    addToRoute: function(id, name) {
        // Проверяем, есть ли уже эта достопримечательность в маршруте
        if (this.routePoints.find(p => p.id === id)) {
            alert('Эта достопримечательность уже добавлена в маршрут');
            return;
        }
        
        // Получаем информацию о достопримечательности
        fetch(`/api/attraction/${id}`)
            .then(response => response.json())
            .then(attraction => {
                // Добавляем точку в маршрут
                this.routePoints.push({
                    id: attraction.id,
                    name: attraction.name,
                    lat: attraction.lat,
                    lng: attraction.lng
                });
                
                // Обновляем отображение маршрута
                this.updateRouteDisplay();
                
                // Если есть хотя бы две точки, строим маршрут
                if (this.routePoints.length >= 2) {
                    this.buildRoute();
                }
                
                // Показываем панель маршрута
                document.getElementById('route-panel').style.display = 'block';
            })
            .catch(error => {
                console.error('Ошибка при добавлении точки в маршрут:', error);
            });
    },
    
    // Удаление точки из маршрута
    removeFromRoute: function(id) {
        this.routePoints = this.routePoints.filter(p => p.id !== id);
        
        // Обновляем отображение маршрута
        this.updateRouteDisplay();
        
        // Если осталось хотя бы две точки, перестраиваем маршрут
        if (this.routePoints.length >= 2) {
            this.buildRoute();
        } else {
            // Если точек меньше двух, очищаем маршрут
            ChelMap.clearRoute();
            
            // Если точек нет, скрываем панель маршрута
            if (this.routePoints.length === 0) {
                document.getElementById('route-panel').style.display = 'none';
            }
        }
    },
    
    // Обновление отображения точек маршрута в панели
    updateRouteDisplay: function() {
        const routeList = document.getElementById('route-points-list');
        routeList.innerHTML = '';
        
        // Обновляем название маршрута, если загружен предопределенный маршрут
        if (this.currentRouteName) {
            document.getElementById('route-name').textContent = this.currentRouteName;
        } else {
            document.getElementById('route-name').textContent = 'Ваш маршрут';
        }
        
        this.routePoints.forEach((point, index) => {
            // Получаем категорию из точки или устанавливаем по умолчанию
            const category = point.category || 'Место';
            
            const item = document.createElement('div');
            item.className = 'route-point d-flex justify-content-between align-items-center';
            item.setAttribute('data-point-id', point.id);
            item.innerHTML = `
                <div>
                    <span class="badge bg-primary me-2">${index + 1}</span>
                    <span class="route-point-title">${point.name}</span>
                    <span class="route-point-category">${category}</span>
                </div>
                <div>
                    <button class="btn btn-sm btn-outline-light" 
                            onclick="ChelMap.zoomToAttraction(${point.lat}, ${point.lng})" 
                            title="Показать на карте">
                        <i class="fas fa-map-marker-alt"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="RouteManager.removeFromRoute(${point.id})" 
                            title="Удалить из маршрута">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            // Добавляем обработчики для drag-and-drop (можно реализовать позже)
            item.draggable = true;
            
            routeList.appendChild(item);
        });
        
        // Обновляем кнопки управления маршрутом и счетчики
        document.getElementById('route-point-count').textContent = this.routePoints.length;
        document.getElementById('clear-route-btn').disabled = this.routePoints.length === 0;
        document.getElementById('optimize-route-btn').disabled = this.routePoints.length < 3;
        
        // Показываем/скрываем инструкцию в зависимости от количества точек
        const instructionEl = document.getElementById('route-instruction');
        if (this.routePoints.length < 3) {
            instructionEl.style.display = 'none';
        } else {
            instructionEl.style.display = 'block';
        }
    },
    
    // Построение маршрута между точками
    buildRoute: function() {
        // Отображаем маршрут на карте
        ChelMap.displayRoute(this.routePoints);
        
        // Вычисляем примерное расстояние маршрута
        const distance = this.calculateRouteDistance();
        document.getElementById('route-distance').textContent = distance.toFixed(1);
    },
    
    // Вычисление примерного расстояния маршрута (в км)
    calculateRouteDistance: function() {
        let totalDistance = 0;
        
        for (let i = 0; i < this.routePoints.length - 1; i++) {
            const point1 = this.routePoints[i];
            const point2 = this.routePoints[i + 1];
            
            // Расстояние между двумя точками (формула гаверсинуса)
            const R = 6371; // радиус Земли в км
            const dLat = this.toRad(point2.lat - point1.lat);
            const dLon = this.toRad(point2.lng - point1.lng);
            
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                    Math.cos(this.toRad(point1.lat)) * Math.cos(this.toRad(point2.lat)) * 
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            const distance = R * c;
            
            totalDistance += distance;
        }
        
        return totalDistance;
    },
    
    // Перевод градусов в радианы
    toRad: function(value) {
        return value * Math.PI / 180;
    },
    
    // Оптимизация маршрута (приближенное решение задачи коммивояжера)
    optimizeRoute: function() {
        if (this.routePoints.length < 3) {
            return; // Нет смысла оптимизировать маршрут из менее чем 3 точек
        }
        
        // Сохраняем первую и последнюю точки
        const start = this.routePoints[0];
        
        // Остальные точки оптимизируем
        const pointsToOptimize = this.routePoints.slice(1);
        
        // Простой жадный алгоритм
        const optimized = [start];
        let currentPoint = start;
        
        while (pointsToOptimize.length > 0) {
            // Находим ближайшую точку к текущей
            let minDistance = Infinity;
            let minIndex = -1;
            
            for (let i = 0; i < pointsToOptimize.length; i++) {
                const point = pointsToOptimize[i];
                
                // Расстояние между текущей точкой и рассматриваемой
                const R = 6371; // радиус Земли в км
                const dLat = this.toRad(point.lat - currentPoint.lat);
                const dLon = this.toRad(point.lng - currentPoint.lng);
                
                const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                        Math.cos(this.toRad(currentPoint.lat)) * Math.cos(this.toRad(point.lat)) * 
                        Math.sin(dLon/2) * Math.sin(dLon/2);
                
                const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                const distance = R * c;
                
                if (distance < minDistance) {
                    minDistance = distance;
                    minIndex = i;
                }
            }
            
            // Добавляем ближайшую точку в оптимизированный маршрут
            const nextPoint = pointsToOptimize.splice(minIndex, 1)[0];
            optimized.push(nextPoint);
            currentPoint = nextPoint;
        }
        
        // Обновляем маршрут
        this.routePoints = optimized;
        this.updateRouteDisplay();
        this.buildRoute();
    },
    
    // Очистка маршрута
    clearRoute: function() {
        this.routePoints = [];
        this.currentRouteName = null; // Сбрасываем название маршрута
        this.updateRouteDisplay();
        ChelMap.clearRoute();
        document.getElementById('route-panel').style.display = 'none';
    }
};

// Загрузка предлагаемых маршрутов
RouteManager.loadPredefinedRoutes = function() {
    fetch('/api/predefined-routes')
        .then(response => response.json())
        .then(routes => {
            this.displayPredefinedRoutes(routes);
        })
        .catch(error => {
            console.error('Ошибка при загрузке предлагаемых маршрутов:', error);
        });
};

// Отображение предлагаемых маршрутов
RouteManager.displayPredefinedRoutes = function(routes) {
    const container = document.getElementById('predefined-routes-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    routes.forEach((route, index) => {
        const card = document.createElement('div');
        card.className = 'card mb-2';
        card.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${route.name}</h5>
                <p class="card-text small">${route.description}</p>
                <p class="card-text text-muted small">${route.points.length} точек</p>
                <button class="btn btn-sm btn-outline-primary" 
                        onclick="RouteManager.loadPredefinedRoute(${index})">
                    <i class="fas fa-route"></i> Загрузить маршрут
                </button>
            </div>
        `;
        container.appendChild(card);
    });
};

// Загрузка предопределенного маршрута
RouteManager.loadPredefinedRoute = function(routeId) {
    // Показываем индикатор загрузки
    const loadingAlert = document.createElement('div');
    loadingAlert.className = 'alert alert-info fade show';
    loadingAlert.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Загрузка...</span>
            </div>
            <span>Загрузка маршрута...</span>
        </div>
    `;
    document.querySelector('.map-container').prepend(loadingAlert);
    
    fetch(`/api/predefined-route/${routeId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(routeData => {
            // Удаляем индикатор загрузки
            loadingAlert.remove();
            
            // Очищаем текущий маршрут
            this.clearRoute();
            
            // Сохраняем название маршрута
            this.currentRouteName = routeData.name;
            
            // Проверяем наличие точек в маршруте
            if (!routeData.points || routeData.points.length === 0) {
                throw new Error('Маршрут не содержит точек');
            }
            
            // Добавляем точки из предопределенного маршрута
            routeData.points.forEach(point => {
                this.routePoints.push({
                    id: point.id,
                    name: point.name,
                    lat: point.lat,
                    lng: point.lng,
                    category: point.category // Добавляем категорию из данных
                });
            });
            
            // Обновляем отображение маршрута
            this.updateRouteDisplay();
            
            // Отображаем маршрут на карте
            if (this.routePoints.length >= 2) {
                this.buildRoute();
            }
            
            // Показываем панель маршрута
            document.getElementById('route-panel').style.display = 'block';
            
            // Закрываем модальное окно, если оно открыто
            const modal = document.getElementById('predefined-routes-modal');
            if (modal) {
                try {
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.hide();
                } catch (e) {
                    // Если модальное окно уже инициализировано, попробуем получить его экземпляр
                    try {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) modalInstance.hide();
                    } catch (innerError) {
                        // Если не удалось, просто скрываем модальное окно стандартными методами
                        modal.classList.remove('show');
                        modal.style.display = 'none';
                        document.body.classList.remove('modal-open');
                        const backdrop = document.querySelector('.modal-backdrop');
                        if (backdrop) backdrop.remove();
                    }
                }
            }
            
            // Показываем сообщение об успешной загрузке
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show';
            alert.innerHTML = `
                <strong>Маршрут загружен!</strong> "${routeData.name}" добавлен на карту.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            document.querySelector('.map-container').prepend(alert);
            
            // Автоматически удаляем сообщение через 5 секунд
            setTimeout(() => {
                alert.remove();
            }, 5000);
            
            // Анимируем карту для показа всего маршрута
            if (this.routePoints.length > 0) {
                ChelMap.fitMapToRoutePoints(this.routePoints);
            }
        })
        .catch(error => {
            // Удаляем индикатор загрузки
            loadingAlert.remove();
            
            console.error('Ошибка при загрузке маршрута:', error);
            
            // Показываем сообщение об ошибке
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger alert-dismissible fade show';
            alert.innerHTML = `
                <strong>Ошибка!</strong> Не удалось загрузить маршрут. Пожалуйста, попробуйте позже.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            document.querySelector('.map-container').prepend(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        });
};

// Инициализация обработчиков событий
document.addEventListener('DOMContentLoaded', function() {
    // Кнопка очистки маршрута
    document.getElementById('clear-route-btn').addEventListener('click', function() {
        RouteManager.clearRoute();
    });
    
    // Кнопка оптимизации маршрута
    document.getElementById('optimize-route-btn').addEventListener('click', function() {
        RouteManager.optimizeRoute();
    });
    
    // Загружаем предлагаемые маршруты
    RouteManager.loadPredefinedRoutes();
});
