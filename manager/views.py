from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.conf import settings as django_settings
from datetime import datetime, timedelta
import logging
import locale
from .models import Role, UserProfile, Service, Reservation
from .forms import SecureUserRegistrationForm, SecureReservationForm, SecureServiceForm, AnnulationForm
from .notifications import NotificationService

# Configuration du logging
logger = logging.getLogger(__name__)

def is_admin(user):
    try:
        return user.userprofile.role.name == 'admin'
    except Exception:
        return False

def ensure_admin_test_account():
    """Garantit la presence du compte admin_test pour les demonstrations."""
    admin_role, _ = Role.objects.get_or_create(name='admin')
    client_role, _ = Role.objects.get_or_create(name='client')

    admin_user, created = User.objects.get_or_create(
        username='admin_test',
        defaults={
            'email': 'admin_test@beauty-manager.local',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        }
    )

    if created:
        admin_user.set_password('AdminTest123!')
        admin_user.save()
    else:
        has_changed = False
        if admin_user.email != 'admin_test@beauty-manager.local':
            admin_user.email = 'admin_test@beauty-manager.local'
            has_changed = True
        if not admin_user.is_active:
            admin_user.is_active = True
            has_changed = True
        if not admin_user.is_staff:
            admin_user.is_staff = True
            has_changed = True
        if not admin_user.is_superuser:
            admin_user.is_superuser = True
            has_changed = True
        if has_changed:
            admin_user.save()

    admin_profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'role': admin_role, 'phone': ''}
    )
    if not created and admin_profile.role != admin_role:
        admin_profile.role = admin_role
        admin_profile.save(update_fields=['role'])

    # Verrouillage fort: desactiver tous les autres comptes admin.
    other_admin_users = User.objects.filter(
        Q(is_staff=True) | Q(is_superuser=True) | Q(userprofile__role__name='admin')
    ).exclude(username='admin_test').distinct()

    for other_user in other_admin_users:
        has_changed = False

        if other_user.is_staff:
            other_user.is_staff = False
            has_changed = True
        if other_user.is_superuser:
            other_user.is_superuser = False
            has_changed = True
        if other_user.is_active:
            other_user.is_active = False
            has_changed = True

        if has_changed:
            other_user.save(update_fields=['is_staff', 'is_superuser', 'is_active'])

        try:
            other_profile = other_user.userprofile
            if other_profile.role == admin_role:
                other_profile.role = client_role
                other_profile.save(update_fields=['role'])
        except UserProfile.DoesNotExist:
            continue


# Create your views here.

@never_cache
def home(request):
    return render(
        request,
        'manager/home.html',
        {
            'hero_cache_buster': getattr(
                django_settings, 'HERO_IMAGE_CACHE_BUSTER', '1'
            ),
        },
    )

def register_client(request):
    if request.method == 'POST':
        # Créer une copie des données POST et définir le rôle
        post_data = request.POST.copy()
        post_data['role'] = 'client'

        form = SecureUserRegistrationForm(post_data, request.FILES)
        if form.is_valid():
            try:
                # Vérifier si l'utilisateur existe déjà
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                
                if User.objects.filter(username=username).exists():
                    messages.error(request, f'❌ Le nom d\'utilisateur "{username}" est déjà pris. Veuillez en choisir un autre.')
                    return render(request, 'manager/register_client.html', {'form': form})
                
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'❌ L\'adresse email "{email}" est déjà utilisée. Veuillez utiliser une autre adresse email.')
                    return render(request, 'manager/register_client.html', {'form': form})
                
                # Créer l'utilisateur
                user = form.save(commit=False)
                user.is_active = True
                user.save()
                
                # Créer le profil utilisateur (rôle créé si base neuve sans setup_data)
                role, _ = Role.objects.get_or_create(name='client')
                UserProfile.objects.create(
                    user=user,
                    role=role,
                    phone=form.cleaned_data.get('phone', '')
                )
                
                messages.success(request, f'✅ Inscription réussie ! Bienvenue {username} ! Votre compte client a été créé avec succès. Vous pouvez maintenant vous connecter.')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'❌ Erreur lors de la création du compte : {str(e)}. Veuillez réessayer.')
                return render(request, 'manager/register_client.html', {'form': form})
        else:
            # Afficher les erreurs de validation
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'username':
                        error_messages.append(f"Nom d'utilisateur : {error}")
                    elif field == 'email':
                        error_messages.append(f"Email : {error}")
                    elif field == 'password1':
                        error_messages.append(f"Mot de passe : {error}")
                    elif field == 'password2':
                        error_messages.append(f"Confirmation mot de passe : {error}")
                    elif field == 'phone':
                        error_messages.append(f"Téléphone : {error}")
                    else:
                        error_messages.append(f"{field} : {error}")
            
            if error_messages:
                messages.error(request, f'❌ Erreurs de validation : {" | ".join(error_messages)}')
            else:
                messages.error(request, '❌ Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = SecureUserRegistrationForm()
        form.fields['role'].choices = [('client', 'Client')]
    
    return render(request, 'manager/register_client.html', {'form': form})

def register_coiffeuse(request):
    if request.method == 'POST':
        form = SecureUserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Nécessite validation admin
            user.save()
            
            # Créer le profil utilisateur
            role, _ = Role.objects.get_or_create(name='coiffeuse')
            user_profile = UserProfile.objects.create(
                user=user,
                role=role,
                phone=form.cleaned_data.get('phone', '')
            )
            
            # Gérer l'upload de l'image de profil
            if 'profile_image' in request.FILES:
                user_profile.profile_image = request.FILES['profile_image']
                user_profile.save()
            
            messages.success(request, 'Inscription esthéticienne soumise ! Votre compte sera activé après validation par l\'administrateur.')
            return redirect('login')
    else:
        form = SecureUserRegistrationForm()
        form.fields['role'].choices = [('coiffeuse', 'Esthéticienne')]
    
    return render(request, 'manager/register_coiffeuse.html', {'form': form})

@never_cache
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        if username == 'admin_test' and password == 'AdminTest123!':
            ensure_admin_test_account()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Verrouillage: seul admin_test peut se connecter en tant qu'admin.
            if (
                hasattr(user, 'userprofile')
                and user.userprofile.role.name == 'admin'
                and user.username != 'admin_test'
            ):
                messages.error(
                    request,
                    "Accès admin refusé. Utilisez uniquement l'identifiant admin_test.",
                )
                return redirect('login')

            login(request, user)
            try:
                profile = user.userprofile
                if profile.role.name == 'admin':
                    return redirect('dashboard_admin')
                elif profile.role.name == 'coiffeuse':
                    return redirect('dashboard_coiffeuse')
                else:
                    return redirect('dashboard_client')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Profil utilisateur non trouvé.')
                return redirect('login')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'manager/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')

def role_required(role_name):
    def decorator(view_func):
        @login_required
        @csrf_protect
        def _wrapped_view(request, *args, **kwargs):
            try:
                if not hasattr(request.user, 'userprofile'):
                    logger.warning(f"Tentative d'accès sans profil utilisateur: {request.user.username}")
                    raise PermissionDenied("Profil utilisateur non trouvé")
                
                if request.user.userprofile.role.name == role_name:
                    # Log de l'accès autorisé
                    logger.info(f"Accès autorisé pour {request.user.username} (rôle: {role_name})")
                    return view_func(request, *args, **kwargs)
                else:
                    logger.warning(f"Tentative d'accès non autorisé: {request.user.username} (rôle: {request.user.userprofile.role.name}) pour {role_name}")
                    raise PermissionDenied(f"Accès refusé : rôle {role_name} requis")
            except PermissionDenied:
                raise
            except Exception as e:
                logger.error(f"Erreur lors de la vérification des permissions: {e}")
                raise PermissionDenied("Erreur lors de la vérification des permissions")
        return _wrapped_view
    return decorator

@role_required('client')
def dashboard_client(request):
    user_profile = request.user.userprofile
    reservations = Reservation.objects.filter(client=user_profile).order_by('-date', '-heure')
    
    context = {
        'user_profile': user_profile,
        'reservations': reservations,
        'total_reservations': reservations.count(),
        'reservations_en_attente': reservations.filter(statut='en_attente').count(),
        'reservations_confirmees': reservations.filter(statut='confirmé').count(),
    }
    return render(request, 'manager/dashboard_client.html', context)

@role_required('coiffeuse')
def dashboard_coiffeuse(request):
    user_profile = request.user.userprofile
    today = timezone.now().date()
    
    # Rendez-vous d'aujourd'hui
    rdv_aujourd_hui = Reservation.objects.filter(
        coiffeuse=user_profile,
        date=today,
        statut__in=['en_attente', 'confirmé', 'payé']
    ).order_by('heure')
    
    # Toutes les réservations pour le planning
    reservations = Reservation.objects.filter(
        coiffeuse=user_profile,
        date__gte=today
    ).order_by('date', 'heure')
    
    context = {
        'user_profile': user_profile,
        'rdv_aujourd_hui': rdv_aujourd_hui,
        'reservations': reservations,
        'total_rdv_aujourd_hui': rdv_aujourd_hui.count(),
    }
    return render(request, 'manager/dashboard_coiffeuse.html', context)

@role_required('admin')
def dashboard_admin(request):
    today = timezone.now().date()
    
    # Statistiques générales
    total_reservations = Reservation.objects.count()
    reservations_aujourd_hui = Reservation.objects.filter(date=today).count()
    reservations_en_attente = Reservation.objects.filter(statut='en_attente').count()
    reservations_payees = Reservation.objects.filter(statut='payé').count()
    coiffeuses_actives = UserProfile.objects.filter(role__name='coiffeuse', user__is_active=True).count()
    clients_actifs = UserProfile.objects.filter(role__name='client', user__is_active=True).count()
    
    # Rendez-vous récents
    rdv_recents = Reservation.objects.filter(
        date__gte=today
    ).order_by('date', 'heure')[:10]
    
    # Coiffeuses en attente de validation
    coiffeuses_en_attente = UserProfile.objects.filter(
        role__name='coiffeuse',
        user__is_active=False
    )
    
    # Liste des clients actifs avec leurs informations
    clients_liste = UserProfile.objects.filter(
        role__name='client',
        user__is_active=True
    ).select_related('user').order_by('user__username')
    
    context = {
        'total_reservations': total_reservations,
        'reservations_aujourd_hui': reservations_aujourd_hui,
        'reservations_en_attente': reservations_en_attente,
        'reservations_payees': reservations_payees,
        'coiffeuses_actives': coiffeuses_actives,
        'clients_actifs': clients_actifs,
        'rdv_recents': rdv_recents,
        'coiffeuses_en_attente': coiffeuses_en_attente,
        'clients_liste': clients_liste,
    }
    return render(request, 'manager/dashboard_admin.html', context)

@role_required('client')
def reservation_client(request):
    user_profile = request.user.userprofile
    
    if request.method == 'POST':
        form = SecureReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.client = user_profile
            reservation.montant = reservation.service.price
            reservation.save()
            
            # Envoyer une notification de confirmation
            try:
                NotificationService.send_reservation_confirmation(reservation)
            except Exception as e:
                print(f"Erreur lors de l'envoi de la notification: {e}")
            
            messages.success(request, f'Réservation créée avec succès ! Montant : {reservation.montant}€')
            return redirect('dashboard_client')
    else:
        form = SecureReservationForm()
    
    # Récupérer les réservations du client
    reservations = Reservation.objects.filter(client=user_profile).order_by('-date', '-heure')
    
    # Récupérer uniquement les coiffeuses pour le formulaire
    role_coiffeuse, _ = Role.objects.get_or_create(name='coiffeuse')
    coiffeuses = UserProfile.objects.filter(role=role_coiffeuse).select_related('user')
    
    context = {
        'form': form,
        'reservations': reservations,
        'services': Service.objects.filter(is_active=True),
        'coiffeuses': coiffeuses,
    }
    return render(request, 'manager/reservation_client.html', context)

@role_required('client')
@require_http_methods(["GET", "POST"])
def simulate_payment(request, reservation_id):
    user_profile = request.user.userprofile
    
    try:
        reservation = get_object_or_404(Reservation, id=reservation_id, client=user_profile)
        
        # Vérifier que la réservation peut être payée
        if reservation.statut != 'en_attente':
            messages.error(request, "Cette réservation ne peut plus être payée.")
            return redirect('dashboard_client')
        
        if request.method == 'POST':
            numero = request.POST.get('numero', '').strip()
            payment_method = request.POST.get('payment_method', 'wave')
            
            # Validation selon la méthode de paiement
            if payment_method != 'cash':
                # Validation pour les paiements mobiles
                if not numero or len(numero) != 10:
                    messages.error(request, "Le numéro de téléphone doit contenir exactement 10 chiffres.")
                    return render(request, 'manager/simulate_payment.html', {'reservation': reservation})
                
                # Vérifier le format du numéro (10 chiffres uniquement)
                import re
                mobile_pattern = r'^[0-9]{10}$'
                if not re.match(mobile_pattern, numero):
                    messages.error(request, "Format de numéro invalide. Utilisez le format: 0556620398 (10 chiffres uniquement)")
                    return render(request, 'manager/simulate_payment.html', {'reservation': reservation})
            
            # Traitement du paiement selon la méthode
            try:
                if payment_method == 'cash':
                    # Pour les paiements en espèces, garder le statut "en_attente"
                    # L'admin ou l'esthéticienne devra confirmer le paiement
                    reservation.statut = 'en_attente'
                    reservation.payment_method = 'cash'
                    reservation.save()
                    
                    # Log du choix de paiement en espèces
                    logger.info(f"Paiement en espèces choisi pour la réservation {reservation.id} par {user_profile.user.username}")
                    
                    messages.success(request, "Réservation confirmée ! Paiement en espèces à effectuer au salon. Votre statut restera 'En attente' jusqu'à confirmation du paiement par le salon.")
                    
                else:
                    # Pour les paiements mobiles, passer directement à "payé"
                    reservation.statut = 'payé'
                    reservation.payment_method = 'mobile'
                    reservation.save()
                    
                    # Log du paiement mobile
                    payment_type = f"mobile money ({payment_method})"
                    logger.info(f"Paiement {payment_type} simulé pour la réservation {reservation.id} par {user_profile.user.username}")
                    
                    # Envoyer une notification de paiement
                    try:
                        NotificationService.send_payment_confirmation(reservation)
                    except Exception as e:
                        logger.error(f"Erreur lors de l'envoi de la notification: {e}")
                    
                    messages.success(request, f"Paiement {payment_method} simulé avec succès !")
                
                return redirect('dashboard_client')
                
            except Exception as e:
                logger.error(f"Erreur lors du paiement: {e}")
                messages.error(request, "Erreur lors du traitement du paiement. Veuillez réessayer.")
                return render(request, 'manager/simulate_payment.html', {'reservation': reservation})
        
        return render(request, 'manager/simulate_payment.html', {'reservation': reservation})
        
    except Exception as e:
        logger.error(f"Erreur dans simulate_payment: {e}")
        messages.error(request, "Erreur lors du chargement de la page de paiement.")
        return redirect('dashboard_client')

@role_required('coiffeuse')
def reservation_coiffeuse(request):
    user_profile = request.user.userprofile
    today = timezone.now().date()
    
    # Rendez-vous de la coiffeuse
    reservations = Reservation.objects.filter(
        coiffeuse=user_profile,
        date__gte=today
    ).order_by('date', 'heure')
    
    context = {
        'reservations': reservations,
        'user_profile': user_profile,
    }
    return render(request, 'manager/reservation_coiffeuse.html', context)

@role_required('admin')
def reservation_admin(request):
    # Par défaut, afficher toutes les réservations
    reservations = Reservation.objects.all().order_by('-date', '-heure')
    
    # Filtres
    statut_filter = request.GET.get('statut')
    if statut_filter:
        if statut_filter == 'toutes':
            reservations = Reservation.objects.all().order_by('-date', '-heure')
        elif statut_filter == 'en_attente':
            reservations = Reservation.objects.filter(statut='en_attente').order_by('-date', '-heure')
        else:
            reservations = Reservation.objects.filter(statut=statut_filter).order_by('-date', '-heure')
    
    date_filter = request.GET.get('date')
    if date_filter:
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        # Gestion des valeurs spéciales de date
        today = timezone.now().date()
        
        if date_filter == 'today':
            reservations = reservations.filter(date=today)
        elif date_filter == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            reservations = reservations.filter(date=tomorrow)
        elif date_filter == 'yesterday':
            yesterday = today - timedelta(days=1)
            reservations = reservations.filter(date=yesterday)
        elif date_filter == 'this_week':
            # Lundi de cette semaine
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            reservations = reservations.filter(date__range=[start_of_week, end_of_week])
        elif date_filter == 'next_week':
            # Lundi de la semaine prochaine
            start_of_week = today - timedelta(days=today.weekday())
            next_week_start = start_of_week + timedelta(days=7)
            next_week_end = next_week_start + timedelta(days=6)
            reservations = reservations.filter(date__range=[next_week_start, next_week_end])
        elif date_filter == 'this_month':
            # Premier jour du mois actuel
            start_of_month = today.replace(day=1)
            # Dernier jour du mois actuel
            if today.month == 12:
                end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            reservations = reservations.filter(date__range=[start_of_month, end_of_month])
        elif date_filter == 'next_month':
            # Premier jour du mois prochain
            if today.month == 12:
                start_of_next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                start_of_next_month = today.replace(month=today.month + 1, day=1)
            # Dernier jour du mois prochain
            if start_of_next_month.month == 12:
                end_of_next_month = start_of_next_month.replace(year=start_of_next_month.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_of_next_month = start_of_next_month.replace(month=start_of_next_month.month + 1, day=1) - timedelta(days=1)
            reservations = reservations.filter(date__range=[start_of_next_month, end_of_next_month])
        else:
            # Format de date standard (YYYY-MM-DD)
            try:
                parsed_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                reservations = reservations.filter(date=parsed_date)
            except ValueError:
                # Si le format n'est pas valide, on ignore le filtre
                pass
    
    coiffeuse_filter = request.GET.get('coiffeuse')
    if coiffeuse_filter:
        reservations = reservations.filter(coiffeuse_id=coiffeuse_filter)
    
    # Statistiques
    total_reservations = Reservation.objects.count()
    reservations_en_attente = Reservation.objects.filter(statut='en_attente').count()
    reservations_confirmees = Reservation.objects.filter(statut='confirmé').count()
    reservations_payees = Reservation.objects.filter(statut='payé').count()
    reservations_annulees = Reservation.objects.filter(statut='annulé').count()
    
    # Statistiques par rôle
    reservations_clients = Reservation.objects.filter(client__role__name='client').count()
    reservations_coiffeuses = Reservation.objects.filter(coiffeuse__role__name='coiffeuse').count()
    
    # Liste des coiffeuses pour le filtre
    coiffeuses = UserProfile.objects.filter(role__name='coiffeuse')
    
    # Liste des clients pour le filtre
    clients = UserProfile.objects.filter(role__name='client')
    
    context = {
        'reservations': reservations,
        'total_reservations': total_reservations,
        'reservations_en_attente': reservations_en_attente,
        'reservations_confirmees': reservations_confirmees,
        'reservations_payees': reservations_payees,
        'reservations_annulees': reservations_annulees,
        'reservations_clients': reservations_clients,
        'reservations_coiffeuses': reservations_coiffeuses,
        'coiffeuses': coiffeuses,
        'clients': clients,
    }
    return render(request, 'manager/reservation_admin.html', context)

@user_passes_test(is_admin)
def validation_coiffeuses(request):
    if request.method == 'POST':
        coiffeuse_id = request.POST.get('coiffeuse_id')
        action = request.POST.get('action')
        
        if coiffeuse_id and action:
            coiffeuse = get_object_or_404(UserProfile, id=coiffeuse_id, role__name='coiffeuse')
            
            if action == 'valider':
                coiffeuse.user.is_active = True
                coiffeuse.user.save()
                
                # Envoyer une notification de validation
                try:
                    NotificationService.send_coiffeuse_validation(coiffeuse)
                except Exception as e:
                    print(f"Erreur lors de l'envoi de la notification: {e}")
                
                messages.success(request, f'Esthéticienne {coiffeuse.user.username} validée avec succès !')
            elif action == 'rejeter':
                coiffeuse.user.delete()
                messages.success(request, f'Esthéticienne {coiffeuse.user.username} rejetée.')
    
    coiffeuses_en_attente = UserProfile.objects.filter(
        role__name='coiffeuse',
        user__is_active=False
    ).annotate(
        reservations_count=Count('reservations')
    )
    
    # Récupérer les coiffeuses validées avec le nombre de réservations
    coiffeuses_validees = UserProfile.objects.filter(
        role__name='coiffeuse',
        user__is_active=True
    ).annotate(
        reservations_count=Count('reservations')
    )
    
    return render(request, 'manager/validation_coiffeuses.html', {
        'coiffeuses_en_attente': coiffeuses_en_attente,
        'coiffeuses_validees': coiffeuses_validees
    })

# API pour le calendrier
def get_available_slots(request):
    """API pour récupérer les créneaux disponibles"""
    coiffeuse_id = request.GET.get('coiffeuse_id')
    date = request.GET.get('date')
    
    if not coiffeuse_id or not date:
        return JsonResponse({'error': 'Paramètres manquants'}, status=400)
    
    try:
        coiffeuse = UserProfile.objects.get(id=coiffeuse_id, role__name='coiffeuse')
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Créneaux disponibles (8h-19h, toutes les 30 minutes)
        slots = []
        start_time = datetime.strptime('08:00', '%H:%M').time()
        end_time = datetime.strptime('19:00', '%H:%M').time()
        
        current_time = start_time
        while current_time <= end_time:
            # Vérifier si le créneau est disponible
            conflicting_reservations = Reservation.objects.filter(
                coiffeuse=coiffeuse,
                date=date_obj,
                heure=current_time,
                statut__in=['en_attente', 'confirmé', 'payé']
            )
            
            if not conflicting_reservations.exists():
                slots.append(current_time.strftime('%H:%M'))
            
            # Ajouter 30 minutes
            current_dt = datetime.combine(date_obj, current_time)
            current_dt += timedelta(minutes=30)
            current_time = current_dt.time()
        
        return JsonResponse({'slots': slots})
        
    except (UserProfile.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Données invalides'}, status=400)

@login_required
def gestion_services(request):
    """Gestion des services par l'admin"""
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'admin':
        return HttpResponseForbidden("Accès refusé")
    
    services = Service.objects.all().order_by('name')
    
    context = {
        'services': services,
        'total_services': services.count(),
        'services_actifs': services.filter(is_active=True).count(),
        'services_inactifs': services.filter(is_active=False).count(),
    }
    return render(request, 'manager/gestion_services.html', context)

@login_required
def ajouter_service(request):
    """Ajouter un nouveau service"""
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'admin':
        return HttpResponseForbidden("Accès refusé")
    
    if request.method == 'POST':
        form = SecureServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.name}" ajouté avec succès !')
            return redirect('gestion_services')
    else:
        form = SecureServiceForm()
    
    context = {
        'form': form,
        'action': 'Ajouter',
    }
    return render(request, 'manager/form_service.html', context)

@login_required
def modifier_service(request, service_id):
    """Modifier un service existant"""
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'admin':
        return HttpResponseForbidden("Accès refusé")
    
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        form = SecureServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.name}" modifié avec succès !')
            return redirect('gestion_services')
    else:
        form = SecureServiceForm(instance=service)
    
    context = {
        'form': form,
        'service': service,
        'action': 'Modifier',
    }
    return render(request, 'manager/form_service.html', context)

@login_required
def supprimer_service(request, service_id):
    """Supprimer un service"""
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'admin':
        return HttpResponseForbidden("Accès refusé")
    
    service = get_object_or_404(Service, id=service_id)
    
    # Vérifier s'il y a des réservations liées
    reservations_count = Reservation.objects.filter(service=service).count()
    
    if request.method == 'POST':
        if reservations_count > 0:
            # Désactiver au lieu de supprimer
            service.is_active = False
            service.save()
            messages.warning(request, f'Service "{service.name}" désactivé (il a {reservations_count} réservation(s) liée(s))')
        else:
            service.delete()
            messages.success(request, f'Service "{service.name}" supprimé avec succès !')
        return redirect('gestion_services')
    
    context = {
        'service': service,
        'reservations_count': reservations_count,
    }
    return render(request, 'manager/confirmation_suppression_service.html', context)

@login_required
def activer_service(request, service_id):
    """Activer un service désactivé"""
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name != 'admin':
        return HttpResponseForbidden("Accès refusé")
    
    service = get_object_or_404(Service, id=service_id)
    service.is_active = True
    service.save()
    messages.success(request, f'Service "{service.name}" activé avec succès !')
    return redirect('gestion_services')

@user_passes_test(is_admin)
def services_list(request):
    services = Service.objects.all().order_by('-is_active', 'name')
    return render(request, 'manager/services_list.html', {'services': services})

@user_passes_test(is_admin)
def service_create(request):
    if request.method == 'POST':
        form = SecureServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service ajouté avec succès.")
            return redirect('services_list')
    else:
        form = SecureServiceForm()
    return render(request, 'manager/service_form.html', {'form': form, 'action': 'Créer'})

@user_passes_test(is_admin)
def service_update(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = SecureServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service modifié avec succès.")
            return redirect('services_list')
    else:
        form = SecureServiceForm(instance=service)
    return render(request, 'manager/service_form.html', {'form': form, 'action': 'Modifier'})

@user_passes_test(is_admin)
def service_delete(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    reservations_count = Reservation.objects.filter(service=service).count()
    
    if request.method == 'POST':
        if reservations_count > 0:
            # Désactiver au lieu de supprimer
            service.is_active = False
            service.save()
            messages.warning(request, f'Service "{service.name}" désactivé (il a {reservations_count} réservation(s) liée(s))')
        else:
            service.delete()
            messages.success(request, f'Service "{service.name}" supprimé avec succès!')
        return redirect('services_list')
    
    return render(request, 'manager/service_confirm_delete.html', {
        'service': service,
        'reservations_count': reservations_count
    })

@user_passes_test(is_admin)
def service_toggle_active(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.is_active = not service.is_active
    service.save()
    messages.success(request, f"Service {'activé' if service.is_active else 'désactivé'}.")
    return redirect('services_list')

# Nouvelles vues pour la gestion des réservations
@login_required
def modifier_reservation(request, reservation_id):
    """Modifier une réservation existante"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Vérifier les permissions
    if not (request.user.userprofile.role.name == 'admin' or 
            (request.user.userprofile.role.name == 'client' and reservation.client == request.user.userprofile)):
        return HttpResponseForbidden("Accès refusé")
    
    if request.method == 'POST':
        form = SecureReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            # Recalculer le montant si le service a changé
            if form.cleaned_data['service'] != reservation.service:
                reservation.montant = form.cleaned_data['service'].price
            
            form.save()
            messages.success(request, 'Réservation modifiée avec succès !')
            return redirect('dashboard_client' if request.user.userprofile.role.name == 'client' else 'reservation_admin')
    else:
        form = SecureReservationForm(instance=reservation)
    
    context = {
        'form': form,
        'reservation': reservation,
        'action': 'Modifier'
    }
    return render(request, 'manager/reservation_form.html', context)

@login_required
def annuler_reservation(request, reservation_id):
    """Annuler une réservation avec justification obligatoire"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Vérifier les permissions
    if not (request.user.userprofile.role.name == 'admin' or 
            (request.user.userprofile.role.name == 'client' and reservation.client == request.user.userprofile)):
        return HttpResponseForbidden("Accès refusé")
    
    # Vérifier que la réservation peut être annulée
    if reservation.statut not in ['en_attente', 'confirmé']:
        error_message = 'Cette réservation ne peut plus être annulée.'
        context = {
            'reservation': reservation,
            'form': AnnulationForm(),
            'error_message': error_message
        }
        return render(request, 'manager/confirmation_annulation.html', context)
    
    if request.method == 'POST':
        form = AnnulationForm(request.POST)
        if form.is_valid():
            justification = form.cleaned_data['justification']
            
            # Mettre à jour la réservation
            reservation.statut = 'annulé'
            reservation.justification_annulation = justification
            reservation.save()
            
            # Envoyer une notification d'annulation
            try:
                NotificationService.send_reservation_cancellation(reservation)
            except Exception as e:
                print(f"Erreur lors de l'envoi de la notification: {e}")
            
            messages.success(request, 'Réservation annulée avec succès ! Vous pouvez maintenant prendre un nouveau rendez-vous.')
            return redirect('reservation_client' if request.user.userprofile.role.name == 'client' else 'reservation_admin')
    else:
        form = AnnulationForm()
    
    context = {
        'reservation': reservation,
        'form': form
    }
    return render(request, 'manager/confirmation_annulation.html', context)

@user_passes_test(is_admin)
def confirmer_reservation(request, reservation_id):
    """Confirmer une réservation (admin seulement)"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        reservation.statut = 'confirmé'
        reservation.save()
        messages.success(request, 'Réservation confirmée avec succès !')
        return redirect('reservation_admin')
    
    return render(request, 'manager/confirmation_reservation.html', {'reservation': reservation})

# Nouvelles vues pour la gestion des profils
@login_required
def profil_utilisateur(request):
    """Afficher le profil de l'utilisateur"""
    user_profile = request.user.userprofile
    
    # Statistiques personnelles
    if user_profile.role.name == 'client':
        reservations = Reservation.objects.filter(client=user_profile)
        total_reservations = reservations.count()
        reservations_payees = reservations.filter(statut='payé').count()
        montant_total = reservations.filter(statut='payé').aggregate(
            total=Sum('montant')
        )['total'] or 0
        reservations_terminees = 0
        revenus = 0
    elif user_profile.role.name == 'coiffeuse':
        reservations = Reservation.objects.filter(coiffeuse=user_profile)
        total_reservations = reservations.count()
        reservations_terminees = reservations.filter(statut='terminé').count()
        revenus = reservations.filter(statut='payé').aggregate(
            total=Sum('montant')
        )['total'] or 0
        reservations_payees = 0
        montant_total = 0
    else:
        total_reservations = 0
        reservations_payees = 0
        reservations_terminees = 0
        montant_total = 0
        revenus = 0
    
    context = {
        'user_profile': user_profile,
        'total_reservations': total_reservations,
        'reservations_payees': reservations_payees if user_profile.role.name == 'client' else reservations_terminees,
        'montant_total': montant_total if user_profile.role.name == 'client' else revenus,
    }
    return render(request, 'manager/profil_utilisateur.html', context)

@login_required
def modifier_profil(request):
    """Modifier le profil utilisateur"""
    user_profile = request.user.userprofile
    
    if request.method == 'POST':
        # Mettre à jour les informations utilisateur
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Mettre à jour le profil
        user_profile.phone = request.POST.get('phone', user_profile.phone)
        
        # Gérer l'upload de l'image de profil
        if 'profile_image' in request.FILES:
            # Supprimer l'ancienne image si elle existe
            if user_profile.profile_image:
                try:
                    user_profile.profile_image.delete(save=False)
                except:
                    pass  # Ignorer les erreurs si le fichier n'existe pas
            
            # Sauvegarder la nouvelle image
            user_profile.profile_image = request.FILES['profile_image']
        
        user_profile.save()
        
        messages.success(request, 'Profil modifié avec succès !')
        return redirect('profil_utilisateur')
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'manager/modifier_profil.html', context)

@login_required
def changer_mot_de_passe(request):
    """Changer le mot de passe"""
    # Regle metier: le compte admin ne peut pas changer son mot de passe.
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role.name == 'admin':
        messages.error(request, "Le mot de passe de l'administrateur ne peut pas être modifié.")
        return redirect('profil_utilisateur')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Vérifier l'ancien mot de passe
        if not request.user.check_password(current_password):
            messages.error(request, 'Mot de passe actuel incorrect.')
            return render(request, 'manager/changer_mot_de_passe.html')
        
        # Vérifier que les nouveaux mots de passe correspondent
        if new_password != confirm_password:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
            return render(request, 'manager/changer_mot_de_passe.html')
        
        # Vérifier la complexité du mot de passe
        if len(new_password) < 8:
            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
            return render(request, 'manager/changer_mot_de_passe.html')
        
        # Changer le mot de passe
        request.user.set_password(new_password)
        request.user.save()
        
        # Reconnecter l'utilisateur
        login(request, request.user)
        messages.success(request, 'Mot de passe modifié avec succès !')
        return redirect('profil_utilisateur')
    
    return render(request, 'manager/changer_mot_de_passe.html')

@user_passes_test(is_admin)
def supprimer_coiffeuse(request, coiffeuse_id):
    """
    Vue pour supprimer une coiffeuse (admin seulement)
    """
    try:
        # Récupérer la coiffeuse
        coiffeuse = get_object_or_404(UserProfile, id=coiffeuse_id, role__name='coiffeuse')
        
        if request.method == 'POST':
            # Vérifier s'il y a des réservations actives
            reservations_actives = Reservation.objects.filter(
                coiffeuse=coiffeuse,
                statut__in=['en_attente', 'confirmé', 'payé']
            ).count()
            
            if reservations_actives > 0:
                messages.error(request, f'❌ Impossible de supprimer cette coiffeuse car elle a {reservations_actives} réservation(s) active(s).')
                return redirect('validation_coiffeuses')
            
            # Supprimer l'utilisateur et son profil
            username = coiffeuse.user.username
            coiffeuse.user.delete()  # Cela supprime aussi le UserProfile automatiquement
            
            messages.success(request, f'✅ La coiffeuse "{username}" a été supprimée avec succès.')
            return redirect('validation_coiffeuses')
        
        # Affichage de la page de confirmation
        context = {
            'coiffeuse': coiffeuse,
            'reservations_count': Reservation.objects.filter(coiffeuse=coiffeuse).count(),
            'reservations_actives': Reservation.objects.filter(
                coiffeuse=coiffeuse,
                statut__in=['en_attente', 'confirmé', 'payé']
            ).count()
        }
        return render(request, 'manager/confirmation_suppression_coiffeuse.html', context)
        
    except Exception as e:
        messages.error(request, f'❌ Erreur lors de la suppression : {str(e)}')
        return redirect('validation_coiffeuses')

@user_passes_test(is_admin)
def update_reservation_status(request, reservation_id):
    """Mettre à jour le statut d'une réservation"""
    if request.method == 'POST':
        try:
            # Log des données reçues pour le débogage
            logger.info(f"Données POST reçues: {dict(request.POST)}")
            logger.info(f"Headers reçus: {dict(request.headers)}")
            
            reservation = get_object_or_404(Reservation, id=reservation_id)
            new_status = request.POST.get('status')
            
            logger.info(f"Statut reçu: '{new_status}'")
            
            if new_status in ['en_attente', 'confirmé', 'payé', 'annulé', 'terminé']:
                reservation.statut = new_status
                reservation.save()
                
                # Log de l'action
                logger.info(f"Admin {request.user.username} a mis à jour le statut de la réservation #{reservation_id} vers '{new_status}'")
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Statut mis à jour vers {reservation.get_statut_display()}',
                    'new_status': new_status,
                    'display_status': reservation.get_statut_display()
                })
            else:
                logger.error(f"Statut invalide reçu: '{new_status}'")
                return JsonResponse({'success': False, 'message': f'Statut invalide: {new_status}'}, status=400)
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut de la réservation #{reservation_id}: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Erreur lors de la mise à jour: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

@user_passes_test(is_admin)
def get_reservation_details(request, reservation_id):
    """Obtenir les détails d'une réservation pour le modal"""
    try:
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        details = {
            'id': reservation.id,
            'statut': reservation.get_statut_display(),
            'date': reservation.date.strftime('%d/%m/%Y'),
            'heure': reservation.heure.strftime('%H:%M'),
            'montant': f"{reservation.montant} FCFA",
            'payment_method': reservation.payment_method,
            'client': {
                'nom': reservation.client.user.get_full_name() or reservation.client.user.username,
                'email': reservation.client.user.email,
                'telephone': reservation.client.phone or 'Non renseigné'
            },
            'coiffeuse': {
                'nom': reservation.coiffeuse.user.get_full_name() or reservation.coiffeuse.user.username,
                'telephone': reservation.coiffeuse.phone or 'Non renseigné'
            },
            'service': {
                'nom': reservation.service.name,
                'duree': f"{reservation.service.duration} minutes",
                'description': reservation.service.description or 'Aucune description'
            },
            'notes': reservation.notes or 'Aucune note'
        }
        
        return JsonResponse({'success': True, 'details': details})
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails de la réservation #{reservation_id}: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Erreur lors de la récupération des détails'}, status=500)

@user_passes_test(is_admin)
def test_admin_access(request):
    """Vue de test pour diagnostiquer l'accès admin"""
    return HttpResponse(f"""
    <h1>Test d'accès admin</h1>
    <p>✅ Vous avez accès à cette page !</p>
    <p>Utilisateur: {request.user.username}</p>
    <p>Rôle: {request.user.userprofile.role.name}</p>
    <p>is_admin(): {is_admin(request.user)}</p>
    <p><a href="/validation-coiffeuses/">Aller à la validation des coiffeuses</a></p>
    """)

@user_passes_test(is_admin)
def bilan_hebdomadaire(request):
    """Vue pour le bilan hebdomadaire des activités"""
    
    # Configurer la localisation française
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'French_France.1252')
        except:
            pass  # Utiliser la localisation par défaut si le français n'est pas disponible
    
    # Calculer la date de début de la semaine (lundi)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Récupérer les données de la semaine
    reservations_semaine = Reservation.objects.filter(
        date__gte=start_of_week,
        date__lte=end_of_week
    )
    
    # Statistiques
    total_reservations = reservations_semaine.count()
    reservations_confirmees = reservations_semaine.filter(statut='confirmé').count()
    reservations_payees = reservations_semaine.filter(statut='payé').count()
    chiffre_affaires = reservations_semaine.filter(statut='payé').aggregate(
        total=Sum('montant')
    )['total'] or 0
    
    # Réservations par jour de la semaine
    jours_semaine = []
    noms_jours = {
        0: 'Lundi',
        1: 'Mardi',
        2: 'Mercredi',
        3: 'Jeudi',
        4: 'Vendredi',
        5: 'Samedi',
        6: 'Dimanche'
    }
    
    for i in range(7):
        jour = start_of_week + timedelta(days=i)
        nb_reservations = reservations_semaine.filter(date=jour).count()
        # Calculer le pourcentage
        pourcentage = (nb_reservations / total_reservations * 100) if total_reservations > 0 else 0
        jours_semaine.append({
            'jour': jour,
            'nom_jour': noms_jours[i],
            'nb_reservations': nb_reservations,
            'pourcentage': pourcentage
        })
    
    # Top coiffeuses de la semaine
    top_coiffeuses = reservations_semaine.values('coiffeuse__user__username').annotate(
        nb_reservations=Count('id'),
        total_montant=Sum('montant')
    ).order_by('-nb_reservations')[:5]
    
    # Top services de la semaine
    top_services = reservations_semaine.values('service__name').annotate(
        nb_reservations=Count('id'),
        total_montant=Sum('montant')
    ).order_by('-nb_reservations')[:5]
    
    context = {
        'periode': f"Du {start_of_week.strftime('%d/%m/%Y')} au {end_of_week.strftime('%d/%m/%Y')}",
        'total_reservations': total_reservations,
        'reservations_confirmees': reservations_confirmees,
        'reservations_payees': reservations_payees,
        'chiffre_affaires': chiffre_affaires,
        'jours_semaine': jours_semaine,
        'top_coiffeuses': top_coiffeuses,
        'top_services': top_services,
        'reservations_semaine': reservations_semaine.order_by('-date', '-heure')[:10]
    }
    
    return render(request, 'manager/bilan_hebdomadaire.html', context)

@user_passes_test(is_admin)
def bilan_mensuel(request):
    """Vue pour le bilan mensuel des activités"""
    
    # Configurer la localisation française
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'French_France.1252')
        except:
            pass  # Utiliser la localisation par défaut si le français n'est pas disponible
    
    # Calculer le mois en cours
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Récupérer les données du mois
    reservations_mois = Reservation.objects.filter(
        date__gte=start_of_month,
        date__lte=end_of_month
    )
    
    # Statistiques
    total_reservations = reservations_mois.count()
    reservations_confirmees = reservations_mois.filter(statut='confirmé').count()
    reservations_payees = reservations_mois.filter(statut='payé').count()
    chiffre_affaires = reservations_mois.filter(statut='payé').aggregate(
        total=Sum('montant')
    )['total'] or 0
    
    # Réservations par semaine du mois (limité à 4 semaines)
    semaines_mois = []
    current_date = start_of_month
    semaine_num = 1
    
    # Calculer le nombre de jours dans le mois
    jours_dans_mois = (end_of_month - start_of_month).days + 1
    
    # Calculer le nombre de jours par semaine (4 semaines)
    jours_par_semaine = jours_dans_mois // 4
    
    for semaine in range(4):
        if semaine_num > 4:
            break
            
        semaine_start = current_date
        if semaine == 3:  # Dernière semaine
            semaine_end = end_of_month
        else:
            semaine_end = min(current_date + timedelta(days=jours_par_semaine - 1), end_of_month)
        
        nb_reservations = reservations_mois.filter(
            date__gte=semaine_start,
            date__lte=semaine_end
        ).count()
        
        semaines_mois.append({
            'semaine': semaine_num,
            'debut': semaine_start,
            'fin': semaine_end,
            'nb_reservations': nb_reservations
        })
        
        current_date = semaine_end + timedelta(days=1)
        semaine_num += 1
    
    # Top coiffeuses du mois
    top_coiffeuses = reservations_mois.values('coiffeuse__user__username').annotate(
        nb_reservations=Count('id'),
        total_montant=Sum('montant')
    ).order_by('-nb_reservations')[:5]
    
    # Top services du mois
    top_services = reservations_mois.values('service__name').annotate(
        nb_reservations=Count('id'),
        total_montant=Sum('montant')
    ).order_by('-nb_reservations')[:5]
    
    # Dictionnaire des noms de mois en français
    noms_mois = {
        1: 'Janvier',
        2: 'Février',
        3: 'Mars',
        4: 'Avril',
        5: 'Mai',
        6: 'Juin',
        7: 'Juillet',
        8: 'Août',
        9: 'Septembre',
        10: 'Octobre',
        11: 'Novembre',
        12: 'Décembre'
    }
    
    context = {
        'periode': f"{noms_mois[start_of_month.month]} {start_of_month.year}",
        'total_reservations': total_reservations,
        'reservations_confirmees': reservations_confirmees,
        'reservations_payees': reservations_payees,
        'chiffre_affaires': chiffre_affaires,
        'semaines_mois': semaines_mois,
        'top_coiffeuses': top_coiffeuses,
        'top_services': top_services,
        'reservations_mois': reservations_mois.order_by('-date', '-heure')[:10]
    }
    
    return render(request, 'manager/bilan_mensuel.html', context)

@user_passes_test(is_admin)
def bilan_annuel(request):
    """Vue pour le bilan annuel des activités"""
    
    # Configurer la localisation française
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'French_France.1252')
        except:
            pass  # Utiliser la localisation par défaut si le français n'est pas disponible
    
    # Calculer l'année en cours
    today = timezone.now().date()
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)
    
    # Récupérer les données de l'année
    reservations_annee = Reservation.objects.filter(
        date__gte=start_of_year,
        date__lte=end_of_year
    )
    
    # Statistiques
    total_reservations = reservations_annee.count()
    reservations_confirmees = reservations_annee.filter(statut='confirmé').count()
    reservations_payees = reservations_annee.filter(statut='payé').count()
    chiffre_affaires = reservations_annee.filter(statut='payé').aggregate(
        total=Sum('montant')
    )['total'] or 0
    
    # Réservations par mois
    mois_annee = []
    noms_mois = {
        1: 'Janvier',
        2: 'Février',
        3: 'Mars',
        4: 'Avril',
        5: 'Mai',
        6: 'Juin',
        7: 'Juillet',
        8: 'Août',
        9: 'Septembre',
        10: 'Octobre',
        11: 'Novembre',
        12: 'Décembre'
    }
    
    for mois in range(1, 13):
        start_month = start_of_year.replace(month=mois)
        if mois == 12:
            end_month = end_of_year
        else:
            end_month = start_of_year.replace(month=mois + 1) - timedelta(days=1)
        
        nb_reservations = reservations_annee.filter(
            date__gte=start_month,
            date__lte=end_month
        ).count()
        
        mois_annee.append({
            'mois': noms_mois[mois],
            'nb_reservations': nb_reservations
        })
    
    # Top coiffeuses de l'année
    top_coiffeuses = reservations_annee.values('coiffeuse__user__username').annotate(
        nb_reservations=Count('id'),
        total_montant=Sum('montant')
    ).order_by('-nb_reservations')[:5]
    
    # Top services de l'année
    top_services = reservations_annee.values('service__name').annotate(
        nb_reservations=Count('id'),
        total_montant=Sum('montant')
    ).order_by('-nb_reservations')[:5]
    
    context = {
        'periode': f"Année {start_of_year.year}",
        'total_reservations': total_reservations,
        'reservations_confirmees': reservations_confirmees,
        'reservations_payees': reservations_payees,
        'chiffre_affaires': chiffre_affaires,
        'mois_annee': mois_annee,
        'top_coiffeuses': top_coiffeuses,
        'top_services': top_services,
        'reservations_annee': reservations_annee.order_by('-date', '-heure')[:10]
    }
    
    return render(request, 'manager/bilan_annuel.html', context)

@user_passes_test(is_admin)
def confirmer_paiement_especes(request, reservation_id):
    """Vue pour confirmer un paiement en espèces (admin uniquement)"""
    try:
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        if request.method == 'POST':
            # Confirmer le paiement
            reservation.statut = 'payé'
            reservation.payment_method = 'cash'
            reservation.save()
            
            # Log de la confirmation
            logger.info(f"Paiement en espèces confirmé pour la réservation {reservation.id} par l'admin {request.user.username}")
            
            # Envoyer une notification de confirmation
            try:
                NotificationService.send_payment_confirmation(reservation)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de la notification: {e}")
            
            messages.success(request, f"Paiement en espèces confirmé pour la réservation #{reservation.id}")
            return redirect('reservation_admin')
        else:
            return render(request, 'manager/confirmer_paiement_especes.html', {
                'reservation': reservation
            })
    except Exception as e:
        logger.error(f"Erreur lors de la confirmation du paiement: {e}")
        messages.error(request, "Erreur lors de la confirmation du paiement")
        return redirect('reservation_admin')

@role_required('coiffeuse')
def confirmer_paiement_especes_coiffeuse(request, reservation_id):
    """Vue pour confirmer un paiement en espèces (coiffeuse)"""
    try:
        user_profile = request.user.userprofile
        reservation = get_object_or_404(Reservation, id=reservation_id, coiffeuse=user_profile)
        
        if request.method == 'POST':
            # Confirmer le paiement
            reservation.statut = 'payé'
            reservation.payment_method = 'cash'
            reservation.save()
            
            # Log de la confirmation
            logger.info(f"Paiement en espèces confirmé pour la réservation {reservation.id} par la coiffeuse {user_profile.user.username}")
            
            # Envoyer une notification de confirmation
            try:
                NotificationService.send_payment_confirmation(reservation)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de la notification: {e}")
            
            messages.success(request, f"Paiement confirmé pour la réservation de {reservation.client.user.username}")
            return redirect('reservation_coiffeuse')
        
        return render(request, 'manager/confirmer_paiement_especes_coiffeuse.html', {'reservation': reservation})
        
    except Exception as e:
        logger.error(f"Erreur dans confirmer_paiement_especes_coiffeuse: {e}")
        messages.error(request, "Erreur lors de la confirmation du paiement.")
        return redirect('reservation_coiffeuse')
