// Менеджер маршрутов
const RouteManager = {
    // Точки маршрута
    routePoints: [],
    
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
        
        this.routePoints.forEach((point, index) => {
            const item = document.createElement('div');
            item.className = 'route-point mb-2 p-2 d-flex justify-content-between align-items-center';
            item.innerHTML = `
                <div>
                    <span class="badge bg-primary me-2">${index + 1}</span>
                    ${point.name}
                </div>
                <div>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="RouteManager.removeFromRoute(${point.id})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            routeList.appendChild(item);
        });
        
        // Обновляем кнопки управления маршрутом
        document.getElementById('route-point-count').textContent = this.routePoints.length;
        document.getElementById('clear-route-btn').disabled = this.routePoints.length === 0;
        document.getElementById('optimize-route-btn').disabled = this.routePoints.length < 3;
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
        this.updateRouteDisplay();
        ChelMap.clearRoute();
        document.getElementById('route-panel').style.display = 'none';
    }
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
});
