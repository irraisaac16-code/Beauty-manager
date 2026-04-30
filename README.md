# Beauty Manager

Application web de gestion de salon de beaute developpee avec Django.

## Apercu

Beauty Manager est une application de gestion pour salon de beaute qui permet de centraliser:
- la gestion des reservations,
- la gestion des profils utilisateurs (admin, coiffeuse, client),
- le suivi des services et des disponibilites,
- les tableaux de bord metier.

Ce projet met en avant ma capacite a concevoir une application web complete avec un back-end Django, des templates dynamiques et une logique metier orientee usage reel.

## Fonctionnalites principales

- Authentification et gestion des roles utilisateurs.
- Espace administrateur avec tableau de bord.
- Gestion des reservations (creation, suivi, annulation).
- Gestion des services proposes par le salon.
- Pages et vues dediees par type d'utilisateur.
- Notifications et emails de confirmation.

## Stack technique

- **Back-end**: Python, Django
- **Base de donnees**: SQLite (dev)
- **Front-end**: HTML, CSS, templates Django
- **Autres outils**: JavaScript, Tailwind (selon configuration)

## Structure du projet

- `beauty_manager/`: configuration principale Django (settings, urls, wsgi, asgi)
- `manager/`: application metier (models, views, forms, templates, urls)
- `manage.py`: point d'entree Django

## Installation locale

### 1) Cloner le projet

```bash
git clone https://github.com/irraisaac16-code/Beauty-manager.git
cd Beauty-manager
```

### 2) Creer et activer un environnement virtuel

Sous Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Installer les dependances minimales

```bash
pip install django django-tailwind pillow
```

### 4) Lancer le serveur

```bash
python manage.py runserver
```

Puis ouvrir: `http://127.0.0.1:8000`

## Déploiement sur PythonAnywhere

### 1) Créer un compte gratuit sur [PythonAnywhere](https://www.pythonanywhere.com/)

### 2) Cloner le projet dans PythonAnywhere

Dans la console Bash de PythonAnywhere :
```bash
git clone https://github.com/irraisaac16-code/Beauty-manager.git
cd Beauty-manager
```

### 3) Créer et activer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4) Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5) Configurer la base de données

```bash
python manage.py migrate
python manage.py setup_data  # Créer les données de base
```

### 6) Créer un superuser (optionnel pour les tests)

```bash
python manage.py createsuperuser
```

### 7) Configurer le fichier WSGI

Dans PythonAnywhere, allez dans l'onglet "Web" :
- Source code : `/home/votre_username/Beauty-manager`
- Working directory : `/home/votre_username/Beauty-manager`
- WSGI configuration file : Créez `/var/www/votre_username_pythonanywhere_com_wsgi.py`

Contenu du fichier WSGI :
```python
import os
import sys

# Ajouter le chemin du projet
path = '/home/votre_username/Beauty-manager'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'beauty_manager.settings'

# Activer l'environnement virtuel
activate_this = '/home/votre_username/Beauty-manager/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import django
django.setup()

from beauty_manager.wsgi import application
```

### 8) Configurer les variables d'environnement (optionnel)

Dans PythonAnywhere, allez dans "Account" > "API token" et définissez :
- `SECRET_KEY` : Une clé secrète
- `DEBUG` : `False`
- `ALLOWED_HOSTS` : `votre_username.pythonanywhere.com`

### 9) Redémarrer l'application

Dans l'onglet "Web", cliquez sur "Reload".

Votre application sera accessible à : `https://votre_username.pythonanywhere.com`

## Donnees de demonstration

Des scripts utilitaires sont disponibles a la racine (`create_test_users.py`, `check_admin_role.py`, etc.) pour creer/verifier des utilisateurs de test selon les besoins de demonstration.

## Points forts du projet

- Architecture Django claire et evolutive.
- Bonne separation des responsabilites (models, views, templates).
- Cas d'usage metier concret et presentable en entretien.
- Base solide pour evoluer vers une version production (PostgreSQL, Docker, CI/CD, tests et monitoring).

## Axes d'amelioration (roadmap)

- Ajouter une suite de tests automatises plus complete.
- Dockeriser l'application.
- Ajouter une API REST (Django REST Framework).
- Mettre en place un pipeline CI/CD.
- Ajouter une page de demo publique avec captures et parcours utilisateur.

## Auteur

**Isaac (irraisaac16-code)**  
GitHub: https://github.com/irraisaac16-code

## Licence

Projet distribue sous licence MIT (voir `LICENSE`).
