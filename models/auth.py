from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import random
import string
from datetime import datetime

db = SQLAlchemy()

class House(db.Model):
    """Modèle pour les maisons"""
    __tablename__ = 'houses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_demo = db.Column(db.Boolean, default=False)
    # Code unique pour rejoindre la maison
    house_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    users = db.relationship('User', backref='house', lazy=True)
    rooms = db.relationship('Room', backref='house', lazy=True)
    
    @staticmethod
    def generate_unique_code():
        """Génère un code unique pour la maison"""
        while True:
            # Générer un code de 6 caractères alphanumériques
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            # Vérifier si le code existe déjà
            existing = House.query.filter_by(house_code=code).first()
            if not existing:
                return code

class User(db.Model, UserMixin):
    """Modèle pour les utilisateurs"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Informations de profil
    gender = db.Column(db.String(10), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    member_type = db.Column(db.String(20), nullable=True)  # père, mère, enfant, etc.
    profile_photo = db.Column(db.String(255), nullable=True)
    
    # Niveau et points
    level = db.Column(db.String(20), default='débutant')  # débutant, intermédiaire, avancé, expert
    points = db.Column(db.Float, default=0)
    connection_count = db.Column(db.Integer, default=0)
    action_count = db.Column(db.Integer, default=0)
    
    # Relation avec la maison
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)  # Admin de la maison?
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    
    def set_password(self, password):
        """Définit le mot de passe haché"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def get_level_percent(self):
        """Calcule le pourcentage vers le niveau suivant"""
        levels = {
            'débutant': {'min': 0, 'max': 10},
            'intermédiaire': {'min': 10, 'max': 25},
            'avancé': {'min': 25, 'max': 50},
            'expert': {'min': 50, 'max': float('inf')}
        }
        
        current_level = levels.get(self.level)
        if not current_level:
            return 100  # Par défaut, 100% si niveau non trouvé
        
        if self.level == 'expert':
            return 100  # Expert est le niveau max
        
        next_level_key = next((k for k, v in levels.items() if v['min'] > current_level['min']), None)
        if not next_level_key:
            return 100  # Pas de niveau suivant
        
        next_level = levels[next_level_key]
        
        # Calculer le pourcentage
        total_points_needed = next_level['min'] - current_level['min']
        points_earned = self.points - current_level['min']
        
        percent = min(100, (points_earned / total_points_needed) * 100)
        return round(percent, 2)

class Room(db.Model):
    """Modèle pour les pièces"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    floor = db.Column(db.Integer, default=0)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    objects = db.relationship('ConnectedObject', backref='room', lazy=True)

class ConnectedObject(db.Model):
    """Modèle pour les objets connectés"""
    __tablename__ = 'connected_objects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    object_type_id = db.Column(db.Integer, db.ForeignKey('object_types.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    brand = db.Column(db.String(50), nullable=True)
    model = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='active')
    connection_status = db.Column(db.String(20), default='connected')
    data = db.Column(db.JSON, nullable=True)
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    actions = db.relationship('ObjectAction', backref='object', lazy=True)

class ObjectType(db.Model):
    """Modèle pour les types d'objets"""
    __tablename__ = 'object_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    objects = db.relationship('ConnectedObject', backref='type', lazy=True)

class ObjectAction(db.Model):
    """Modèle pour les actions sur les objets"""
    __tablename__ = 'object_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey('connected_objects.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref='actions', lazy=True)