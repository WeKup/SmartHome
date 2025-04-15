#!/bin/bash

echo " Mise à jour des paquets..."
sudo apt update

echo " Installation de venv si nécessaire..."
sudo apt install -y python3.12-venv

echo " Création de l'environnement virtuel..."
python3 -m venv venv

echo " Activation de l'environnement virtuel..."
source venv/bin/activate

echo " Mise à jour de pip et installation des packages requis..."
pip install --upgrade pip

# Vérifie si requirements.txt existe
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo " Pas de requirements.txt, installation manuelle des dépendances..."
    pip install flask flask-migrate flask-login flask-sqlalchemy pymysql python-dotenv
fi

echo " Démarrage du service MySQL..."
sudo service mysql start

echo " Création de la base de données 'smart_home_py'..."
mysql -u root -p <<EOF
CREATE DATABASE IF NOT EXISTS smart_home_py CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

echo " Configuration des variables d'environnement..."
export FLASK_APP=app.py
export FLASK_ENV=development
export DB_USERNAME=root
export DB_PASSWORD=cytech0001
export DB_HOST=localhost
export DB_NAME=smart_home_py

echo " Initialisation et migration de la base de données..."
if [ ! -d "migrations" ]; then
    flask db init
fi

flask db migrate -m "Initial migration"
flask db upgrade

echo " Lancement de l'application Flask..."
flask run

