#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_manager.settings')
django.setup()

from django.contrib.auth.models import User
from manager.models import UserProfile, Role

def check_and_fix_admin_roles():
    """Vérifie et corrige les rôles des utilisateurs admin"""
    
    print("🔍 Vérification des rôles utilisateurs...")
    
    # Vérifier si le rôle admin existe
    try:
        admin_role = Role.objects.get(name='admin')
        print(f"✅ Rôle 'admin' trouvé (ID: {admin_role.id})")
    except Role.DoesNotExist:
        print("❌ Rôle 'admin' non trouvé !")
        return
    
    # Lister tous les utilisateurs
    users = User.objects.all()
    print(f"\n📋 Utilisateurs trouvés ({users.count()}):")
    
    for user in users:
        print(f"  - {user.username} (ID: {user.id}, Active: {user.is_active})")
        
        # Vérifier le profil utilisateur
        try:
            profile = user.userprofile
            print(f"    Profil: rôle='{profile.role.name}', téléphone='{profile.phone}'")
        except UserProfile.DoesNotExist:
            print(f"    ❌ Pas de profil utilisateur !")
            
            # Créer le profil si c'est l'admin
            if user.username == 'admin':
                print(f"    🔧 Création du profil admin...")
                UserProfile.objects.create(
                    user=user,
                    role=admin_role,
                    phone='+225 0000000000'
                )
                print(f"    ✅ Profil admin créé !")
    
    # Vérifier spécifiquement l'admin
    try:
        admin_user = User.objects.get(username='admin')
        admin_profile = admin_user.userprofile
        
        if admin_profile.role.name == 'admin':
            print(f"\n✅ L'utilisateur admin a le bon rôle !")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Active: {admin_user.is_active}")
            print(f"   Rôle: {admin_profile.role.name}")
            print(f"   Téléphone: {admin_profile.phone}")
        else:
            print(f"\n❌ L'utilisateur admin a le mauvais rôle: {admin_profile.role.name}")
            print(f"   Correction du rôle...")
            admin_profile.role = admin_role
            admin_profile.save()
            print(f"   ✅ Rôle corrigé !")
            
    except User.DoesNotExist:
        print(f"\n❌ Utilisateur 'admin' non trouvé !")
    except UserProfile.DoesNotExist:
        print(f"\n❌ Profil utilisateur 'admin' non trouvé !")
    
    print(f"\n🎯 Test de la fonction is_admin...")
    
    # Importer la fonction is_admin
    from manager.views import is_admin
    
    for user in users:
        is_admin_result = is_admin(user)
        print(f"  {user.username}: is_admin() = {is_admin_result}")
    
    print(f"\n✅ Vérification terminée !")

if __name__ == '__main__':
    check_and_fix_admin_roles() 