from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from manager.models import Role, UserProfile, Service

class Command(BaseCommand):
    help = 'Initialise les données de base pour Beauty Manager'

    def handle(self, *args, **options):
        self.stdout.write('Initialisation des données de base...')
        
        # Créer les rôles
        roles_data = [
            {'name': 'admin'},
            {'name': 'coiffeuse'},
            {'name': 'client'},
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(**role_data)
            if created:
                self.stdout.write(f'Rôle créé: {role.name}')
            else:
                self.stdout.write(f'Rôle existant: {role.name}')
        
        # Créer les services
        services_data = [
            {
                'name': 'Coupe et Brushing',
                'description': 'Coupe de cheveux personnalisée avec brushing professionnel',
                'price': 25.00,
                'duration': 60,
            },
            {
                'name': 'Coloration',
                'description': 'Coloration complète avec produits professionnels',
                'price': 45.00,
                'duration': 90,
            },
            {
                'name': 'Mèches',
                'description': 'Pose de mèches pour un effet naturel',
                'price': 35.00,
                'duration': 75,
            },
            {
                'name': 'Lissage',
                'description': 'Lissage professionnel pour cheveux rebelles',
                'price': 55.00,
                'duration': 120,
            },
            {
                'name': 'Tresses Africaines',
                'description': 'Tresses traditionnelles africaines',
                'price': 30.00,
                'duration': 90,
            },
            {
                'name': 'Manucure',
                'description': 'Soin complet des mains et pose de vernis',
                'price': 20.00,
                'duration': 45,
            },
            {
                'name': 'Pédicure',
                'description': 'Soin complet des pieds et pose de vernis',
                'price': 25.00,
                'duration': 60,
            },
            {
                'name': 'Soin du Visage',
                'description': 'Soin hydratant et rajeunissant du visage',
                'price': 40.00,
                'duration': 60,
            },
        ]
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'Service créé: {service.name} - {service.price}€')
            else:
                self.stdout.write(f'Service existant: {service.name}')
        
        # Créer un identifiant admin de test pour les démonstrations
        admin_role = Role.objects.get(name='admin')
        admin_test_user, created = User.objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin_test@beauty-manager.local',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_test_user.set_password('AdminTest123!')
            admin_test_user.save()
            self.stdout.write('Utilisateur admin_test créé')
        else:
            self.stdout.write('Utilisateur admin_test existant')
            # Garantit que le compte de test reste pleinement administrateur
            has_changed = False
            if not admin_test_user.is_active:
                admin_test_user.is_active = True
                has_changed = True
            if not admin_test_user.is_staff:
                admin_test_user.is_staff = True
                has_changed = True
            if not admin_test_user.is_superuser:
                admin_test_user.is_superuser = True
                has_changed = True
            if has_changed:
                admin_test_user.save()
                self.stdout.write('Privilèges admin_test synchronisés')

        admin_test_profile, created = UserProfile.objects.get_or_create(
            user=admin_test_user,
            defaults={'role': admin_role, 'phone': ''}
        )
        if not created and admin_test_profile.role != admin_role:
            admin_test_profile.role = admin_role
            admin_test_profile.save(update_fields=['role'])
        self.stdout.write('Profil admin_test prêt')
        self.stdout.write("Identifiant de test admin: username='admin_test' / password='AdminTest123!'")
        
        self.stdout.write(self.style.SUCCESS('Initialisation terminée avec succès!')) 