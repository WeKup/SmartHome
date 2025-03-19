from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.auth import db, User, House
from werkzeug.security import generate_password_hash
import random
import string

# Créer le blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
   # if current_user.is_authenticated:
    #    return redirect(url_for('info.home'))
        
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
            
            # Incrémenter le compteur de connexions
            user.connection_count += 1
            db.session.commit()
            
            flash(f'Bienvenue, {user.username} !', 'success')
            
            # Rediriger vers la page demandée ou l'accueil
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('info.home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
   # if current_user.is_authenticated:
   #     return redirect(url_for('info.home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        house_code = request.form.get('house_code', '').upper()  # Code de maison
        
        # Vérifications de base
        if not username or not email or not password:
            flash('Tous les champs sont obligatoires!', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas!', 'danger')
            return render_template('auth/register.html')
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà utilisé', 'danger')
            return render_template('auth/register.html')
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Cette adresse email est déjà utilisée', 'danger')
            return render_template('auth/register.html')
        
        # Si un code de maison est fourni, vérifier s'il existe
        house = None
        if house_code:
            house = House.query.filter_by(house_code=house_code).first()
            if not house:
                flash('Code de maison invalide', 'danger')
                return render_template('auth/register.html')
        
        # Création de l'utilisateur
        new_user = User(
            username=username,
            email=email,
            level='débutant',
            points=0,
            is_admin=False
        )
        new_user.set_password(password)
        
        # Si une maison a été trouvée, associer l'utilisateur
        if house:
            new_user.house_id = house.id
            
        db.session.add(new_user)
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/create-house', methods=['GET', 'POST'])
def create_house():
    """Page de création de maison"""
    #if current_user.is_authenticated:
     #   return redirect(url_for('info.home'))
        
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