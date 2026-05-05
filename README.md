# Beautix

Application web de gestion de salon de beaute developpee avec Django.

## Apercu

Beautix est une application de gestion pour salon de beaute qui permet de centraliser:
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


### 5) CrÃ©er et activer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

### 6) Installer les dÃ©pendances

```bash
pip install -r requirements.txt
```

### 7) Configurer la base de donnÃ©es

```bash
python manage.py migrate
python manage.py setup_data  # CrÃ©er les donnÃ©es de base
```

**Isaac (irraisaac16-code)**  
GitHub: https://github.com/irraisaac16-code

## Licence

Projet distribue sous licence MIT (voir `LICENSE`).

