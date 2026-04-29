#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_manager.settings')
django.setup()

from django.contrib.auth.models import User
from manager.models import Role, UserProfile

def create_test_users():
    """Crée des utilisateurs de test pour tous les rôles"""
    
    print("🔧 Création des utilisateurs de test...")
    
    # Créer les rôles s'ils n'existent pas
    roles = ['admin', 'coiffeuse', 'client']
    for role_name in roles:
        role, created = Role.objects.get_or_create(name=role_name)
        if created:
            print(f"✅ Rôle '{role_name}' créé")
        else:
            print(f"ℹ️  Rôle '{role_name}' existe déjà")
    
    # Créer un utilisateur admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Utilisateur admin créé")
    else:
        print("ℹ️  Utilisateur admin existe déjà")
    
    # Créer le profil admin
    admin_role = Role.objects.get(name='admin')
    admin_profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'role': admin_role,
            'phone': '0123456789'
        }
    )
    if created:
        print("✅ Profil admin créé")
    else:
        print("ℹ️  Profil admin existe déjà")
    
    # Créer un utilisateur coiffeuse
    coiffeuse_user, created = User.objects.get_or_create(
        username='coiffeuse',
        defaults={
            'email': 'coiffeuse@example.com',
            'is_active': True
        }
    )
    
    if created:
        coiffeuse_user.set_password('coiffeuse123')
        coiffeuse_user.save()
        print("✅ Utilisateur coiffeuse créé")
    else:
        print("ℹ️  Utilisateur coiffeuse existe déjà")
    
    # Créer le profil coiffeuse
    coiffeuse_role = Role.objects.get(name='coiffeuse')
    coiffeuse_profile, created = UserProfile.objects.get_or_create(
        user=coiffeuse_user,
        defaults={
            'role': coiffeuse_role,
            'phone': '0987654321'
        }
    )
    if created:
        print("✅ Profil coiffeuse créé")
    else:
        print("ℹ️  Profil coiffeuse existe déjà")
    
    # Créer un utilisateur client
    client_user, created = User.objects.get_or_create(
        username='client',
        defaults={
            'email': 'client@example.com',
            'is_active': True
        }
    )
    
    if created:
        client_user.set_password('client123')
        client_user.save()
        print("✅ Utilisateur client créé")
    else:
        print("ℹ️  Utilisateur client existe déjà")
    
    # Créer le profil client
    client_role = Role.objects.get(name='client')
    client_profile, created = UserProfile.objects.get_or_create(
        user=client_user,
        defaults={
            'role': client_role,
            'phone': '0555666777'
        }
    )
    if created:
        print("✅ Profil client créé")
    else:
        print("ℹ️  Profil client existe déjà")
    
    print("\n🎯 Utilisateurs de test créés avec succès !")
    print("\n📋 Informations de connexion :")
    print("=" * 50)
    print("👑 ADMIN :")
    print("   Username: admin")
    print("   Password: admin123")
    print("   URL: http://127.0.0.1:8000/dashboard/admin/")
    print()
    print("💇‍♀️ COIFFEUSE :")
    print("   Username: coiffeuse")
    print("   Password: coiffeuse123")
    print("   URL: http://127.0.0.1:8000/dashboard/coiffeuse/")
    print()
    print("👤 CLIENT :")
    print("   Username: client")
    print("   Password: client123")
    print("   URL: http://127.0.0.1:8000/dashboard/client/")
    print("=" * 50)
    
    # Vérifier les utilisateurs existants
    print("\n📊 Utilisateurs existants dans la base :")
    for user in User.objects.all():
        try:
            profile = user.userprofile
            print(f"   - {user.username} (rôle: {profile.role.name}, actif: {user.is_active})")
        except UserProfile.DoesNotExist:
            print(f"   - {user.username} (pas de profil, actif: {user.is_active})")

if __name__ == '__main__':
    create_test_users() 