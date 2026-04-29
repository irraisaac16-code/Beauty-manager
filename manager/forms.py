from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
from .models import UserProfile, Service, Reservation
from datetime import datetime, timedelta, time
import calendar

class CoiffeuseSelectWidget(forms.Select):
    """Widget personnalisé pour afficher les photos de profil des esthéticiennes"""
    
    def render_option(self, selected_choices, option_value, option_label):
        """Rendu personnalisé avec photo de profil"""
        if option_value == '':
            return f'<option value="">{option_label}</option>'
        
        # Récupérer le profil de l'esthéticienne
        try:
            from .models import UserProfile
            coiffeuse_profile = UserProfile.objects.get(id=option_value)
            
            # Créer l'option avec data attributes pour les informations de profil
            selected = 'selected' if str(option_value) in selected_choices else ''
            image_url = coiffeuse_profile.profile_image.url if coiffeuse_profile.profile_image else ''
            return f'<option value="{option_value}" {selected} data-image="{image_url}" data-username="{coiffeuse_profile.user.username}">{coiffeuse_profile.user.username}</option>'
            
        except UserProfile.DoesNotExist:
            return f'<option value="{option_value}">{option_label}</option>'

class TimeSlotWidget(forms.Select):
    """Widget personnalisé pour les créneaux de 30 minutes"""
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = self._get_time_slots()
    
    def _get_time_slots(self):
        """Génère les créneaux de 30 minutes de 8h à 19h (sauf 12h00-13h30)"""
        slots = []
        start_hour = 8
        end_hour = 19
        
        for hour in range(start_hour, end_hour):
            # Créneau à l'heure pile
            time_slot = time(hour, 0)
            # Exclure les créneaux entre 12h00 et 13h30
            if hour != 12 and hour != 13:
                slots.append((time_slot.strftime('%H:%M'), f"{hour:02d}:00"))
            
            # Créneau à la demi-heure
            time_slot = time(hour, 30)
            # Exclure les créneaux entre 12h00 et 13h30
            if hour != 12 and hour != 13:
                slots.append((time_slot.strftime('%H:%M'), f"{hour:02d}:30"))
        
        return slots

class SecureUserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription avec validation de sécurité renforcée"""
    
    # Validateurs pour les champs
    phone_regex = RegexValidator(
        regex=r'^[0-9]{10}$',
        message="Le numéro de téléphone doit contenir exactement 10 chiffres (exemple: 0556620398)."
    )
    
    username = forms.CharField(
        max_length=150,
        help_text="Choisissez le nom d'utilisateur de votre choix (150 caractères maximum)."
    )
    
    email = forms.EmailField(
        max_length=254,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message="Veuillez entrer une adresse email valide."
            )
        ]
    )
    
    phone = forms.CharField(
        validators=[phone_regex],
        max_length=10,
        required=False,
        help_text="Format: 0556620398 (10 chiffres uniquement)"
    )
    
    profile_image = forms.ImageField(
        required=False,
        help_text="Image de profil (recommandé pour les esthéticiennes)",
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    
    role = forms.ChoiceField(
        choices=[('client', 'Client'), ('coiffeuse', 'Esthéticienne')],
        widget=forms.HiddenInput(),
        required=False
    )
    
    # Validation personnalisée pour le mot de passe
    password1 = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Au moins 8 caractères minimum."
    )
    
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Entrez le même mot de passe que précédemment, pour vérification."
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_username(self):
        """Validation personnalisée du nom d'utilisateur"""
        username = self.cleaned_data.get('username')
        
        # Aucune contrainte sur le nom d'utilisateur sauf la longueur minimale
        if len(username) < 1:
            raise ValidationError("Le nom d'utilisateur ne peut pas être vide.")
        
        return username
    
    def clean_email(self):
        """Validation personnalisée de l'email"""
        email = self.cleaned_data.get('email')
        
        # Vérifier le format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Veuillez entrer une adresse email valide.")
        
        # Vérifier la longueur
        if len(email) > 254:
            raise ValidationError("L'adresse email est trop longue.")
        
        return email
    
    def clean_password1(self):
        """Validation personnalisée du mot de passe"""
        password = self.cleaned_data.get('password1')
        
        # Vérifier la longueur minimale
        if len(password) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        return password
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        
        return cleaned_data

class SecureReservationForm(forms.ModelForm):
    """Formulaire de réservation avec validation de sécurité"""
    
    class Meta:
        model = Reservation
        fields = ['coiffeuse', 'service', 'date', 'heure', 'notes']
        widgets = {
            'coiffeuse': forms.Select(attrs={'placeholder': 'Sélectionnez une coiffeuse'}),
            'service': forms.Select(attrs={'placeholder': 'Sélectionnez un service'}),
            'date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Sélectionnez une date'}),
            'heure': TimeSlotWidget(attrs={'placeholder': 'Sélectionnez un créneau'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'maxlength': 500, 'placeholder': 'Ajoutez des notes (optionnel)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer pour n'afficher que les coiffeuses
        from .models import Role, UserProfile
        try:
            role_coiffeuse = Role.objects.get(name='coiffeuse')
            coiffeuses = UserProfile.objects.filter(role=role_coiffeuse).select_related('user')
            self.fields['coiffeuse'].queryset = coiffeuses
        except Role.DoesNotExist:
            # Si le rôle n'existe pas, on laisse le queryset par défaut
            pass
        
        # Supprimer les tirets par défaut et définir des labels vides
        self.fields['coiffeuse'].empty_label = "Sélectionnez une coiffeuse"
        self.fields['service'].empty_label = "Sélectionnez un service"
        self.fields['heure'].empty_label = "Sélectionnez un créneau"
        
        # Définir des labels personnalisés
        self.fields['coiffeuse'].label = ""
        self.fields['service'].label = ""
        self.fields['date'].label = ""
        self.fields['heure'].label = ""
        self.fields['notes'].label = ""
        
    def clean_date(self):
        """Validation de la date"""
        date = self.cleaned_data.get('date')
        
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        # Vérifier que la date n'est pas dans le passé
        if date < today:
            raise ValidationError("Vous ne pouvez pas réserver une date dans le passé.")
        
        # Vérifier que la date n'est pas trop éloignée (max 2 mois)
        max_date = today + timedelta(days=60)
        if date > max_date:
            raise ValidationError("Vous ne pouvez pas réserver plus de 2 mois à l'avance.")
        
        return date
    
    def clean_heure(self):
        """Validation de l'heure"""
        heure = self.cleaned_data.get('heure')
        
        # Vérifier que l'heure est dans les horaires d'ouverture (8h-19h)
        if heure.hour < 8 or heure.hour >= 19:
            raise ValidationError("Les réservations sont possibles entre 8h et 19h.")
        
        # Vérifier que l'heure est un multiple de 30 minutes
        if heure.minute % 30 != 0:
            raise ValidationError("Les réservations se font par créneaux de 30 minutes.")
        
        # Vérifier que l'heure n'est pas entre 12h00 et 13h30 (pause déjeuner)
        if heure.hour == 12 or (heure.hour == 13 and heure.minute < 30):
            raise ValidationError("Les réservations ne sont pas possibles entre 12h00 et 13h30 (pause déjeuner).")
        
        return heure
    
    def clean_notes(self):
        """Validation des notes"""
        notes = self.cleaned_data.get('notes')
        
        if notes:
            # Vérifier la longueur
            if len(notes) > 500:
                raise ValidationError("Les notes ne peuvent pas dépasser 500 caractères.")
            
            # Vérifier le contenu suspect
            suspicious_patterns = [
                r'<script[^>]*>', r'javascript:', r'on\w+\s*=',
                r'<iframe[^>]*>', r'<object[^>]*>', r'<embed[^>]*>'
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, notes, re.IGNORECASE):
                    raise ValidationError("Le contenu des notes contient des éléments non autorisés.")
        
        return notes
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        coiffeuse = cleaned_data.get('coiffeuse')
        service = cleaned_data.get('service')
        date = cleaned_data.get('date')
        heure = cleaned_data.get('heure')
        
        # Vérifier que la coiffeuse est active
        if coiffeuse and not coiffeuse.user.is_active:
            raise ValidationError("Cette coiffeuse n'est pas disponible.")
        
        # Vérifier que le service est actif
        if service and not service.is_active:
            raise ValidationError("Ce service n'est pas disponible.")
            
            # Vérifier les conflits de réservation
        if coiffeuse and date and heure:
            from .models import Reservation
            conflicting_reservations = Reservation.objects.filter(
                coiffeuse=coiffeuse,
                date=date,
                heure=heure,
                statut__in=['en_attente', 'confirmé', 'payé']
            )
            
            if conflicting_reservations.exists():
                raise ValidationError("Ce créneau n'est plus disponible.")
        
        return cleaned_data

class SecureServiceForm(forms.ModelForm):
    """Formulaire de service avec validation de sécurité"""
    
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'maxlength': 1000}),
        }
    
    def clean_name(self):
        """Validation du nom du service"""
        name = self.cleaned_data.get('name')
        
        # Vérifier la longueur
        if len(name) < 2:
            raise ValidationError("Le nom du service doit contenir au moins 2 caractères.")
        
        if len(name) > 100:
            raise ValidationError("Le nom du service ne peut pas dépasser 100 caractères.")
        
        # Vérifier le contenu suspect
        suspicious_patterns = [
            r'<script[^>]*>', r'javascript:', r'on\w+\s*=',
            r'<iframe[^>]*>', r'<object[^>]*>', r'<embed[^>]*>'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                raise ValidationError("Le nom du service contient des éléments non autorisés.")
        
        return name
    
    def clean_price(self):
        """Validation du prix"""
        price = self.cleaned_data.get('price')
        
        if price <= 0:
            raise ValidationError("Le prix doit être supérieur à 0.")
        
        return price
    
    def clean_duration(self):
        """Validation de la durée"""
        duration = self.cleaned_data.get('duration')
        
        if duration <= 0:
            raise ValidationError("La durée doit être supérieure à 0.")
        
        if duration > 480:  # 8 heures maximum
            raise ValidationError("La durée ne peut pas dépasser 8 heures.")
        
        return duration
    
    def clean_description(self):
        """Validation de la description"""
        description = self.cleaned_data.get('description')
        
        if description:
            # Vérifier la longueur
            if len(description) > 1000:
                raise ValidationError("La description ne peut pas dépasser 1000 caractères.")
            
            # Vérifier le contenu suspect
            suspicious_patterns = [
                r'<script[^>]*>', r'javascript:', r'on\w+\s*=',
                r'<iframe[^>]*>', r'<object[^>]*>', r'<embed[^>]*>'
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    raise ValidationError("La description contient des éléments non autorisés.")
        
        return description

class AnnulationForm(forms.Form):
    """Formulaire pour l'annulation d'une réservation avec justification obligatoire"""
    
    justification = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Veuillez expliquer la raison de votre annulation (minimum 10 caractères)'
        }),
        required=True,
        min_length=10,
        max_length=500,
        help_text="La justification est obligatoire pour annuler une réservation"
    )
    
    def clean_justification(self):
        justification = self.cleaned_data.get('justification')
        # Validation du contenu de la justification
        if justification:
            # Vérifier qu'il n'y a pas de contenu suspect
            suspicious_patterns = [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, justification, re.IGNORECASE):
                    raise ValidationError("La justification contient des caractères non autorisés.")
        
        return justification.strip() 

# Alias pour la compatibilité 