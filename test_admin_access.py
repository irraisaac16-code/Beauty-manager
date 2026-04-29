#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_manager.settings')
django.setup()

from django.contrib.auth.models import User
from manager.models import UserProfile, Role
from manager.views import is_admin

def test_admin_access():
    """Test l'accès admin et diagnostique les problèmes"""
    
    print("🔍 Diagnostic de l'accès admin...")
    
    # 1. Vérifier l'utilisateur admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Utilisateur admin trouvé: {admin_user.username}")
        print(f"   ID: {admin_user.id}")
        print(f"   Active: {admin_user.is_active}")
        print(f"   Email: {admin_user.email}")
    except User.DoesNotExist:
        print("❌ Utilisateur admin non trouvé !")
        return
    
    # 2. Vérifier le profil admin
    try:
        admin_profile = admin_user.userprofile
        print(f"✅ Profil admin trouvé")
        print(f"   Rôle: {admin_profile.role.name}")
        print(f"   Téléphone: {admin_profile.phone}")
    except UserProfile.DoesNotExist:
        print("❌ Profil admin non trouvé !")
        return
    
    # 3. Tester la fonction is_admin
    is_admin_result = is_admin(admin_user)
    print(f"✅ Test is_admin(): {is_admin_result}")
    
    # 4. Vérifier le rôle admin
    try:
        admin_role = Role.objects.get(name='admin')
        print(f"✅ Rôle admin trouvé (ID: {admin_role.id})")
        
        # Vérifier si le profil a le bon rôle
        if admin_profile.role == admin_role:
            print(f"✅ Le profil admin a le bon rôle")
        else:
            print(f"❌ Le profil admin a le mauvais rôle: {admin_profile.role.name}")
            print(f"   Correction en cours...")
            admin_profile.role = admin_role
            admin_profile.save()
            print(f"   ✅ Rôle corrigé !")
            
    except Role.DoesNotExist:
        print("❌ Rôle admin non trouvé !")
        return
    
    # 5. Tester le décorateur role_required
    print(f"\n🎯 Test du décorateur role_required...")
    
    # Importer la fonction role_required
    from manager.views import role_required
    
    # Créer une fonction de test
    def test_view(request):
        return "Test OK"
    
    # Appliquer le décorateur
    decorated_view = role_required('admin')(test_view)
    
    print(f"✅ Décorateur role_required appliqué")
    
    # 6. Vérifier les URLs
    print(f"\n🔗 Vérification des URLs...")
    
    try:
        from django.urls import reverse
        validation_url = reverse('validation_coiffeuses')
        print(f"✅ URL validation_coiffeuses: {validation_url}")
    except Exception as e:
        print(f"❌ Erreur URL: {e}")
    
    print(f"\n✅ Diagnostic terminé !")
    print(f"🎯 Essayez maintenant de vous connecter avec:")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   Puis allez sur: http://127.0.0.1:8000/validation-coiffeuses/")

if __name__ == '__main__':
    test_admin_access() 