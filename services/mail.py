from flask_mail import Message
from flask import current_app, url_for
from datetime import datetime, timedelta
import secrets

def send_verification_email(user, mail):
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    
    msg = Message(
        'Vérification de votre compte Maison Intelligente',
        recipients=[user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    msg.html = f'''
    <h2>Bienvenue à la Maison Intelligente!</h2>
    <p>Merci de vous être inscrit. Pour activer votre compte, veuillez cliquer sur le lien ci-dessous:</p>
    <p><a href="{verification_url}">Vérifier mon adresse email</a></p>
    <p>Ce lien expirera dans 24 heures.</p>
    <p>Si vous n'avez pas créé de compte, veuillez ignorer cet email.</p>
    '''
    
    mail.send(msg)
    return token
