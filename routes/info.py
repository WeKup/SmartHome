from flask import Blueprint, render_template, request
from services.news_service import NewsService
from models.demo_data import get_demo_stats

# Créer le blueprint
info_bp = Blueprint('info', __name__)

# Initialiser le service d'actualités
news_service = NewsService()

@info_bp.route('/')
def home():
    """Page d'accueil pour les visiteurs"""
    # Récupérer les statistiques de démo
    stats = get_demo_stats()
    
    # Récupérer les dernières actualités
    latest_news = news_service.get_latest_news(3)
    
    return render_template('info/home.html', stats=stats, latest_news=latest_news)

@info_bp.route('/news')
def news():
    """Page des actualités"""
    # Récupérer toutes les actualités
    all_news = news_service.get_all_news()
    
    return render_template('info/news.html', news=all_news)

@info_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Page de recherche d'objets connectés"""
    from models.demo_data import get_object_types, get_demo_rooms, search_demo_objects
    
    # Récupérer les types d'objets et les pièces pour les filtres
    object_types = get_object_types()
    rooms = get_demo_rooms()
    
    results = None
    
    if request.method == 'POST':
        # Récupérer les paramètres de recherche
        query = request.form.get('query', '')
        type_id = request.form.get('type', '')
        room_id = request.form.get('room', '')
        
        # Effectuer la recherche
        results = search_demo_objects(query, type_id, room_id)
    
    return render_template('info/search.html', 
                          object_types=object_types, 
                          rooms=rooms, 
                          results=results)