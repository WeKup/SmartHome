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
    house_objects = db.relationship('ConnectedObject', backref='object_house', lazy=True, cascade="all, delete-orphan")
    house_reports = db.relationship('Rapport', backref='report_house', lazy=True, cascade="all, delete-orphan")
    
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
    nbR=db.Column(db.Integer, default=0)
    nbAU=db.Column(db.Integer, default=0)
    nbDU=db.Column(db.Integer, default=0)
    nbA=db.Column(db.Integer, default=0)
    nbAROOM=db.Column(db.Integer, default=0)
    nbAType=db.Column(db.Integer, default=0)
    nbD=db.Column(db.Integer, default=0)
    nbM=db.Column(db.Integer, default=0)
    nbMO=db.Column(db.Integer, default=0)

    
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
        levels = {
            'débutant': 0,
            'intermédiaire': 3,
            'avancé': 5,
            'expert': 7
        }
        current_level = self.level
        if current_level == 'expert':
            return 100
        
        if current_level == 'débutant':
            next_level = 'intermédiaire'
        elif current_level == 'intermédiaire':
            next_level = 'avancé'
        elif current_level == 'avancé':
            next_level = 'expert'
        
        current_points = self.points
        points_needed_for_next_level = levels[next_level]
        points_needed_for_current_level = levels[current_level]
        
        total_points_needed = points_needed_for_next_level - points_needed_for_current_level
        points_earned = current_points - points_needed_for_current_level
    
        if total_points_needed == 0:
            return 100
        percentage = (points_earned / total_points_needed) * 100
        return min(max(0, percentage), 100)

    def update_user_points(user, action_type):
        levels = {
            'débutant': 0,
            'intermédiaire': 3,
            'avancé': 5,
            'expert': 7
        }
        if action_type == 'connection':
            user.connection_count += 1
            user.points += 0.25
        elif action_type == 'view':
            user.action_count += 1
            user.points += 0.50
        elif action_type == 'search':
            user.action_count += 1
            user.points += 0.50
        
        if user.level == 'débutant' and user.points >= levels['intermédiaire']:
            user.level = 'intermédiaire'
        elif user.level == 'intermédiaire' and user.points >= levels['avancé']:
            user.level = 'avancé'
        elif user.level == 'avancé' and user.points >= levels['expert']:
            user.level = 'expert'
        
        db.session.commit()
    
    def nb(user,typeA):
        if typeA == 'nbR':
            user.nbR = (user.nbR or 0) + 1
        elif typeA == 'nbA':
            user.nbA = (user.nbA or 0) + 1
        elif typeA == 'nbAU':
            user.nbAU = (user.nbAU or 0) + 1
        elif typeA == 'nbD':
            user.nbD = (user.nbD or 0) + 1
        elif typeA == 'nbDU':
            user.nbDU = (user.nbDU or 0) + 1
        elif typeA == 'nbAROOM':
            user.nbAROOM = (user.nbAROOM or 0) + 1
        elif typeA == 'nbAType':
            user.nbAType = (user.nbAType or 0) + 1
        elif typeA == 'nbM':
            user.nbM = (user.nbM or 0) + 1

        db.session.commit()
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
    #je veux plutot connected_objects_in_room = db.relationship('ConnectedObject', back_populates='room', lazy=True)

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
    conso_min = db.Column(db.Integer, nullable=False, default=0)
    conso_max = db.Column(db.Integer, nullable=False, default=100)
    conso_actuelle = db.Column(db.Integer, nullable=True)
    model = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='active')
    connection_status = db.Column(db.String(20), default='connected')
    data = db.Column(db.JSON, nullable=True)
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    actions = db.relationship('ObjectAction', backref='object', lazy=True, cascade="all, delete-orphan")
    object_type = db.relationship('ObjectType', backref='connected_objects', lazy=True)
    room = db.relationship('Room', back_populates='connected_objects_in_room', lazy=True)

class ObjectType(db.Model):
    """Modèle pour les types d'objets"""
    __tablename__ = 'object_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=True)
    
    # Relations
    objects = db.relationship('ConnectedObject', backref='type', lazy=True)
    house = db.relationship('House', backref='object_types', lazy=True)

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

class ObjetHistorique(db.Model):
    __tablename__ = 'objet_historique'

    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey('connected_objects.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    action = db.Column(db.String(400), nullable=False)  # "Modification", "Activation", "Désactivation"
    status = db.Column(db.String(250), nullable=True)  # "active" ou "inactive"
    details = db.Column(db.Text, nullable=True)  # Description des changements


class ObjectParametres(db.Model):
    """Modèle pour les paramètres des objets"""
    __tablename__ = 'parametres'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    object_id = db.Column(db.Integer, db.ForeignKey('connected_objects.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    parametre = db.Column(db.String(200), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    unite = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rapport(db.Model):
    """Modèle pour les rapports"""
    __tablename__ = 'rapports'
    
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey('connected_objects.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_maj = db.Column(db.DateTime, onupdate=datetime.utcnow)

    connected_object = db.relationship('ConnectedObject', backref='rapports', lazy=True)

    

class Association(db.Model):
    """Table d'association entre objets et pièces"""
    __tablename__ = 'object_room_associations'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete="CASCADE"), nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey('connected_objects.id', ondelete="CASCADE"), nullable=False)

    object = db.relationship('ConnectedObject', backref='associations', lazy=True)
    room = db.relationship('Room', backref='associations', lazy=True)

class DefaultObjectParametre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, nullable=False)  # type_id de l'objet
    parametre = db.Column(db.String(100), nullable=False)
    default_value = db.Column(db.String(255), nullable=True)



