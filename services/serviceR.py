
SERVICES_BY_CATEGORY = {
    "ajout": [
        {"id": 1, "name": "Ajout d'objets connectés", "is_upcoming": False},
        {"id": 2, "name": "Ajout de membres", "is_upcoming": False},
        {"id": 3, "name": "Ajout de types d'objets", "is_upcoming": False},
        {"id": 4, "name": "Ajout de pièces", "is_upcoming": False},
        {"id": 55, "name": "Ajout de pièces via le controle vocal", "is_upcoming": True}
    ],
    "suppression": [
        {"id": 5, "name": "Suppression d'objets", "is_upcoming": False},
        {"id": 6, "name": "Suppression de membres", "is_upcoming": False},
        {"id": 7, "name": "Suppression de types d'objets", "is_upcoming": False},
        {"id": 54, "name": "Suppression de vos voisin", "is_upcoming": True},
        {"id": 56, "name": "suppression de pièces via le controle vocal", "is_upcoming": True}
    ],
    "modification": [
        {"id": 8, "name": "Modification des paramètres d'objets", "is_upcoming": False},
        {"id": 9, "name": "Modification des profils utilisateurs", "is_upcoming": False},
        {"id": 10, "name": "Modification des pièces", "is_upcoming": False},
        {"id": 50, "name": "Modification du type de matière de votre maison", "is_upcoming": True},
        {"id": 51, "name": "Modification de l'isolation de votre maison", "is_upcoming": True},
        {"id": 57, "name": "modification de pièces via le controle vocal", "is_upcoming": True}
    ],
    "consultation": [
        {"id": 11, "name": "Consultation des statistiques", "is_upcoming": False},
        {"id": 12, "name": "Consultation des objets", "is_upcoming": False},
        {"id": 13, "name": "Consultation des membres", "is_upcoming": False},
        {"id": 52, "name": "Consultation de la nuisance sonore externe", "is_upcoming": True},
        {"id": 58, "name": "consultation de pièces via le controle vocal", "is_upcoming": True}
    ]
}

def get_services(category=None, upcoming_only=False):
    if category:
        services = SERVICES_BY_CATEGORY.get(category, [])
    else:
        services = []
        for category_services in SERVICES_BY_CATEGORY.values():
            services.extend(category_services)
    
    if upcoming_only:
        services = [service for service in services if service["is_upcoming"]]
    
    return services