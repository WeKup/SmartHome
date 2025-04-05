from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models.auth import db, User, House, ConnectedObject, Room, ObjectType
import os
import time
from werkzeug.utils import secure_filename
from config import *
connected_bp = Blueprint('connected', __name__, url_prefix='/connected')

@connected_bp.route('/accueil')
@login_required
def accueil():
    connected_objects = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()
    return render_template('connected/accueil.html', user=current_user, connectedObject=connected_objects)

@connected_bp.route('/profil')
@login_required
def profil():
    return render_template('connected/profil.html', user=current_user)

@connected_bp.route('/Aprofile')
@login_required
def Aprofile():
    Famille= User.query.filter_by(house_id=current_user.house_id).all()
    return render_template('connected/Aprofile.html', user=Famille,)

@connected_bp.route('/modifier', methods=['GET', 'POST'])
@login_required
def modifier():
    User.nb(current_user,'nbM')
    if request.method == 'POST':
        username = request.form.get('username')
        if username and username != current_user.username:
            current_user.username = username
        
        email = request.form.get('email')
        if email and email != current_user.email:
            current_user.email = email

        member_type = request.form.get('member_type')
        if member_type and member_type != current_user.member_type:
            current_user.member_type = member_type
        level = request.form.get('level')
        if level and level != current_user.level:
            current_user.level = level

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{current_user.id}_{int(time.time())}_{file.filename}")
                    
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    
                    if current_user.profile_photo:
                        old_path = os.path.join(UPLOAD_FOLDER, 'static', current_user.profile_photo)
                        try:
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        except Exception as e:
                            print(f"Erreur lors de la suppression de l'ancienne photo: {e}")
                    
                    path = os.path.join('images/profile_pictures', filename)
                    current_user.profile_photo = path.replace('\\', '/')
        db.session.commit()
        flash('Profil mis à jour avec succès!', 'gg')
        return redirect(url_for('connected.profil'))
    return render_template('connected/modifier.html', user=current_user,)

@connected_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    connected_objects = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()
    rooms = Room.query.filter_by(house_id=current_user.house_id).all()
    object_types = ObjectType.query.filter_by(house_id=current_user.house_id).all() 
    
    results = []
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        type_id = request.form.get('type', '')
        room_id = request.form.get('room', '')
        
        search_query = ConnectedObject.query.filter_by(house_id=current_user.house_id)
    
        if query:
            search_query = search_query.filter(ConnectedObject.name.ilike(f'%{query}%'))
        
        if type_id and type_id != 'all':
            search_query = search_query.filter_by(object_type_id=type_id)
        
        if room_id and room_id != 'all':
            search_query = search_query.filter_by(room_id=room_id)
        
        results = search_query.all()
        User.nb(current_user,'nbR')
        User.update_user_points(current_user,'search')
    
    return render_template('connected/search.html', 
                           object_types=object_types, 
                           rooms=rooms, 
                           results=results,
                           query=request.form.get('query', '') if request.method == 'POST' else '',
                           selected_type=request.form.get('type', '') if request.method == 'POST' else '',
                           selected_room=request.form.get('room', '') if request.method == 'POST' else '')
@connected_bp.route('/view/<int:object_id>')
@login_required
def view(object_id):
    object = ConnectedObject.query.get_or_404(object_id)
    User.update_user_points(current_user,'view')
    return render_template('connected/view.html',object=object)