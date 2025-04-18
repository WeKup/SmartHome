from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from models.auth import db, User
from routes.info import info_bp
from routes.auth import auth_bp
from routes.connected import connected_bp
from routes.admin import admin_bp
from routes.gestion import gestion_bp
import datetime
from config import *
from werkzeug.utils import secure_filename
from flask_mail import Mail

app = Flask(__name__)
mail = Mail()
app.config.from_object('config.Config')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'smarthomepy01@gmail.com'
app.config['MAIL_PASSWORD'] = 'rrzo fwsr oscp nyux'
app.config['MAIL_DEFAULT_SENDER'] = 'smarthomepy01@gmail.com'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Initialisation de la bdd
db.init_app(app)
migrate = Migrate(app, db)

# Initialisation du login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

mail.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#enregistre / ramène les blueprint
app.register_blueprint(info_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(connected_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(gestion_bp)

# Context processor pour les templates
@app.context_processor
def inject_global_vars():
    return {
        'current_year': datetime.datetime.now().year
    }

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page non trouvée"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="Erreur interne du serveur"), 500

# test co bdd
with app.app_context():
    try:
        db.engine.connect()
        print("Connexion à la base de données réussie!")
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
if __name__ == '__main__':
    app.run(debug=True)
