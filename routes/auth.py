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
from services.mail import send_verification_email
from flask_mail import Mail
auth_bp = Blueprint('auth', __name__)
mail = Mail()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        house = House.query.get(current_user.house_id)
        if house.Join_method == 'mail' and current_user.email_verified:
            return redirect(url_for('connected.accueil'))
        elif house.Join_method == 'Approbation' and current_user.requete == 0:
            return redirect(url_for('connected.accueil'))
        
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Veuillez remplir tous les champs', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        
        if user and user.check_password(password):
            login_user(user)
            house = House.query.get(current_user.house_id)
            user.update_user_points('connection')
            if house.Join_method== 'mail':
                if not user.email_verified:
                    flash('Veuillez vérifier votre email avant de vous connecter. Vérifiez votre boîte de réception.', 'warning')
                    return render_template('auth/login.html')

            if house.Join_method== 'Approbation':
                if current_user.requete == 1:
                    flash('Veuillez attendre que un administrateur vous valide.', 'warning')
                    return render_template('auth/login.html')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('connected.accueil'))
            flash(f'Bienvenue, {user.username} !', 'success')
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        house = House.query.get(current_user.house_id)
        if house.Join_method == 'mail' and current_user.email_verified:
            return redirect(url_for('connected.accueil'))
        elif house.Join_method == 'Approbation' and current_user.requete == 0:
            return redirect(url_for('connected.accueil'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        nom=request.form.get('nom')
        prénom=request.form.get('prénom')
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
            nom=nom,
            prénom=prénom,
            email=email,
            gender=gender,
            birthdate=parsed_birthdate,
            member_type=member_type,
            level='débutant',
            points=0,
            is_admin=is_admin,
            email_verified=False
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

        if house.Join_method == 'mail':
            send_verification_email(new_user, mail)
            db.session.commit()
            flash('Plus qu' 'a valider grace a votre mail est c' 'est bon')
            return redirect(url_for('auth.login'))
        if house.Join_method == 'Approbation':
            new_user.requete=1
            new_user.email_verified=1
            db.session.commit()
            flash('Plus qu' 'a attendre qu' 'un admin vous valide')
            return redirect(url_for('auth.login'))
        
        
    
    return render_template('auth/register.html')

@auth_bp.route('/create-house', methods=['GET', 'POST'])
def create_house():
    """Page de création de maison"""
    if current_user.is_authenticated:
        house = House.query.get(current_user.house_id)
        if house.Join_method == 'mail' and current_user.email_verified:
            return redirect(url_for('connected.accueil'))
        elif house.Join_method == 'Approbation' and current_user.requete == 0:
            return redirect(url_for('connected.accueil'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        prénom=request.form.get('prénom')
        nom = request.form.get('nom')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        house_name = request.form.get('house_name')
        house_description = request.form.get('house_description', '')
        member_type = request.form.get('member_type')
        
        if not username or not email or not password or not house_name or not member_type:
            flash('Tous les champs marqués * sont obligatoires!', 'danger')
            return render_template('auth/create_house.html')
            
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas!', 'danger')
            return render_template('auth/create_house.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà utilisé', 'danger')
            return render_template('auth/create_house.html')
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Cette adresse email est déjà utilisée', 'danger')
            return render_template('auth/create_house.html')
        
        house_code = House.generate_unique_code()
        
        new_house = House(
            name=house_name,
            description=house_description,
            house_code=house_code,
            is_demo=False
        )
        db.session.add(new_house)
        db.session.flush()
        
        new_user = User(
            username=username,
            nom=nom,
            prénom=prénom,
            email=email,
            member_type=member_type,
            level='débutant',
            points=0,
            house_id=new_house.id,
            is_admin=True 
        )
        new_user.set_password(password)
        send_verification_email(new_user, mail)
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

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash('Le lien de vérification est invalide.', 'danger')
        return redirect(url_for('auth.login'))

    user.email_verified = True
    user.verification_token = None
    user.token_expiration = None
    db.session.commit()
    
    flash('Votre email a été vérifié avec succès! Vous pouvez maintenant vous connecter.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Aucun compte trouvé avec cette adresse email.', 'danger')
            return render_template('auth/resend_verification.html')
        
        if user.email_verified:
            flash('Votre email est déjà vérifié. Vous pouvez vous connecter.', 'info')
            return redirect(url_for('auth.login'))
        
        send_verification_email(user, mail)
        db.session.commit()
        
        flash('Un nouvel email de vérification a été envoyé. Veuillez vérifier votre boîte de réception.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/resend_verification.html')