from flask import Blueprint, render_template, request
from services.news_service import NewsService
from models.demo_data import get_demo_stats

info_bp = Blueprint('info', __name__)

news_service = NewsService()

@info_bp.route('/')
def home():
    stats = get_demo_stats()
    
    latest_news = news_service.get_latest_news(3)
    
    return render_template('info/home.html', stats=stats, latest_news=latest_news)

@info_bp.route('/news')
def news():
    all_news = news_service.get_all_news()
    
    return render_template('info/news.html', news=all_news)

@info_bp.route('/search', methods=['GET', 'POST'])
def search():
    from models.demo_data import get_object_types, get_demo_rooms, search_demo_objects
    
    object_types = get_object_types()
    rooms = get_demo_rooms()
    
    results = None
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        type_id = request.form.get('type', '')
        room_id = request.form.get('room', '')
        
        results = search_demo_objects(query, type_id, room_id)
    
    return render_template('info/search.html', 
                          object_types=object_types, 
                          rooms=rooms, 
                          results=results)