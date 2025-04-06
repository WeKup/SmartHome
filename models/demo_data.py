
def get_demo_stats():
    return {
        'objects_count': 15,
        'rooms_count': 7,
        'active_objects': 12
    }

def get_object_types():
    """Retourne les types d'objets connectés"""
    return [
        {'id': 1, 'name': 'Thermostat', 'icon': 'fa-thermometer-half'},
        {'id': 2, 'name': 'Éclairage', 'icon': 'fa-lightbulb'},
        {'id': 3, 'name': 'Caméra', 'icon': 'fa-video'},
        {'id': 4, 'name': 'Serrure', 'icon': 'fa-lock'},
        {'id': 5, 'name': 'Électroménager', 'icon': 'fa-blender'},
        {'id': 6, 'name': 'Capteur', 'icon': 'fa-sensor-on'},
        {'id': 7, 'name': 'Divertissement', 'icon': 'fa-tv'},
        {'id': 8, 'name': 'Énergie', 'icon': 'fa-bolt'}
    ]


def get_room_id_by_name(name):
    rooms = get_demo_rooms()
    for room in rooms:
        if room['name'].strip().lower() == name.strip().lower():
            return room['id']
    
    # Si la salle n'existe pas, retourne le max ID + 1
    max_id = max(room['id'] for room in rooms)
    return max_id + 1


def get_demo_rooms():
    """Retourne les pièces de la maison de démo"""
    return [
        {'id': 1, 'name': 'Salon', 'floor': 0},
        {'id': 2, 'name': 'Cuisine', 'floor': 0},
        {'id': 3, 'name': 'Chambre principale', 'floor': 1},
        {'id': 4, 'name': 'Chambre enfant', 'floor': 1},
        {'id': 5, 'name': 'Salle de bain', 'floor': 1},
        {'id': 6, 'name': 'Bureau', 'floor': 0},
        {'id': 7, 'name': 'Garage', 'floor': 0}
    ]

def get_demo_objects():
    """Retourne les objets connectés de démo"""
    return [
        {
            'id': 1,
            'name': 'Thermostat Salon',
            'description': 'Contrôle la température dans le salon',
            'type_id': 1,
            'room_id': 1,
            'brand': 'Nest',
            'model': 'Learning Thermostat 3rd Gen',
            'status': 'active'
        },
        {
            'id': 2,
            'name': 'Éclairage Salon',
            'description': 'Système d\'éclairage intelligent pour le salon',
            'type_id': 2,
            'room_id': 1,
            'brand': 'Philips',
            'model': 'Hue White and Color',
            'status': 'active'
        },
        {
            'id': 3,
            'name': 'Caméra Salon',
            'description': 'Surveillance visuelle dans le salon',
            'type_id': 3,
            'room_id': 1,
            'brand': 'Ring',
            'model': 'Indoor Cam',
            'status': 'active'
        },
        {
            'id': 4,
            'name': 'Thermostat Cuisine',
            'description': 'Contrôle la température dans la cuisine',
            'type_id': 1,
            'room_id': 2,
            'brand': 'Nest',
            'model': 'Learning Thermostat 3rd Gen',
            'status': 'active'
        },
        {
            'id': 5,
            'name': 'Réfrigérateur Intelligent',
            'description': 'Réfrigérateur connecté avec contrôle de température',
            'type_id': 5,
            'room_id': 2,
            'brand': 'Samsung',
            'model': 'Family Hub',
            'status': 'active'
        },
        {
            'id': 6,
            'name': 'Thermostat Chambre',
            'description': 'Contrôle la température dans la chambre principale',
            'type_id': 1,
            'room_id': 3,
            'brand': 'Nest',
            'model': 'Learning Thermostat 3rd Gen',
            'status': 'active'
        },
        {
            'id': 7,
            'name': 'Éclairage Chambre',
            'description': 'Système d\'éclairage intelligent pour la chambre',
            'type_id': 2,
            'room_id': 3,
            'brand': 'Philips',
            'model': 'Hue White and Color',
            'status': 'active'
        },
        {
            'id': 8,
            'name': 'Aspirateur Robot',
            'description': 'Aspirateur robot programmable',
            'type_id': 5,
            'room_id': 1,
            'brand': 'iRobot',
            'model': 'Roomba 980',
            'status': 'inactive'
        },
        {
            'id': 9,
            'name': 'Enceinte Intelligente',
            'description': 'Enceinte avec assistant vocal',
            'type_id': 7,
            'room_id': 1,
            'brand': 'Amazon',
            'model': 'Echo Dot',
            'status': 'active'
        },
        {
            'id': 10,
            'name': 'Détecteur de Fumée',
            'description': 'Détecteur de fumée connecté',
            'type_id': 6,
            'room_id': 2,
            'brand': 'Nest',
            'model': 'Protect',
            'status': 'active'
        },
        {
            'id': 11,
            'name': 'Serrure Porte d\'entrée',
            'description': 'Serrure connectée avec contrôle à distance',
            'type_id': 4,
            'room_id': 1,
            'brand': 'August',
            'model': 'Smart Lock Pro',
            'status': 'active'
        },
        {
            'id': 12,
            'name': 'Compteur d\'énergie',
            'description': 'Mesure la consommation électrique',
            'type_id': 8,
            'room_id': 7,
            'brand': 'Sense',
            'model': 'Home Energy Monitor',
            'status': 'active'
        },
        {
            'id': 13,
            'name': 'Télévision Intelligente',
            'description': 'Télévision connectée',
            'type_id': 7,
            'room_id': 1,
            'brand': 'Samsung',
            'model': 'QLED Smart TV',
            'status': 'active'
        },
        {
            'id': 14,
            'name': 'Thermostat Bureau',
            'description': 'Contrôle la température dans le bureau',
            'type_id': 1,
            'room_id': 6,
            'brand': 'Nest',
            'model': 'Learning Thermostat 3rd Gen',
            'status': 'inactive'
        },
        {
            'id': 15,
            'name': 'Station Météo',
            'description': 'Mesure les conditions météorologiques',
            'type_id': 6,
            'room_id': 7,
            'brand': 'Netatmo',
            'model': 'Weather Station',
            'status': 'active'
        }
    ]

def search_demo_objects(query='', type_id='', room_id=''):
    """
    Recherche dans les objets connectés de démo
    
    Args:
        query (str): Texte de recherche
        type_id (str): ID du type d'objet
        room_id (str): ID de la pièce
    
    Returns:
        list: Liste d'objets correspondant aux critères
    """
    # Convertir en entiers si non vides
    type_id = int(type_id) if type_id else None
    room_id = int(room_id) if room_id else None
    
    objects = get_demo_objects()
    results = []
    
    for obj in objects:
        # Filtre par mot-clé (nom ou description)
        if query and query.lower() not in obj['name'].lower() and query.lower() not in obj['description'].lower():
            continue
        
        # Filtre par type
        if type_id and obj['type_id'] != type_id:
            continue
        
        # Filtre par pièce
        if room_id and obj['room_id'] != room_id:
            continue
        
        # Ajouter les informations sur le type et la pièce
        obj_type = next((t for t in get_object_types() if t['id'] == obj['type_id']), None)
        room = next((r for r in get_demo_rooms() if r['id'] == obj['room_id']), None)
        
        if obj_type and room:
            obj['type'] = obj_type
            obj['room'] = room
            results.append(obj)
    
    return results
