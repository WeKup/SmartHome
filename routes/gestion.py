from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models.auth import db, User, House, ConnectedObject, Room, ObjectType, ObjetHistorique,ObjectParametres, ConnectedObject, Association, Rapport, ObjectAction,DefaultObjectParametre
import os
import time
import json
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
    return render_template('gestion/add.html', user=current_user,listeRoom=liste_salle)


@gestion_bp.route('/added', methods=["POST"])
@login_required
def added():
    nomObj = request.form.get("nomObj")
    salleObj = request.form.get("salleObj")
    brandObj = request.form.get("brandObj")
    modeleObj = request.form.get("modeleObj")
    descriptionObj = request.form.get("descriptionObj")
    conso_min = int(request.form.get("conso_min", 0))
    conso_max = int(request.form.get("conso_max", 100))

    max_id = db.session.query(func.max(ConnectedObject.id)).scalar() or 0
    new_id = max_id + 1

    Objet = ConnectedObject(
        id=new_id,
        name=nomObj + " " + salleObj,
        object_type_id=new_id,
        room_id=get_room_id_by_name(salleObj),
        description=descriptionObj,
        brand=brandObj,
        model=modeleObj,
        house_id=current_user.house_id,
        conso_min=conso_min,
        conso_max=conso_max,
        status="active"
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

    flash("Objet ajouté avec succès", "success")
    return render_template('gestion/add.html', user=current_user)


   
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

@gestion_bp.route('/modified', methods=["POST", "GET"])
@login_required
def modified():
    objet_id = request.form.get("objet_id")
    objet = ConnectedObject.query.get_or_404(objet_id)
    rooms = Room.query.filter_by(house_id=current_user.house_id).all()  #  On récupère les salles
    return render_template('gestion/modified.html', obj=objet, rooms=rooms)


@gestion_bp.route('/modifiedObj', methods=["POST", "GET"])
@login_required
def modifiedObj():
    objet_id = request.form.get("Id")
    objet = ConnectedObject.query.get_or_404(objet_id)

    if objet.house_id != current_user.house_id:
        flash("Vous n'avez pas l'autorisation de modifier cet objet.", "danger")
        return redirect(url_for("connected.accueil"))

    # Anciennes valeurs
    old_name = objet.name
    old_description = objet.description
    old_status = objet.status
    old_brand = objet.brand
    old_model = objet.model
    old_conso_min = objet.conso_min
    old_conso_max = objet.conso_max
    old_room_id = objet.room_id

    # Nouvelles valeurs
    new_room_id = int(request.form.get("room_id"))
    salle = Room.query.get(new_room_id)
    nom_base = request.form.get("name").split(" ")[0]  # Extrait la base du nom (ex: "Thermostat")

    objet.name = nom_base + " " + salle.name  # Reconstruit le nom complet
    objet.description = request.form.get("description")
    objet.status = request.form.get("status")
    objet.brand = request.form.get("brand")
    objet.model = request.form.get("model")
    objet.conso_min = int(request.form.get("conso_min", 0))
    objet.conso_max = int(request.form.get("conso_max", 100))
    objet.room_id = new_room_id

    # Historique
    changes = []
    if old_name != objet.name:
        changes.append(f"Nom changé de '{old_name}' à '{objet.name}'")
    if old_room_id != new_room_id:
        old_room = Room.query.get(old_room_id)
        changes.append(f"Salle changée de '{old_room.name}' à '{salle.name}'")
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



@gestion_bp.route('/parametres', methods=['GET', 'POST'])
def parametres():
    if not current_user.house_id:
        flash("Vous devez avoir une maison associée", "warning")
        return redirect(url_for('auth.profile'))

    room_for_object = Room.query.filter_by(house_id=current_user.house_id).all()

    selected_room = None
    selected_object = None
    parametres = []
    objects = []

    if request.method == 'POST':
        room_id = request.form.get('room')
        object_id = request.form.get('object')

        if room_id:
            selected_room = Room.query.get(room_id)
            if selected_room:
                objects = db.session.query(ConnectedObject).join(Association).filter(Association.room_id == room_id).all()

        if object_id:
            selected_object = ConnectedObject.query.get(object_id)
            if selected_object and selected_room:
                # Vérifie si l'utilisateur a déjà des paramètres personnalisés
                existing_user_params = ObjectParametres.query.filter_by(
                    object_id=object_id,
                    room_id=room_id,
                    user_id=current_user.id
                ).all()

                # Si aucun paramètre utilisateur, injecter les valeurs par défaut
                if not existing_user_params:
                    default_params = DefaultObjectParametre.query.filter_by(type_id=selected_object.object_type_id).all()
                    for d in default_params:
                        new_param = ObjectParametres(
                            object_id=selected_object.id,
                            room_id=selected_room.id,
                            user_id=current_user.id,
                            parametre=d.parametre,
                            value=d.default_value
                        )
                        db.session.add(new_param)
                    db.session.commit()

                # Recharger tous les paramètres (y compris ceux nouvellement ajoutés)
                all_param_names = db.session.query(ObjectParametres.parametre).filter_by(
                    object_id=object_id,
                    room_id=room_id
                ).distinct().all()

                param_names = [p[0] for p in all_param_names]
                parametres = []
                for name in param_names:
                    user_param = ObjectParametres.query.filter_by(
                        object_id=object_id,
                        room_id=room_id,
                        parametre=name,
                        user_id=current_user.id
                    ).first()

                    if user_param:
                        parametres.append(user_param)
                    else:
                        default_param = ObjectParametres.query.filter_by(
                            object_id=object_id,
                            room_id=room_id,
                            parametre=name
                        ).first()
                        parametres.append(default_param)

                for p in parametres:
                    print(f"Paramètre trouvé : {p.parametre}, valeur={p.value}, user_id={p.user_id}")

                print("Object ID:", object_id)
                print("Room ID:", room_id)


            # Injecter des paramètres par défaut s'il n'y en a aucun pour cet utilisateur
            if selected_object and selected_room and not parametres:
                default_params = DefaultObjectParametre.query.filter_by(type_id=selected_object.object_type_id).all()
                for d in default_params:
                    new_param = ObjectParametres(
                        object_id=selected_object.id,
                        room_id=selected_room.id,
                        user_id=current_user.id,
                        parametre=d.parametre,
                        value=d.default_value
                    )
                    db.session.add(new_param)
                    parametres.append(new_param)
                db.session.commit()


    return render_template('gestion/parametres.html',
                           room_for_object=room_for_object,
                           objects=objects,
                           selected_room=selected_room,
                           selected_object=selected_object,
                           parametres=parametres)





@gestion_bp.route('/traitement', methods=['POST'])
def traitement():
    object_id = request.form.get('object')
    room_id = request.form.get('room')

    if not all([object_id, room_id]):
        flash("Données manquantes", "error")
        return redirect(url_for('gestion.parametres'))

    # Traiter les paramètres envoyés dans le formulaire
    for key, value in request.form.items():
        if key not in ['object', 'room', 'csrf_token']:
            # Vérifier si le paramètre existe déjà pour cet objet et cette pièce
            param = ObjectParametres.query.filter_by(
                object_id=object_id,
                room_id=room_id,
                user_id=current_user.id,
                parametre=key
            ).first()

            if param:
                param.value = value  # Mettre à jour la valeur existante
            else:
                # Ajouter un nouveau paramètre si il n'existe pas
                new_param = ObjectParametres(
                    object_id=object_id,
                    room_id=room_id,
                    user_id=current_user.id,
                    parametre=key,
                    value=value
                )
                db.session.add(new_param)

    try:
        db.session.commit()
        flash("Paramètres mis à jour avec succès", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la mise à jour : {str(e)}", "error")

    return redirect(url_for('gestion.parametres'))




@gestion_bp.route('/association', methods=['GET', 'POST'])
def association():
    if not current_user.house_id:
        flash("Vous devez avoir une maison associée", "warning")
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        object_id = request.form.get('object')
        room_id = request.form.get('room')
        action = request.form.get('action')

        if not all([object_id, room_id, action]):
            flash("Données manquantes", "error")
            return redirect(url_for('gestion.association'))

        assoc = Association.query.filter_by(
            object_id=object_id,
            room_id=room_id
        ).first()

        try:
            if action == 'add' and not assoc:
                new_assoc = Association(object_id=object_id, room_id=room_id)
                db.session.add(new_assoc)
                flash("Association créée avec succès", "success")
            elif action == 'remove' and assoc:
                db.session.delete(assoc)
                flash("Association supprimée avec succès", "success")
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {str(e)}", "error")

    # Récupération des données pour l'affichage
    objects = ConnectedObject.query.filter_by(house_id=current_user.house_id).all()
    rooms = Room.query.filter_by(house_id=current_user.house_id).all()
    associations = Association.query.join(
        ConnectedObject, ConnectedObject.id == Association.object_id
    ).filter(
        ConnectedObject.house_id == current_user.house_id
    ).all()

    return render_template('gestion/association.html',
                         objects=objects,
                         rooms=rooms,
                         associations=associations)

@gestion_bp.route('/rapports', methods=['GET', 'POST'])
@login_required
def rapports():
    rooms = Room.query.filter_by(house_id=current_user.house_id).all()
    selected_room_id = request.args.get('room_id') or request.form.get('room_id')
    connected_objects = []

    if selected_room_id:
        connected_objects = ConnectedObject.query.filter_by(room_id=selected_room_id).all()

    if request.method == 'POST':
        connected_object_id = request.form.get('connected_object_id')
        contenu = request.form.get('contenu')

        if not connected_object_id or not contenu:
            flash("Tous les champs sont requis", "error")
            return redirect(url_for('gestion.rapports', room_id=selected_room_id))

        connected_object = ConnectedObject.query.get_or_404(connected_object_id)
        if connected_object.house_id != current_user.house_id:
            flash("Accès non autorisé", "error")
            return redirect(url_for('gestion.rapports'))

        rapport = Rapport(
            object_id=connected_object_id,
            house_id=connected_object.house_id,
            contenu=contenu,
            date_creation=datetime.utcnow()
        )

        try:
            db.session.add(rapport)
            db.session.commit()
            flash("Rapport généré avec succès", "success")
            return redirect(url_for('gestion.rapports', room_id=selected_room_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la génération du rapport : {str(e)}", "error")

    # Charger tous les rapports liés à la maison
    rapports = Rapport.query.join(ConnectedObject).filter(
        ConnectedObject.house_id == current_user.house_id
    ).order_by(Rapport.date_creation.desc()).all()

    return render_template(
        'gestion/rapports.html',
        rooms=rooms,
        connected_objects=connected_objects,
        rapports=rapports,
        selected_room_id=selected_room_id
    )

