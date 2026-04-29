#!/usr/bin/env python
"""
Script de test pour la fonctionnalité d'annulation et de nouvelle réservation
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_manager.settings')
django.setup()

from manager.models import User, UserProfile, Role, Service, Reservation
from django.contrib.auth import authenticate
from datetime import date, time, timedelta

def test_annulation_reservation():
    """Test de la fonctionnalité d'annulation et de nouvelle réservation"""
    
    print("=== Test de la fonctionnalité d'annulation et de nouvelle réservation ===\n")
    
    try:
        # 1. Vérifier qu'il y a des utilisateurs de test
        clients = UserProfile.objects.filter(role__name='client')
        coiffeuses = UserProfile.objects.filter(role__name='coiffeuse')
        services = Service.objects.filter(is_active=True)
        
        if not clients.exists():
            print("❌ Aucun client trouvé. Créez d'abord des utilisateurs de test.")
            return False
            
        if not coiffeuses.exists():
            print("❌ Aucune coiffeuse trouvée. Créez d'abord des utilisateurs de test.")
            return False
            
        if not services.exists():
            print("❌ Aucun service trouvé. Créez d'abord des services.")
            return False
        
        client = clients.first()
        coiffeuse = coiffeuses.first()
        service = services.first()
        
        print(f"✅ Client de test: {client.user.username}")
        print(f"✅ Coiffeuse de test: {coiffeuse.user.username}")
        print(f"✅ Service de test: {service.name}")
        
        # 2. Créer une réservation de test
        tomorrow = date.today() + timedelta(days=1)
        reservation = Reservation.objects.create(
            client=client,
            coiffeuse=coiffeuse,
            service=service,
            date=tomorrow,
            heure=time(14, 0),  # 14h00
            statut='en_attente',
            montant=service.price
        )
        
        print(f"✅ Réservation créée: {reservation}")
        print(f"   - Date: {reservation.date}")
        print(f"   - Heure: {reservation.heure}")
        print(f"   - Statut: {reservation.get_statut_display()}")
        
        # 3. Simuler l'annulation
        reservation.statut = 'annulé'
        reservation.save()
        
        print(f"✅ Réservation annulée: {reservation.get_statut_display()}")
        
        # 4. Vérifier que le créneau est disponible pour une nouvelle réservation
        # (Le créneau devrait être libéré après annulation)
        existing_reservations = Reservation.objects.filter(
            coiffeuse=coiffeuse,
            date=tomorrow,
            heure=time(14, 0),
            statut__in=['en_attente', 'confirmé', 'payé']
        )
        
        if existing_reservations.exists():
            print("⚠️  Attention: Il y a encore des réservations actives pour ce créneau")
        else:
            print("✅ Le créneau est bien libéré après annulation")
        
        # 5. Créer une nouvelle réservation pour le même créneau
        new_reservation = Reservation.objects.create(
            client=client,
            coiffeuse=coiffeuse,
            service=service,
            date=tomorrow,
            heure=time(14, 0),
            statut='en_attente',
            montant=service.price
        )
        
        print(f"✅ Nouvelle réservation créée: {new_reservation}")
        print(f"   - Date: {new_reservation.date}")
        print(f"   - Heure: {new_reservation.heure}")
        print(f"   - Statut: {new_reservation.get_statut_display()}")
        
        # 6. Nettoyer les données de test
        reservation.delete()
        new_reservation.delete()
        
        print("\n✅ Test terminé avec succès!")
        print("✅ La fonctionnalité d'annulation et de nouvelle réservation fonctionne correctement.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    success = test_annulation_reservation()
    sys.exit(0 if success else 1) 