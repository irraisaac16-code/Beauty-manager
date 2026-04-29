#!/usr/bin/env python
"""
Script pour supprimer automatiquement tous les utilisateurs de test sauf admin
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_manager.settings')
django.setup()

from django.contrib.auth.models import User
from manager.models import UserProfile, Role

def delete_test_users():
    print("🧹 Suppression automatique des utilisateurs de test...")
    
    # Récupérer tous les utilisateurs sauf admin
    test_users = User.objects.exclude(username='admin')
    
    if not test_users.exists():
        print("✅ Aucun utilisateur de test trouvé.")
        return
    
    print(f"📋 {test_users.count()} utilisateurs de test trouvés:")
    for user in test_users:
        try:
            profile = user.userprofile
            role_name = profile.role.name if profile.role else "Pas de rôle"
        except UserProfile.DoesNotExist:
            role_name = "Pas de profil"
        print(f"   - {user.username} ({user.email}) - Rôle: {role_name}")
    
    print("\n🗑️ Suppression automatique en cours...")
    deleted_count = 0
    
    for user in test_users:
        try:
            username = user.username
            user.delete()
            print(f"   ✅ {username} supprimé")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Erreur lors de la suppression de {user.username}: {e}")
    
    print(f"\n✅ Nettoyage terminé! {deleted_count} utilisateurs supprimés.")
    print("✅ Seul l'utilisateur 'admin' a été conservé.")

if __name__ == '__main__':
    delete_test_users() 