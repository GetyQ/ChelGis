from app import db

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
