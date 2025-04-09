from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.auth import db, User, House
from werkzeug.security import generate_password_hash
import random
import string
import os
from datetime import *
import time
from werkzeug.utils import secure_filename
from config import *
# Créer le blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('connected.accueil'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vérifier si les champs sont remplis
        if not username or not password:
            flash('Veuillez remplir tous les champs', 'danger')
            return render_template('auth/login.html')
        
        # Rechercher l'utilisateur dans la base de données
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Connexion réussie
            login_user(user)
            
            user.update_user_points('connection')
            
            flash(f'Bienvenue, {user.username} !', 'success')
            
            # Rediriger vers la page demandée ou l'accueil
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('connected.accueil'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if current_user.is_authenticated:
        return redirect(url_for('connected.accueil'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        house_code = request.form.get('house_code', '').upper()
        gender = request.form.get('gender')
        birthdate = request.form.get('birthdate')
        member_type = request.form.get('member_type')
        is_admin = request.form.get('is_admin') == 'on'
        
        if not username or not email or not password:
            flash('Tous les champs sont obligatoires!', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas!', 'danger')
            return render_template('auth/register.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà utilisé', 'danger')
            return render_template('auth/register.html')
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Cette adresse email est déjà utilisée', 'danger')
            return render_template('auth/register.html')
        
        house = None
        if house_code:
            house = House.query.filter_by(house_code=house_code).first()
            if not house:
                flash('Code de maison invalide', 'danger')
                return render_template('auth/register.html')
        
        parsed_birthdate = None
        if birthdate:
            try:
                parsed_birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()
            except ValueError:
                flash('Format de date invalide', 'danger')
                return render_template('auth/register.html')
        
        if member_type in ['père', 'mère']:
            is_admin = True
        
        new_user = User(
            username=username,
            email=email,
            gender=gender,
            birthdate=parsed_birthdate,
            member_type=member_type,
            level='débutant',
            points=0,
            is_admin=is_admin
        )
        new_user.set_password(password)
        
        if house:
            new_user.house_id = house.id
            
        db.session.add(new_user)
        db.session.flush()
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{new_user.id}_{int(time.time())}_{file.filename}")
                    
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    
                    path = os.path.join('images/profile_pictures', filename)
                    new_user.profile_photo = path.replace('\\', '/')
                else:
                    flash('Format de fichier non autorisé. Utilisez PNG, JPG, JPEG ou GIF.', 'danger')
        
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/create-house', methods=['GET', 'POST'])
def create_house():
    """Page de création de maison"""
    if current_user.is_authenticated:
        return redirect(url_for('connected.accueil'))
        
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        house_name = request.form.get('house_name')
        house_description = request.form.get('house_description', '')
        member_type = request.form.get('member_type')
        
        # Vérifications de base
        if not username or not email or not password or not house_name or not member_type:
            flash('Tous les champs marqués * sont obligatoires!', 'danger')
            return render_template('auth/create_house.html')
            
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas!', 'danger')
            return render_template('auth/create_house.html')
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà utilisé', 'danger')
            return render_template('auth/create_house.html')
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Cette adresse email est déjà utilisée', 'danger')
            return render_template('auth/create_house.html')
        
        # Créer un code unique pour la maison
        house_code = House.generate_unique_code()
        
        # Créer la maison
        new_house = House(
            name=house_name,
            description=house_description,
            house_code=house_code,
            is_demo=False
        )
        db.session.add(new_house)
        db.session.flush()  # Pour obtenir l'ID de la maison
        
        # Créer l'utilisateur
        new_user = User(
            username=username,
            email=email,
            member_type=member_type,
            level='débutant',
            points=0,
            house_id=new_house.id,
            is_admin=True  # Premier utilisateur = admin
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Maison "{house_name}" créée avec succès! Votre code de maison est: {house_code}. Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/create_house.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté!', 'success')
    return redirect(url_for('info.home'))