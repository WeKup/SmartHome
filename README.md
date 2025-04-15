# 🏠 Smart-Home




## Auteurs

- [@WeKup](https://www.github.com/WeKup)

- [@jawhrz ](https://www.github.com/jawhrz)

- [@nonooow ](https://www.github.com/nonooow)


## 🚀 Fonctionnalités principales

- **Tableau de bord** : Visualisez et contrôlez tous vos appareils depuis une interface intuitive  
- **Gestion des objets connectés** : Ajoutez, modifiez et suivez l'état de vos différents appareils  
- **Types de consommation multiples** : Suivez la consommation électrique, d'eau, de gaz et autres  
- **Statistiques détaillées** : Analysez votre consommation avec des graphiques interactifs  
- **Gestion des utilisateurs** : Partagez l'accès à votre maison avec différents niveaux de permission  
- **Système d'invitation flexible** : Par email ou par approbation manuelle  
- **Mode sombre** : Interface adaptable pour un confort visuel optimal  
- **Export PDF** : Générez des rapports complets sur vos consommations  

---

## 🛠️ Technologies utilisées

- **Backend** : Python, Flask, SQLAlchemy  
- **Frontend** : HTML, CSS, JavaScript, Bootstrap  
- **Base de données** : MySQL  
- **Visualisation** : Matplotlib  
- **PDF** : WeasyPrint  

---

## ⚙️ Installation

### Prérequis

- Python 3.8 ou supérieur  
- WampServer (Windows) ou équivalent LAMP (Linux)  
- Environnement GTK (Windows uniquement)

---

### 💻 Installation sur Windows

#### 1. Préparer la base de données

- Lancez **WampServer**
- Créez une base de données nommée `smart_home_py`

#### 2. Installer GTK

- Téléchargez et installez **GTK Runtime** sur github
- Ajoutez le dossier d’installation à votre variable d’environnement `PATH`

#### 3. Installations des dépendances

- Ouvrez un terminal dans le dossier du projet une fois telechargé
- Installez les dépendances : pip install -r requirements.txt
- Activez l'environnement virtuel : venv\scripts\activate
- Modifiez le fichier config.py pour indiquer le mot de passe de votre base de données si nécessaire ( par default il est vide )


### 4.Initialiser la base de données
- une fois cela fait, veuillez:
- réaliser la commande flask db upgrade directement car le fichier migrations existe déjà.

( si il y'a une erreur alors réalisez la commande flask db init, puis flask db migrate et enfin flask db upgrade)

avec tout cela votre base de données a reçu toute les informations necessaire
### 5. Lancer l'application:
- flask run
- l'application est lancer au http://127.0.0.1:5000

---
---
### 💻 Installation sur Linux

### 1 installation automatisé
- installez le dossier puis ouvrez un terminal à l'intérieur
- une fois fait, faite chmod+x setup.sh
- puis lancer le scripts automatisé, il va vous installez toutes les dépendances nécessaire et vous crée votre base de donnée, pour cela faites : ./setup.sh
- Si un mot de passe est demandé pour installer des paquets, utilisez votre mot de passe système
- Si un mot de passe est demandé pour la base de données, utilisez le mot de passe de votre serveur MySQL
- ensuite le serveur est lancé automatiquement sur http://127.0.0.1:5000

### 2 Lancement manuel après installation
après avoir utilisé le site comme ça, si vous souhaitez le lancez manuellement:
- Modifiez config.py pour mettre à jour le mot de passe de la base de données si nécessaire
- Activez l'environnement virtuel : source venv/bin/activate
- Lancez l'application : flask run ou python3 app.py
- puis le serveur est lancé au http://127.0.0.1:5000

---
---


