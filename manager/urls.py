from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('inscription/client/', views.register_client, name='register_client'),
    path('inscription/coiffeuse/', views.register_coiffeuse, name='register_coiffeuse'),
    path('connexion/', views.login_view, name='login'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('dashboard/client/', views.dashboard_client, name='dashboard_client'),
    path('dashboard/coiffeuse/', views.dashboard_coiffeuse, name='dashboard_coiffeuse'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('reservation/', views.reservation_client, name='reservation_client'),
    path('planning/', views.reservation_coiffeuse, name='reservation_coiffeuse'),
    path('reservations/', views.reservation_admin, name='reservation_admin'),
    path('validation-coiffeuses/', views.validation_coiffeuses, name='validation_coiffeuses'),
    path('payer/<int:reservation_id>/', views.simulate_payment, name='simulate_payment'),
    path('api/slots/', views.get_available_slots, name='get_available_slots'),
    
    # URLs pour la gestion des services
    path('services/', views.services_list, name='services_list'),
    path('services/ajouter/', views.service_create, name='service_create'),
    path('services/<int:service_id>/modifier/', views.service_update, name='service_update'),
    path('services/<int:service_id>/supprimer/', views.service_delete, name='service_delete'),
    path('services/<int:service_id>/toggle/', views.service_toggle_active, name='service_toggle_active'),
    
    # URLs pour la gestion des réservations
    path('reservation/<int:reservation_id>/modifier/', views.modifier_reservation, name='modifier_reservation'),
    path('reservation/<int:reservation_id>/annuler/', views.annuler_reservation, name='annuler_reservation'),
    path('reservation/<int:reservation_id>/confirmer/', views.confirmer_reservation, name='confirmer_reservation'),
    
    # Nouvelles URLs pour la gestion des réservations (admin)
    path('reservation/<int:reservation_id>/update-status/', views.update_reservation_status, name='update_reservation_status'),
    path('reservation/<int:reservation_id>/details/', views.get_reservation_details, name='get_reservation_details'),
    
    # URLs pour la confirmation des paiements en espèces
    path('reservation/<int:reservation_id>/confirmer-paiement/', views.confirmer_paiement_especes, name='confirmer_paiement_especes'),
    path('reservation/<int:reservation_id>/confirmer-paiement-coiffeuse/', views.confirmer_paiement_especes_coiffeuse, name='confirmer_paiement_especes_coiffeuse'),
    
    # URLs pour la gestion des profils
    path('profil/', views.profil_utilisateur, name='profil_utilisateur'),
    path('profil/modifier/', views.modifier_profil, name='modifier_profil'),
    path('changer-mot-de-passe/', views.changer_mot_de_passe, name='changer_mot_de_passe'),
    
    # URLs pour la gestion des esthéticiennes (admin)
    path('coiffeuse/<int:coiffeuse_id>/supprimer/', views.supprimer_coiffeuse, name='supprimer_coiffeuse'),
    
    # URL de test pour l'accès admin
    path('test-admin/', views.test_admin_access, name='test_admin_access'),
    
    # URLs pour les bilans
    path('bilan/hebdomadaire/', views.bilan_hebdomadaire, name='bilan_hebdomadaire'),
    path('bilan/mensuel/', views.bilan_mensuel, name='bilan_mensuel'),
    path('bilan/annuel/', views.bilan_annuel, name='bilan_annuel'),
] 