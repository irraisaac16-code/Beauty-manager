#!/usr/bin/env python
"""
Script pour supprimer automatiquement tous les utilisateurs de test sauf admin
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_manager.settings')
django.setup()

from django.contrib.auth.models import User
from manager.models import UserProfile

print("Suppression des utilisateurs de test...")

# Supprimer tous les utilisateurs sauf admin
users_to_delete = User.objects.exclude(username='admin')
count = users_to_delete.count()

print(f"Suppression de {count} utilisateurs...")

for user in users_to_delete:
    print(f"Suppression de {user.username}")
    user.delete()

print("Terminé! Seul l'utilisateur 'admin' reste.") 