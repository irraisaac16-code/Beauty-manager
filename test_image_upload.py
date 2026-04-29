#!/usr/bin/env python
import os
import sys
import django
from django.core.files import File
import uuid

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_manager.settings')
django.setup()

from django.contrib.auth.models import User
from manager.models import UserProfile, Role

def create_test_coiffeuse_with_image():
    """Crée une coiffeuse de test avec une image de profil"""

    try:
        # Générer un nom d'utilisateur unique
        unique_username = f'test_coiffeuse_{uuid.uuid4().hex[:8]}'
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=unique_username,
            email=f'{unique_username}@example.com',
            password='testpass123',
            is_active=False
        )

        # Créer le profil
        role = Role.objects.get(name='coiffeuse')
        profile = UserProfile.objects.create(
            user=user,
            role=role,
            phone='0123456789'
        )

        # Créer un fichier image de test
        test_image_path = 'test_image.jpg'
        
        # Créer un fichier image simple (format JPEG minimal)
        with open(test_image_path, 'wb') as f:
            # En-tête JPEG minimal
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')

        # Attacher l'image au profil
        with open(test_image_path, 'rb') as f:
            profile.profile_image.save('test_image.jpg', File(f), save=True)

        # Nettoyer le fichier temporaire
        os.unlink(test_image_path)

        print(f"✅ Coiffeuse de test créée : {user.username}")
        print(f"📸 Image de profil : {profile.profile_image.url}")
        print(f"📁 Chemin physique : {profile.profile_image.path}")

        return profile

    except Exception as e:
        print(f"❌ Erreur : {e}")
        return None

if __name__ == '__main__':
    create_test_coiffeuse_with_image() 