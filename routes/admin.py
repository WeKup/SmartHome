from flask import *
from flask_login import login_required, current_user
from models.auth import *
from werkzeug.security import generate_password_hash
import random
from weasyprint import HTML
import string
from datetime import *
from sqlalchemy import func
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  
import numpy as np
import base64
from io import BytesIO
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def accueil():
    house = House.query.get(current_user.house_id)
    return render_template('admin/dashboard.html',house=house)


@admin_bp.route('/ChangerJoin')
@login_required
def changerJoin():
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits pour approuver des utilisateurs.", "danger")
        return redirect(url_for('admin.accueil'))
    house = House.query.get(current_user.house_id)
    if house.Join_method == 'mail':
        house.Join_method= 'Approbation'
    else:
        house.Join_method= 'mail'
    
    db.session.commit()
    flash(f"Le mode d'admission a été changé en : {house.Join_method}", "success")
    return redirect(url_for('admin.accueil'))

@admin_bp.route('/requete')
@login_required
def requete():
    listUser= User.query.filter_by(house_id=current_user.house_id, requete=1).all()
    return render_template('admin/appro.html', users=listUser)

@admin_bp.route('/approve-user/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        flash("Vous n'avez pas les droits pour approuver des utilisateurs.", "danger")
        return redirect(url_for('admin.requete'))

    user = User.query.get_or_404(user_id)

    user.requete = 0
    User.nb(current_user,'nbAU')
    db.session.commit()
    
    flash(f"L'utilisateur {user.username} a été approuvé avec succès.", "success")
    return redirect(url_for('admin.requete'))


@admin_bp.route('/users')
@login_required
def manage_users():
    house_id = current_user.house_id
    users = User.query.filter_by(house_id=current_user.house_id).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    User.nb(current_user,'nbAU')
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        nom = request.form['nom']
        prénom = request.form['prénom']
        password = request.form['password']
        gender = request.form['gender']
        birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
        member_type = request.form['member_type']
        is_admin = 'is_admin' in request.form
        
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Un utilisateur avec ce nom ou cet email existe déjà.', 'danger')
            return redirect(url_for('admin.add_user'))
        
        new_user = User(
            username=username,
            email=email,
            nom=nom,
            prénom=prénom,
            gender=gender,
            birthdate=birthdate,
            member_type=member_type,
            house_id=current_user.house_id,
            is_admin=is_admin,
            email_verified=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Utilisateur {username} ajouté avec succès!', 'success')
        return redirect(url_for('admin.manage_users'))
        
    return render_template('admin/add_user.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    User.nb(current_user,'nbM')
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.nom = request.form['nom']
        user.prénom = request.form['prénom']
        if request.form.get('password'):
            user.set_password(request.form['password'])
        user.gender = request.form['gender']
        user.birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
        user.member_type = request.form['member_type']
        if current_user.is_admin:
            user.is_admin = 'is_admin' in request.form
        else:
            user.is_admin= user.is_admin
        
        if 'level' in request.form and request.form['level'] != user.level:
            user.level = request.form['level']
        
        db.session.commit()
        flash(f'Utilisateur {user.username} mis à jour avec succès!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    User.nb(current_user,'nbDU')
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    
    username = user.username
    for action in user.actions:
        db.session.delete(action)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Utilisateur {username} supprimé avec succès!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/objects')
@login_required
def manage_objects():
    house_id = current_user.house_id
    objects = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()
    return render_template('admin/objects.html', objects=objects)

@admin_bp.route('/objects/add', methods=['GET', 'POST'])
@login_required
def add_object():
    User.nb(current_user,'nbA')
    house_id = current_user.house_id
    room_list = Room.query.filter_by(house_id=house_id).all()
    object_types = ObjectType.query.filter_by(house_id=house_id).all()
    
    
    if not room_list:
        flash('Vous devez d\'abord créer au moins une pièce avant d\'ajouter un objet.', 'warning')
        return redirect(url_for('admin.manage_rooms'))
    
    if not object_types:
        flash('Vous devez d\'abord créer au moins un type d\'objet avant d\'ajouter un objet.', 'warning')
        return redirect(url_for('admin.manage_object_types'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        object_type_id = request.form['object_type_id']
        room_id = request.form['room_id']
        brand = request.form['brand']
        model = request.form['model']
        conso_min = request.form['conso_min']
        if conso_min:
            conso_min = int(conso_min)
        else:
            conso_min = 0 
        conso_max = (request.form['conso_max'])
        if conso_max:
            conso_max = int(conso_max)
        else:
            conso_max = 0 
        conso_visé= (request.form['conso_visé'])
        if conso_visé:
            conso_visé = int(conso_visé)
        else:
            conso_visé = 0 
        temp_min = (request.form['temp_min'])
        if temp_min:
            temp_min = int(temp_min)
        else:
            temp_min = 0 
        temp_max = (request.form['temp_max'])
        if temp_max:
            temp_max = int(temp_max)
        else:
            temp_max = 0 
        temp_visé= (request.form['temp_visé'])
        if temp_visé:
            temp_visé = int(temp_visé)
        else:
            temp_visé = 0 
        eau_visé= (request.form['eau_visé'])
        if eau_visé:
            eau_visé = int(eau_visé)
        else:
            eau_visé = 0 
        eau_min = (request.form['eau_min'])
        if eau_min:
            eau_min = int(eau_min)
        else:
            eau_min = 0 
        eau_max = (request.form['eau_max'])
        if eau_max:
            eau_max = int(eau_max)
        else:
            eau_max = 0 
        gaz_visé= (request.form['gaz_visé'])
        if gaz_visé:
            gaz_visé = int(gaz_visé)
        else:
            gaz_visé = 0 
        gaz_min = (request.form['gaz_min'])
        if gaz_min:
            gaz_min = int(gaz_min)
        else:
            gaz_min = 0 
        gaz_max = (request.form['gaz_max'])
        if gaz_max:
            gaz_max = int(gaz_max)
        else:
            gaz_max = 0 
        autre_visé= (request.form['autre_visé'])
        if autre_visé:
            autre_visé = int(autre_visé)
        else:
            autre_visé = 0 
        autre_min = (request.form['autre_min'])
        if autre_min:
            autre_min = int(autre_min)
        else:
            autre_min = 0 
        autre_max = (request.form['autre_max'])
        if autre_max:
            autre_max = int(autre_max)
        else:
            autre_max = 0 

        conso_actuelle = random.randint(conso_min, conso_max)
        temp_actuelle = random.randint(temp_min, temp_max)
        eau_actuelle=random.randint(eau_min,eau_max)
        gaz_actuelle=random.randint(gaz_min,gaz_max)
        autre_actuelle=random.randint(autre_min,autre_max)
        batterie= random.randint(0,100)

        new_object = ConnectedObject(
            name=name,
            description=description,
            object_type_id=object_type_id,
            room_id=room_id,
            house_id=house_id,
            brand=brand,
            model=model,
            status='active',
            connection_status='connected',
            data={},
            conso_min=conso_min,
            conso_max=conso_max,
            conso_actuelle=conso_actuelle,
            conso_visé=conso_visé,
            temp_min=temp_min,
            temp_max=temp_max,
            temp_actuelle=temp_actuelle,
            temp_visé=temp_visé,
            batterie=batterie,
            eau_min=eau_min,
            eau_max=eau_max,
            eau_actuelle=eau_actuelle,
            eau_visé=eau_visé,
            gaz_min=gaz_min,
            gaz_max=gaz_max,
            gaz_actuelle=gaz_actuelle,
            gaz_visé=gaz_visé,
            autre_min=autre_min,
            autre_max=autre_max,
            autre_actuelle=autre_actuelle,
            autre_visé=autre_visé
        )
        
        db.session.add(new_object)
        db.session.commit()
        
        flash(f'Objet {name} ajouté avec succès!', 'success')
        return redirect(url_for('admin.manage_objects'))
    
    return render_template('admin/add_object.html', rooms=room_list, object_types=object_types)

@admin_bp.route('/objects/edit/<int:object_id>', methods=['GET', 'POST'])
@login_required
def edit_object(object_id):
    User.nb(current_user,'nbMO')
    obj = ConnectedObject.query.get_or_404(object_id)
    house_id = current_user.house_id
    room_list = Room.query.filter_by(house_id=house_id).all()
    object_types = ObjectType.query.filter_by(house_id=house_id).all()
    oldstatu=obj.status
    
    if request.method == 'POST':
        obj.name = request.form['name']
        obj.description = request.form['description']
        obj.object_type_id = request.form['object_type_id']
        obj.room_id = request.form['room_id']
        obj.brand = request.form['brand']
        obj.model = request.form['model']
        obj.status = request.form['status']
        obj.connection_status = request.form['connection_status']
        obj.conso_actuelle = (request.form['conso_actuelle'])
        if obj.conso_actuelle:
            obj.conso_actuelle = int(obj.conso_actuelle)
        else:
            obj.conso_actuelle = 0
        obj.conso_min = (request.form['conso_min'])
        if obj.conso_min:
            obj.conso_min = int(obj.conso_min)
        else:
            obj.conso_min = 0
        obj.conso_max = (request.form['conso_max'])
        if obj.conso_max:
            obj.conso_max = int(obj.conso_max)
        else:
            obj.conso_max = 0
        obj.conso_visé= (request.form['conso_visé'])
        if obj.conso_visé:
            obj.conso_visé = int(obj.conso_visé)
        else:
            obj.conso_visé = 0 
        obj.temp_actuelle = (request.form['temp_actuelle'])
        if obj.temp_actuelle:
            obj.temp_actuelle = int(obj.temp_actuelle)
        else:
            obj.temp_actuelle = 0 
        obj.temp_visé= (request.form['temp_visé'])
        if obj.temp_visé:
            obj.temp_visé = int(obj.temp_visé)
        else:
            obj.temp_visé = 0
        obj.temp_min= (request.form['temp_min'])
        if obj.temp_min:
            obj.temp_min = int(obj.temp_min)
        else:
            obj.temp_min = 0
        obj.temp_max= (request.form['temp_max'])
        if obj.temp_max:
            obj.temp_max = int(obj.temp_max)
        else:
            obj.temp_max = 0 
        obj.eau_visé= (request.form['eau_visé'])
        if obj.eau_visé:
            obj.eau_visé = int(obj.eau_visé)
        else:
            obj.eau_visé = 0  
        obj.eau_actuelle = (request.form['eau_actuelle'])
        if obj.eau_actuelle:
            obj.eau_actuelle = int(obj.eau_actuelle)
        else:
            obj.eau_actuelle = 0 
        obj.eau_min = (request.form['eau_min'])
        if obj.eau_min:
            obj.eau_min = int(obj.eau_min)
        else:
            obj.eau_min = 0
        obj.eau_max = (request.form['eau_max'])
        if obj.eau_max:
            obj.eau_max = int(obj.eau_max)
        else:
            obj.eau_max = 0 
        
        obj.gaz_visé= (request.form['gaz_visé'])
        if obj.gaz_visé:
            obj.gaz_visé = int(obj.gaz_visé)
        else:
            obj.gaz_visé = 0 
        obj.gaz_actuelle = (request.form['gaz_actuelle'])
        if obj.gaz_actuelle:
            obj.gaz_actuelle = int(obj.gaz_actuelle)
        else:
            obj.gaz_actuelle = 0 
        obj.gaz_min = (request.form['gaz_min'])
        if obj.gaz_min:
            obj.gaz_min = int(obj.gaz_min)
        else:
            obj.gaz_min = 0 
        obj.gaz_max = (request.form['gaz_max'])
        if obj.gaz_max:
            obj.gaz_max = int(obj.gaz_max)
        else:
            obj.gaz_max = 0 
        obj.autre_visé= (request.form['autre_visé'])
        if obj.autre_visé:
            obj.autre_visé = int(obj.autre_visé)
        else:
            obj.autre_visé = 0 
        obj.autre_actuelle = (request.form['autre_actuelle'])
        if obj.autre_actuelle:
            obj.autre_actuelle = int(obj.autre_actuelle)
        else:
            obj.autre_actuelle = 0
        obj.autre_min = (request.form['autre_min'])
        if obj.autre_min:
            obj.autre_min = int(obj.autre_min)
        else:
            obj.autre_min = 0
        obj.autre_max = (request.form['autre_max'])
        if obj.autre_max:
            obj.autre_max = int(obj.autre_max)
        else:
            obj.autre_max = 0 
        
        if oldstatu != obj.status:
            if obj.status == 'active':
                obj.conso_actuelle=random.randint(obj.conso_min,obj.conso_max)
                obj.eau_actuelle=random.randint(obj.eau_min,obj.eau_max)
                obj.gaz_actuelle=random.randint(obj.gaz_min,obj.gaz_max)
                obj.autre_actuelle=random.randint(obj.autre_min,obj.autre_max)
                obj.temp_actuelle=random.randint(obj.temp_min,obj.temp_max)
            elif obj.status == 'inactive':
                obj.conso_actuelle= 0
                obj.eau_actuelle= 0
                obj.gaz_actuelle= 0
                obj.temp_actuelle= 0
                obj.autre_actuelle= 0
        db.session.commit()
        
        flash(f'Objet {obj.name} mis à jour avec succès!', 'success')
        return redirect(url_for('admin.manage_objects'))
    
    return render_template('admin/edit_object.html', 
                           object=obj, 
                           rooms=room_list, 
                           object_types=object_types)

@admin_bp.route('/objects/delete/<int:object_id>', methods=['POST'])
@login_required
def delete_object(object_id):
    User.nb(current_user,'nbD')
    obj = ConnectedObject.query.get_or_404(object_id)
    
    object_name = obj.name
    for action in obj.actions:
        db.session.delete(action)
    ObjetHistorique.query.filter_by(object_id=object_id).delete()
    db.session.delete(obj)
    db.session.commit()
    
    flash(f'Objet {object_name} supprimé avec succès!', 'success')
    return redirect(url_for('admin.manage_objects'))

@admin_bp.route('/object-types')
@login_required
def manage_object_types():
    object_types = ObjectType.query.filter_by(house_id=current_user.house_id).all()
    return render_template('admin/object_types.html', object_types=object_types)

@admin_bp.route('/object-types/add', methods=['GET', 'POST'])
@login_required
def add_object_type():
    User.nb(current_user,'nbAtype')
    if request.method == 'POST':
        name = request.form['name'].lower()
        description = request.form['description']
        icon = request.form['icon']
        
        existing_type = ObjectType.query.filter_by(name=name, house_id=current_user.house_id).first()
        if existing_type:
            flash(f'Un type d\'objet avec le nom {name} existe déjà dans votre maison.', 'danger')
            return redirect(url_for('admin.add_object_type'))
        
        new_type = ObjectType(
            name=name,
            description=description,
            icon=icon,
            house_id=current_user.house_id
        )
        
        db.session.add(new_type)
        db.session.commit()
        
        flash(f'Type d\'objet {name} ajouté avec succès!', 'success')
        return redirect(url_for('admin.manage_object_types'))
    
    return render_template('admin/add_object_type.html')


@admin_bp.route('/object-types/delete/<int:type_id>', methods=['POST'])
@login_required
def delete_object_type(type_id):
    User.nb(current_user,'nbD')
    obj_type = ObjectType.query.get_or_404(type_id)
    type_name = obj_type.name
    
    objects = ConnectedObject.query.filter_by(object_type_id=type_id).all()
    
    for obj in objects:
        for action in obj.actions:
            db.session.delete(action)
        db.session.delete(obj)
    
    db.session.delete(obj_type)
    db.session.commit()
    
    flash(f'Type d\'objet {type_name} et tous les objets associés supprimés avec succès!', 'success')
    return redirect(url_for('admin.manage_object_types'))


@admin_bp.route('/rooms')
@login_required
def manage_rooms():
    house_id = current_user.house_id
    rooms = Room.query.filter_by(house_id=house_id).all()
    return render_template('admin/rooms.html', rooms=rooms)

@admin_bp.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    User.nb(current_user,'nbAROOM')
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        floor = request.form['floor']
        
        new_room = Room(
            name=name,
            description=description,
            floor=floor,
            house_id=current_user.house_id
        )
        
        db.session.add(new_room)
        db.session.commit()
        
        flash(f'Pièce {name} ajoutée avec succès!', 'success')
        return redirect(url_for('admin.manage_rooms'))
    
    return render_template('admin/add_room.html')


@admin_bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    User.nb(current_user,'nbD')
    room = Room.query.get_or_404(room_id)
    
    objects = ConnectedObject.query.filter_by(room_id=room_id).all()
    if objects:
        flash(f'Impossible de supprimer la pièce car {len(objects)} objets y sont associés. Déplacez-les d\'abord.', 'danger')
        return redirect(url_for('admin.manage_rooms'))
    
    room_name = room.name
    db.session.delete(room)
    db.session.commit()
    
    flash(f'Pièce {room_name} supprimée avec succès!', 'success')
    return redirect(url_for('admin.manage_rooms'))


@admin_bp.route('/stats')
@login_required
def view_stats():
    house_id=current_user.house_id
    total_users = User.query.filter_by(house_id=house_id).count()
    total_connexions = db.session.query(
            db.func.sum(User.connection_count)
        ).filter_by(house_id=house_id).scalar() or 0
    avg_connexions = db.session.query(
            db.func.avg(User.connection_count)
        ).filter_by(house_id=house_id).scalar() or 0
    total_objects = ConnectedObject.query.filter_by(house_id=house_id).count()
        
    total_rooms = Room.query.filter_by(house_id=house_id).count()

    return render_template('admin/statistics.html',total_users=total_users,total_connexion=total_connexions,avg=avg_connexions,obj=total_objects,room=total_rooms)
@admin_bp.route('/stats/data')
@login_required
def stats_data():
    
    house_id = current_user.house_id
    
    try:
        total_users = User.query.filter_by(house_id=house_id).count()
        user_levels = db.session.query(
            User.level, db.func.count(User.id)
        ).filter_by(house_id=house_id).group_by(User.level).all()
        
        user_types = db.session.query(
            User.member_type, db.func.count(User.id)
        ).filter_by(house_id=house_id).group_by(User.member_type).all()
        
        total_connexions = db.session.query(
            db.func.sum(User.connection_count)
        ).filter_by(house_id=house_id).scalar() or 0
        
        avg_connexions = db.session.query(
            db.func.avg(User.connection_count)
        ).filter_by(house_id=house_id).scalar() or 0
        
        most_connected_users = db.session.query(
            User.username, User.connection_count
        ).filter_by(house_id=house_id).order_by(User.connection_count.desc()).limit(5).all()
        
        total_objects = ConnectedObject.query.filter_by(house_id=house_id).count()
        objects_by_type = db.session.query(
            ObjectType.name, db.func.count(ConnectedObject.id)
        ).join(ObjectType).filter(ConnectedObject.house_id == house_id).group_by(ObjectType.name).all()
        
        total_rooms = Room.query.filter_by(house_id=house_id).count()
        objects_by_room = db.session.query(
            Room.name, db.func.count(ConnectedObject.id)
        ).join(Room).filter(ConnectedObject.house_id == house_id).group_by(Room.name).all()
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        connexions_by_day = db.session.query(
                User.username,
                User.connection_count
            ).filter(
                User.house_id == house_id,
                User.created_at >= thirty_days_ago
            ).all()

        conso = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.conso_actuelle
        ).filter(ConnectedObject.house_id == house_id).all()

        eau = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.eau_actuelle
        ).filter(ConnectedObject.house_id == house_id).all()

        gaz = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.gaz_actuelle
        ).filter(ConnectedObject.house_id == house_id).all()

        autre = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.autre_actuelle
        ).filter(ConnectedObject.house_id == house_id).all()

        temp = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.temp_actuelle
        ).filter(ConnectedObject.house_id == house_id).all()

        service_stats = db.session.query(
            func.sum(User.nbR).label('recherches'),
            func.sum(User.nbAU).label('ajout_utilisateurs'),
            func.sum(User.nbDU).label('delete_utilisateur'),
            func.sum(User.nbA).label('ajout_objet'),
            func.sum(User.nbAROOM).label('ajout_room'),
            func.sum(User.nbAType).label('ajout_type'),
            func.sum(User.nbD).label('delete'),
            func.sum(User.nbM).label('modifications'),
            func.sum(User.nbMO).label('modifObjet')
            ).filter_by(house_id=house_id).first()

        return jsonify({
            'total_users': total_users,
            'user_levels': [list(item) for item in user_levels],
            'user_types': [list(item) for item in user_types],
            'total_connexions': total_connexions,
            'avg_connexions': round(avg_connexions, 2),
            'most_connected_users': [list(item) for item in most_connected_users],
            'total_objects': total_objects,
            'objects_by_type': [list(item) for item in objects_by_type],
            'total_rooms': total_rooms,
            'objects_by_room': [list(item) for item in objects_by_room],
            'connexions_by_day': [list(item) for item in connexions_by_day],
            'conso': [list(item) for item in conso],
            'eau': [list(item) for item in eau],
            'gaz': [list(item) for item in gaz],
            'autre': [list(item) for item in autre],
            'temp': [list(item) for item in temp],
            'service_stats': {
                    'recherches': service_stats.recherches or 0,
                    'ajout_utilisateurs': service_stats.ajout_utilisateurs or 0,
                    'delete_utilisateur': service_stats.delete_utilisateur or 0,
                    'ajout_objet': service_stats.ajout_objet or 0,
                    'ajout_room': service_stats.ajout_room or 0,
                    'ajout_type': service_stats.ajout_type or 0,
                    'delete': service_stats.delete or 0,
                    'modifications': service_stats.modifications or 0,
                    'modifObjet': service_stats.modifObjet or 0
                    }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@admin_bp.route('/export/stats/pdf')
@login_required
def export_stats_pdf():
    house_id = current_user.house_id
    
    total_users = User.query.filter_by(house_id=house_id).count()
    obj = ConnectedObject.query.filter_by(house_id=house_id).count()
    room = Room.query.filter_by(house_id=house_id).count()
    total_connexion = db.session.query(db.func.sum(User.connection_count)).filter(User.house_id == house_id).scalar() or 0
    conso = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.conso_actuelle
        ).filter(
                ConnectedObject.house_id == house_id,
                ConnectedObject.conso_actuelle !=  None 
        ).all()
    temp = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.temp_actuelle
        ).filter(
                ConnectedObject.house_id == house_id,
                ConnectedObject.temp_actuelle !=  None 
        ).all()
    eau = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.eau_actuelle
        ).filter(
                ConnectedObject.house_id == house_id,
                ConnectedObject.eau_actuelle !=  None 
        ).all()
    gaz = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.gaz_actuelle
        ).filter(
                ConnectedObject.house_id == house_id,
                ConnectedObject.gaz_actuelle !=  None 
        ).all()
    autre = db.session.query(
            ConnectedObject.name, 
            ConnectedObject.autre_actuelle
        ).filter(
                ConnectedObject.house_id == house_id,
                ConnectedObject.autre_actuelle !=  None 
        ).all()
    service_stats = db.session.query(
            func.sum(User.nbR).label('Recherches'),
            func.sum(User.nbAU).label('Ajout_utilisateurs'),
            func.sum(User.nbDU).label('Delete_utilisateur'),
            func.sum(User.nbA).label('Ajout_objet'),
            func.sum(User.nbAROOM).label('Ajout_room'),
            func.sum(User.nbAType).label('Ajout_type'),
            func.sum(User.nbD).label('Delete'),
            func.sum(User.nbM).label('Modifications'),
            func.sum(User.nbMO).label('ModifObjet')
            ).filter_by(house_id=house_id).first()
    service_data = {
        "Recherches": service_stats.Recherches,
        "Ajout utilisateurs": service_stats.Ajout_utilisateurs,
        "Suppression utilisateurs": service_stats.Delete_utilisateur,
        "Ajout objets": service_stats.Ajout_objet,
        "Ajout pièces": service_stats.Ajout_room,
        "Ajout types": service_stats.Ajout_type,
        "Suppression objets": service_stats.Delete,
        "Modifications": service_stats.Modifications,
        "Modifications objets": service_stats.ModifObjet
    }

    Bon_service_data = {
        key: value for key, value in service_data.items() if value not in (None, 0)
    }
    service_data_tuples = [(key, value) for key, value in Bon_service_data.items()]


    avg = round(total_connexion / total_users, 2) if total_users > 0 else 0
    
    
    user_levels = db.session.query(
        User.level, db.func.count(User.id)
    ).filter_by(house_id=house_id).group_by(User.level).all()
    
    objects_by_type = db.session.query(
        ObjectType.name, db.func.count(ConnectedObject.id)
    ).join(ObjectType).filter(ConnectedObject.house_id == house_id).group_by(ObjectType.name).all()
    
    objects_by_room = db.session.query(
        Room.name, db.func.count(ConnectedObject.id)
    ).join(Room).filter(ConnectedObject.house_id == house_id).group_by(Room.name).all()
    
    graph_images = {
        'user_levels': generate_pie_chart(user_levels, "Utilisateurs par niveau"),
        'Bon_service_data': generate_pie_chart(service_data_tuples, "statistique des services utiliser"),
        'objects_by_type': generate_bar_chart(objects_by_type, "Objets par type"),
        'objects_by_room': generate_bar_chart(objects_by_room, "Objets par pièce"),
        'consomation': generate_bar_chart(conso,'consomation','conso'),
        'température': generate_bar_chart(temp,'température','temp'),
        'eau': generate_bar_chart(eau,'eau','eau'),
        'gaz': generate_bar_chart(gaz,'gaz','gaz'),
        'autre': generate_bar_chart(autre,'autre','autre')
    }
    
    html = render_template('admin/pdf/stats_report.html', 
                          total_users=total_users,
                          obj=obj,
                          room=room,
                          total_connexion=total_connexion,
                          avg=avg,
                          house=House.query.get(house_id),
                          current_user=current_user,
                          current_date=datetime.utcnow(),
                          graph_images=graph_images)
    
    pdf_file = BytesIO()
    HTML(string=html).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    response = make_response(pdf_file.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=statistiques-maison.pdf'
    return response

def generate_pie_chart(data, title):
    """Génère un diagramme circulaire à partir des données"""
    labels = [item[0] for item in data]
    values = [item[1] for item in data]
    
    plt.figure(figsize=(8, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, 
            colors=['#54A0FF', '#FFDA79', '#4BCFFA', '#FF7675'])
    plt.axis('equal') 
    plt.title(title)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"

def generate_bar_chart(data, title,n= None):
    """Génère un diagramme en barres à partir des données"""
    labels = [item[0] for item in data]
    values = [item[1] for item in data]
    
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='#54A0FF')
    
    plt.xlabel('Catégories')
    if n == 'conso':
        plt.ylabel('Consomation en Watts')
    elif n == 'temp':
        plt.ylabel('température en degré')
    elif n == 'eau':
        plt.ylabel('consomation en Litre')
    elif n == 'gaz':
        plt.ylabel('Consomation en metre cube')
    elif n == 'autre':
        plt.ylabel('Consomation autre')
    else:
        plt.ylabel('Nombre')
    plt.title(title)
    
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"