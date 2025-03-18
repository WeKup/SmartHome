from flask import Flask
from routes.info import info_bp
from routes.auth import auth_bp
# Ces imports seront activés plus tard quand vous développerez les autres modules
# from routes.visualization import visualization_bp
# from routes.management import management_bp
# from routes.admin import admin_bp

app = Flask(__name__)
app.config.from_object('config.Config')

# Enregistrer les blueprints
app.register_blueprint(info_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
# app.register_blueprint(visualization_bp, url_prefix='/dashboard')
# app.register_blueprint(management_bp, url_prefix='/management')
# app.register_blueprint(admin_bp, url_prefix='/admin')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page non trouvée"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="Erreur interne du serveur"), 500

if __name__ == '__main__':
    app.run(debug=True)