from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from models.auth import db, User
from routes.info import info_bp
from routes.auth import auth_bp
import datetime

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialisation de la bdd
db.init_app(app)
migrate = Migrate(app, db)

# Initialisation du login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#enregistre / ramène les blueprint
app.register_blueprint(info_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')

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