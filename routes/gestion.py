from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models.auth import db, User, House, ConnectedObject, Room, ObjectType, ObjetHistorique
import os
import time
import random
from werkzeug.utils import secure_filename
from config import *
from routes.connected import connected_bp
from datetime import datetime, timedelta
gestion_bp = Blueprint('gestion', __name__, url_prefix='/gestion')
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from models.demo_data import get_room_id_by_name


from datetime import datetime, timedelta


@gestion_bp.route('/gestion')
@login_required
def gestion():
    if current_user.level not in ['avancé', 'expert']:
        flash("Vous n'avez pas les droits pour accéder à cette page.", "danger")
        return redirect(url_for('connected.accueil'))     
    """Page de gestion pour utilisateurs connectés"""
    return render_template('gestion/gestion.html', user=current_user)

@gestion_bp.route('/add')
@login_required
def add():
    liste_salle=Room.query.filter_by(house_id=current_user.house_id).all()
    obj= ObjectType.query.filter_by(house_id=current_user.house_id).all()
    return render_template('gestion/add.html', user=current_user,listeRoom=liste_salle, obj=obj)

@gestion_bp.route('/added', methods=['GET', 'POST'])
@login_required
def added():
    if request.method == 'POST':
        nomObj = request.form.get("nomObj")
        room_id = request.form['room_id']
        brandObj = request.form.get("brandObj")
        modeleObj = request.form.get("modeleObj")
        descriptionObj = request.form.get("descriptionObj")
        conso_min = int(request.form['conso_min'])
        conso_max = int(request.form['conso_max'])
        conso_visé= int(request.form['conso_visé'])
        temp_min = int(request.form['temp_min'])
        temp_max = int(request.form['temp_max'])
        temp_visé= int(request.form['temp_visé'])
        object_type_id = request.form['typeobj']
        max_id = db.session.query(func.max(ConnectedObject.id)).scalar() or 0
        new_id = max_id + 1
        conso_actuelle=random.randint(conso_min,conso_max)
        temp_actuelle=random.randint(temp_min,temp_max)
        batterie= random.randint(0,100)
        Objet = ConnectedObject(
            id=new_id,
            name=nomObj,
            object_type_id=object_type_id,
            room_id=room_id,
            description=descriptionObj,
            brand=brandObj,
            model=modeleObj,
            house_id=current_user.house_id,
            status="active",
            conso_min=conso_min,
            conso_max=conso_max,
            conso_actuelle=conso_actuelle,
            conso_visé=conso_visé,
            temp_min=temp_min,
            temp_max=temp_max,
            temp_actuelle=temp_actuelle,
            temp_visé=temp_visé,
            batterie=batterie
        )

    db.session.add(Objet)
    db.session.commit()

    historique = ObjetHistorique(
        object_id=Objet.id,
        timestamp=datetime.utcnow(),
        action="Création",
        status="active"
    )
    db.session.add(historique)
    db.session.commit()
    liste_salle = Room.query.filter_by(house_id=current_user.house_id).all()
    obj_types = ObjectType.query.filter_by(house_id=current_user.house_id).all()
    flash("Objet ajouté avec succès", "success")
    return render_template('gestion/add.html', user=current_user, listeRoom=liste_salle, obj=obj_types)


"""
@gestion_bp.route('/added', methods=["POST"])
@login_required
def added():
    nomObj = request.form.get("nomObj")
    salleObj = request.form.get("salleObj")
    brandObj = request.form.get("brandObj")
    modeleObj = request.form.get("modeleObj")
    descriptionObj = request.form.get("descriptionObj")

    max_id = db.session.query(func.max(ConnectedObject.id)).scalar() or 0
    new_id = max_id + 1

    # 👇 On crée l'objet AVEC un statut initial "active"
    Objet = ConnectedObject(
        id=new_id,
        name=nomObj + " " + salleObj,
        object_type_id=new_id,
        room_id=get_room_id_by_name(salleObj),
        description=descriptionObj,
        brand=brandObj,
        model=modeleObj,
        house_id=current_user.house_id,
        status="active"  # 👈 si tu as ce champ dans ton modèle
    )

    db.session.add(Objet)
    db.session.commit()

    # ✅ 👇 Ajouter une entrée dans l'historique dès la création
    historique = ObjetHistorique(
        object_id=Objet.id,
        timestamp=datetime.utcnow(),
        action="Création",
        status="active"
    )
    db.session.add(historique)
    db.session.commit()

    flash("Objet ajouté avec succès", "success")
    return render_template('gestion/add.html', user=current_user)
"""
   
@gestion_bp.route('/delete', methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        objet_id = request.form.get("objet_id")
        objet = ConnectedObject.query.get_or_404(objet_id)

        admins = User.query.filter_by(house_id=current_user.house_id, is_admin=True).all()
        admin_emails = ",".join([admin.email for admin in admins])

        return render_template('gestion/confirm_delete.html', objet=objet, admins=admins, admin_emails=admin_emails, user=current_user)

    connected_objects = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()
    return render_template('gestion/delete.html', listeObj=connected_objects)


    
@gestion_bp.route('/modif',methods=["POST","GET"])
@login_required
def modif():
    connected_objects = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()    
    return render_template('gestion/modif.html', listeObj=connected_objects)

@gestion_bp.route('/modified',methods=["POST","GET"])
@login_required
def modified():
    objet_id = request.form.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)
    return render_template('gestion/modified.html', obj=objet)

@gestion_bp.route('/modifiedObj', methods=["POST", "GET"])
@login_required
def modifiedObj():
    objet_id = request.form.get("Id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    if objet.house_id != current_user.house_id:
        flash("Vous n'avez pas l'autorisation de modifier cet objet.", "danger")
        return redirect(url_for("connected.accueil"))

    old_name = objet.name
    old_description = objet.description
    old_status = objet.status
    old_brand = objet.brand
    old_model = objet.model
    old_conso_min = objet.conso_min
    old_conso_max = objet.conso_max

    objet.name = request.form.get("name")
    objet.description = request.form.get("description")
    objet.status = request.form.get("status")
    objet.brand = request.form.get("brand")
    objet.model = request.form.get("model")
    objet.conso_min = int(request.form.get("conso_min", 0))
    objet.conso_max = int(request.form.get("conso_max", 100))

    changes = []
    if old_name != objet.name:
        changes.append(f"Nom changé de '{old_name}' à '{objet.name}'")
    if old_description != objet.description:
        changes.append("Description changée")
    if old_status != objet.status:
        changes.append(f"Statut changé de '{old_status}' à '{objet.status}'")
    if old_brand != objet.brand:
        changes.append(f"Marque changée de '{old_brand}' à '{objet.brand}'")
    if old_model != objet.model:
        changes.append(f"Modèle changé de '{old_model}' à '{objet.model}'")
    if old_conso_min != objet.conso_min:
        changes.append(f"Conso min changée de {old_conso_min} à {objet.conso_min}")
    if old_conso_max != objet.conso_max:
        changes.append(f"Conso max changée de {old_conso_max} à {objet.conso_max}")

    if changes:
        historique = ObjetHistorique(
            object_id=objet.id,
            timestamp=datetime.utcnow(),
            action="; ".join(changes),
            status=objet.status
        )
        db.session.add(historique)

    db.session.commit()
    flash("Objet modifié avec succès !", "success")
    return redirect(url_for("gestion.analyse"))
"""

@gestion_bp.route('/modifiedObj', methods=["POST", "GET"])
@login_required
def modifiedObj():
    objet_id = request.form.get("Id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    # Vérifier que l'utilisateur appartient bien à la maison de cet objet
    if objet.house_id != current_user.house_id:
        flash("Vous n'avez pas l'autorisation de modifier cet objet.", "danger")
        return redirect(url_for("connected.accueil"))

    # Sauvegarde des anciennes valeurs avant modification
    old_name = objet.name
    old_description = objet.description
    old_status = objet.status
    old_brand = objet.brand
    old_model = objet.model

    # Récupérer les nouvelles valeurs
    objet.name = request.form.get("name")
    objet.description = request.form.get("description")
    objet.status = request.form.get("status")
    objet.brand = request.form.get("brand")
    objet.model = request.form.get("model")

    # Enregistrer l'historique seulement si les valeurs changent
    changes = []
    if old_name != objet.name:
        changes.append(f"Nom changé de '{old_name}' à '{objet.name}'")
    if old_description != objet.description:
        changes.append(f"Description changée")
    if old_status != objet.status:
        changes.append(f"Statut changé de '{old_status}' à '{objet.status}'")
    if old_brand != objet.brand:
        changes.append(f"Marque changée de '{old_brand}' à '{objet.brand}'")
    if old_model != objet.model:
        changes.append(f"Modèle changé de '{old_model}' à '{objet.model}'")

    if changes:
        historique = ObjetHistorique(
            object_id=objet.id,
            timestamp=datetime.utcnow(),
            action="; ".join(changes),
            status=objet.status  # Enregistrer le statut actuel
        )
        db.session.add(historique)

    db.session.commit()
    flash("Objet modifié avec succès !", "success")
    return redirect(url_for("gestion.analyse"))  # Retourner sur analyse après modification
"""

@gestion_bp.route('/analyse', methods=["GET", "POST"])
@login_required
def analyse():
    """Affiche la page de sélection d'un objet et d'une action"""
    connected_objects = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()
    
    if request.method == "POST":
        objet_id = request.form.get("objet_id")
        action = request.form.get("action")

        if action == "stats":
            return redirect(url_for("gestion.stats", objet_id=objet_id))
        elif action == "rapport":
            return redirect(url_for("gestion.rapport", objet_id=objet_id))
        elif action == "historique":
            return redirect(url_for("gestion.historique", objet_id=objet_id))

    return render_template("gestion/analyse.html", listeObj=connected_objects)

"""
@gestion_bp.route('/stats', methods=['GET'])
@login_required
def stats():
    objet_id = request.args.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    start_date = datetime.utcnow() - timedelta(days=7)

    # Récupérer les changements d’état
    changements = db.session.query(ObjetHistorique.timestamp, ObjetHistorique.status).filter(
        ObjetHistorique.object_id == objet.id,
        ObjetHistorique.timestamp >= start_date
    ).order_by(ObjetHistorique.timestamp.asc()).all()

    total_time_active = 0
    last_active_time = None

    for action in changements:
        if action.status == "active":
            last_active_time = action.timestamp  # Début d'activation
        elif action.status == "inactive" and last_active_time:
            total_time_active += (action.timestamp - last_active_time).total_seconds()
            last_active_time = None  # Remise à zéro

    return render_template("gestion/stats.html", objet=objet, total_time_active=total_time_active)

@gestion_bp.route('/rapport', methods=['GET'])
@login_required
def rapport():
    objet_id = request.args.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    start_date = datetime.utcnow() - timedelta(days=7)

    activations = db.session.query(ObjetHistorique.timestamp, ObjetHistorique.status).filter(
        ObjetHistorique.object_id == objet.id,
        ObjetHistorique.timestamp >= start_date
    ).order_by(ObjetHistorique.timestamp.desc()).all()

    return render_template("gestion/rapport.html", objet=objet, activations=activations)


@gestion_bp.route('/historique', methods=['GET'])
@login_required
def historique():
    objet_id = request.args.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    modifications = db.session.query(ObjetHistorique.timestamp, ObjetHistorique.action, ObjetHistorique.status).filter(
        ObjetHistorique.object_id == objet.id
    ).order_by(ObjetHistorique.timestamp.desc()).all()

    return render_template("gestion/historique.html", objet=objet, modifications=modifications)
"""

"""

@gestion_bp.route('/stats', methods=['GET'])
@login_required
def stats():
    objet_id = request.args.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    start_date = datetime.utcnow() - timedelta(days=7)

    changements = db.session.query(ObjetHistorique.timestamp, ObjetHistorique.status).filter(
        ObjetHistorique.object_id == objet.id,
        ObjetHistorique.timestamp >= start_date
    ).order_by(ObjetHistorique.timestamp.asc()).all()

    total_time_active = 0
    last_active_time = None

    # ➕ Décalage des timestamps
    changements = [(c.timestamp + timedelta(hours=2), c.status) for c in changements]

    for timestamp, status in changements:
        if status == "active":
            last_active_time = timestamp
        elif status == "inactive" and last_active_time:
            total_time_active += (timestamp - last_active_time).total_seconds()
            last_active_time = None

    return render_template("gestion/stats.html", objet=objet, total_time_active=total_time_active)
"""
@gestion_bp.route('/stats', methods=['GET'])
@login_required
def stats():
    objet_id = request.args.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    start_date = datetime.utcnow() - timedelta(days=7)

    changements = db.session.query(ObjetHistorique.timestamp, ObjetHistorique.status).filter(
        ObjetHistorique.object_id == objet.id,
        ObjetHistorique.timestamp >= start_date,
    ).order_by(ObjetHistorique.timestamp.asc()).all()

    total_time_active = 0
    last_active_time = None

    for action in changements:
        if action.status == "active":
            last_active_time = action.timestamp
        elif action.status == "inactive" and last_active_time:
            total_time_active += (action.timestamp - last_active_time).total_seconds()
            last_active_time = None

    if last_active_time:
        total_time_active += (datetime.utcnow() - last_active_time).total_seconds()

    total_seconds = int(total_time_active)
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_breakdown = {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }

    return render_template("gestion/stats.html", objet=objet, time_breakdown=time_breakdown)


@gestion_bp.route('/rapport', methods=['GET'])
@login_required
def rapport():
    objet_id = request.args.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    start_date = datetime.utcnow() - timedelta(days=7)

    activations = db.session.query(ObjetHistorique.timestamp, ObjetHistorique.status).filter(
        ObjetHistorique.object_id == objet.id,
        ObjetHistorique.timestamp >= start_date
    ).order_by(ObjetHistorique.timestamp.desc()).all()

    activations = [
        type('Obj', (object,), {"timestamp": a.timestamp + timedelta(hours=2), "status": a.status})()
        for a in activations
    ]

    return render_template("gestion/rapport.html", objet=objet, activations=activations)

@gestion_bp.route('/historique', methods=['GET'])
@login_required
def historique():
    objet_id = request.args.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    modifications = db.session.query(ObjetHistorique.timestamp, ObjetHistorique.action, ObjetHistorique.status).filter(
        ObjetHistorique.object_id == objet.id
    ).order_by(ObjetHistorique.timestamp.desc()).all()

    modifications = [
        type('Obj', (object,), {
            "timestamp": m.timestamp + timedelta(hours=2),
            "action": m.action,
            "status": m.status
        })()
        for m in modifications
    ]

    return render_template("gestion/historique.html", objet=objet, modifications=modifications)


################################################ Partie Noam ########################################################################
"""
@gestion_bp.route('/association', methods=['GET','POST'])
def association():  
    
    # Récupération des données
    rooms = Room.query.filter_by(house_id=current_user.house_id).all()
    objects = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()
    
    # Traitement du formulaire (POST)
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        object_id = request.form.get('object_id')
        
        # Validation basique
        if not room_id or not object_id:
            flash("Sélection invalide", 'danger')
        else:
            # Associer l'objet à la pièce (exemple simplifié)
            obj = ConnectedObject.query.get(object_id)
            if obj:
                obj.room_id = room_id
                db.session.commit()
                flash("Association réussie", 'success')

    return render_template('gestion/association.html',
                         rooms=rooms,
                         objects=objects)


@gestion_bp.route('/parametres', methods=['GET', 'POST'])
def parametres():
    # Vérification maison
    if not current_user.house_id:
        flash("Vous n'avez pas de maison associée.", "danger")
        return redirect(url_for('info.home'))

    # Récupère les pièces et objets de l'utilisateur
    pieces = Room.query.filter_by(house_id=current_user.house_id).all()
    objets = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()
    
    if not pieces:
        flash("Aucune pièce disponible.", "warning")

    # Initialisation des variables
    selected_object = None
    selected_room = None
    parametres = []

    if request.method == 'POST':
        # Conversion directe (crash si non-entier)
        object_id = int(request.form['object'])  
        room_id = int(request.form['room'])
        
        # Vérification d'appartenance
        selected_room = Room.query.filter_by(
            id=room_id, 
            house_id=current_user.house_id
        ).first()
        
        selected_object = ConnectedObject.query.filter_by(
            id=object_id, 
            house_id=current_user.house_id
        ).first()

        if selected_object and selected_room:
            parametres = ObjectParametres.query.filter_by(
                object_id=object_id,
                room_id=room_id
            ).all()
            
            if not parametres:
                flash("Aucun paramètre trouvé.", "warning")
        else:
            flash("Objet ou pièce invalide.", "danger")

    return render_template(
        'gestion/parametres.html',
        pieces=pieces,
        objets=objets,
        selected_object=selected_object,
        selected_room=selected_room,
        parametres=parametres
    )

@gestion_bp.route('/traitement_par', methods=['POST'])
def traitement():
    Page de traitement des données des paramètres
    connected_object_id = request.form.get('object')  # Récupérer l'objet
    room_id = request.form.get('room')  # Récupérer la chambre
    donnees = request.form

    # Trouver l'objet connecté sélectionné
    connected_object = ConnectedObject.query.get(connected_object_id)
    room = Room.query.get(room_id)

    # Fonction pour mettre à jour les paramètres de l'objet
    def update_object_param(param_to_update):
        for param, value in param_to_update.items():
            if value:  # Si la valeur est présente
                object_param = ObjectParametres.query.filter_by(object_id=connected_object.id, parametre=param).first()
                if object_param:
                    object_param.value = value
                    db.session.commit()

    # Traitement des paramètres selon l'objet sélectionné
    if connected_object and room:
        if connected_object.room_id == room.id:
            # Traitement du thermostat
            if donnees.get('temperature_t'):
                params_to_update = {
                    'temperature': donnees.get('temperature_t'),
                    'Mode': donnees.get('Mode'),
                    'Horaire_start': donnees.get('Horaire_start'),
                    'Horaire_end': donnees.get('Horaire_end')
                }
                update_object_param(params_to_update)

            # Traitement de l'éclairage
            if donnees.get('Intensitelum'):
                params_to_update = {
                    'Intensitelum': donnees.get('Intensitelum'),
                    'Couleur': donnees.get('Couleur'),
                    'Horaire_Ecl_start': donnees.get('Horaire_Ecl_start'),
                    'Horaire_Ecl_end': donnees.get('Horaire_Ecl_end')
                }
                update_object_param(params_to_update)

            # Traitement de la caméra de surveillance
            if donnees.get('Mode_de_detection_cam'):
                params_to_update = {
                    'Mode_de_detection_cam': donnees.get('Mode_de_detection_cam'),
                    'qual_cam': donnees.get('qual_cam'),
                    'alerte_cam': donnees.get('alerte_cam')
                }
                update_object_param(params_to_update)

            # Traitement du réfrigérateur intelligent
            if donnees.get('temp_congelo'):
                params_to_update = {
                    'temp_congelo': donnees.get('temp_congelo'),
                    'temp_refrigerateur': donnees.get('temp_refrigerateur'),
                    'Mode_economie': donnees.get('Mode_economie')
                }
                update_object_param(params_to_update)

            # Traitement de la serrure connectée
            if donnees.get('Mode_Serrure'):
                params_to_update = {
                    'Mode_Serrure': donnees.get('Mode_Serrure'),
                    'Code_acces': donnees.get('Code_acces'),
                    'Horaire_Serrure_start': donnees.get('Horaire_Serrure_start'),
                    'Horaire_Serrure_end': donnees.get('Horaire_Serrure_end')
                }
                update_object_param(params_to_update)

            # Traitement de l'enceinte intelligente
            if donnees.get('Mode_enceinte'):
                params_to_update = {
                    'Mode_enceinte': donnees.get('Mode_enceinte'),
                    'volume_enceinte': donnees.get('volume_enceinte'),
                    'Horaire_enceinte_start': donnees.get('Horaire_enceinte_start'),
                    'Horaire_enceinte_end': donnees.get('Horaire_enceinte_end')
                }
                update_object_param(params_to_update)

    return redirect(url_for('gestion.parametres'))

"""
