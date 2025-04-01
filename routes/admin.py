from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.auth import db, House, User, Room, ConnectedObject, ObjectType
from werkzeug.security import generate_password_hash
import random
import string
from datetime import datetime
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def accueil():
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
@login_required
def manage_users():
    house_id = current_user.house_id
    users = User.query.filter_by(house_id=current_user.house_id).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
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
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form.get('password'):
            user.set_password(request.form['password'])
        user.gender = request.form['gender']
        user.birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
        user.member_type = request.form['member_type']
        user.is_admin = 'is_admin' in request.form
        
        if 'level' in request.form and request.form['level'] != user.level:
            user.level = request.form['level']
        
        db.session.commit()
        flash(f'Utilisateur {user.username} mis à jour avec succès!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
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
            data={}
        )
        
        db.session.add(new_object)
        db.session.commit()
        
        flash(f'Objet {name} ajouté avec succès!', 'success')
        return redirect(url_for('admin.manage_objects'))
    
    return render_template('admin/add_object.html', rooms=room_list, object_types=object_types)

@admin_bp.route('/objects/edit/<int:object_id>', methods=['GET', 'POST'])
@login_required
def edit_object(object_id):
    obj = ConnectedObject.query.get_or_404(object_id)
    house_id = current_user.house_id
    room_list = Room.query.filter_by(house_id=house_id).all()
    object_types = ObjectType.query.filter_by(house_id=house_id).all()
    
    if request.method == 'POST':
        obj.name = request.form['name']
        obj.description = request.form['description']
        obj.object_type_id = request.form['object_type_id']
        obj.room_id = request.form['room_id']
        obj.brand = request.form['brand']
        obj.model = request.form['model']
        obj.status = request.form['status']
        obj.connection_status = request.form['connection_status']
        
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
    obj = ConnectedObject.query.get_or_404(object_id)
    
    object_name = obj.name
    for action in obj.actions:
        db.session.delete(action)
    
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

