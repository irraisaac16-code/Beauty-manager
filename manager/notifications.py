from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime

class NotificationService:
    """Service pour gérer les notifications par email"""
    
    @staticmethod
    def send_reservation_confirmation(reservation):
        """Envoyer une confirmation de réservation"""
        subject = f"Confirmation de réservation - {reservation.service.name}"
        
        context = {
            'reservation': reservation,
            'client_name': reservation.client.user.username,
            'coiffeuse_name': reservation.coiffeuse.user.username,
            'service_name': reservation.service.name,
            'date': reservation.date.strftime("%d/%m/%Y"),
            'heure': reservation.heure.strftime("%H:%M"),
            'montant': reservation.montant,
        }
        
        html_message = render_to_string('manager/emails/reservation_confirmation.html', context)
        plain_message = render_to_string('manager/emails/reservation_confirmation.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.client.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    @staticmethod
    def send_reservation_cancellation(reservation):
        """Envoyer une notification d'annulation"""
        subject = f"Annulation de réservation - {reservation.service.name}"
        
        context = {
            'reservation': reservation,
            'client_name': reservation.client.user.username,
            'coiffeuse_name': reservation.coiffeuse.user.username,
            'service_name': reservation.service.name,
            'date': reservation.date.strftime("%d/%m/%Y"),
            'heure': reservation.heure.strftime("%H:%M"),
        }
        
        html_message = render_to_string('manager/emails/reservation_cancellation.html', context)
        plain_message = render_to_string('manager/emails/reservation_cancellation.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.client.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    @staticmethod
    def send_payment_confirmation(reservation):
        """Envoyer une confirmation de paiement"""
        subject = f"Paiement confirmé - {reservation.service.name}"
        
        context = {
            'reservation': reservation,
            'client_name': reservation.client.user.username,
            'service_name': reservation.service.name,
            'date': reservation.date.strftime("%d/%m/%Y"),
            'heure': reservation.heure.strftime("%H:%M"),
            'montant': reservation.montant,
        }
        
        html_message = render_to_string('manager/emails/payment_confirmation.html', context)
        plain_message = render_to_string('manager/emails/payment_confirmation.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.client.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    @staticmethod
    def send_reminder_24h(reservation):
        """Envoyer un rappel 24h avant le rendez-vous"""
        subject = f"Rappel : Rendez-vous demain - {reservation.service.name}"
        
        context = {
            'reservation': reservation,
            'client_name': reservation.client.user.username,
            'coiffeuse_name': reservation.coiffeuse.user.username,
            'service_name': reservation.service.name,
            'date': reservation.date.strftime("%d/%m/%Y"),
            'heure': reservation.heure.strftime("%H:%M"),
            'montant': reservation.montant,
        }
        
        html_message = render_to_string('manager/emails/reminder_24h.html', context)
        plain_message = render_to_string('manager/emails/reminder_24h.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.client.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    @staticmethod
    def send_coiffeuse_validation(coiffeuse_profile):
        """Envoyer une notification de validation à la coiffeuse"""
        subject = "Votre compte coiffeuse a été validé !"
        
        context = {
            'coiffeuse_name': coiffeuse_profile.user.username,
            'email': coiffeuse_profile.user.email,
        }
        
        html_message = render_to_string('manager/emails/coiffeuse_validation.html', context)
        plain_message = render_to_string('manager/emails/coiffeuse_validation.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[coiffeuse_profile.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False 