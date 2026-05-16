from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('coiffeuse', 'Esthéticienne'),
        ('client', 'Client'),
    ]
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, help_text="Image de profil (recommandé pour les esthéticiennes)")

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    duration = models.IntegerField(help_text="Durée en minutes")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.price} FCFA ({self.duration}min)"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmé', 'Confirmé'),
        ('payé', 'Payé'),
        ('terminé', 'Terminé'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('mobile', 'Wave'),
        ('cash', 'Espèces'),
        ('not_set', 'Non défini'),
    ]
    
    client = models.ForeignKey(UserProfile, related_name='reservations', on_delete=models.CASCADE)
    coiffeuse = models.ForeignKey(UserProfile, related_name='rdv_coiffeuse', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    heure = models.TimeField()
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='not_set')
    justification_annulation = models.TextField(blank=True, null=True, help_text="Justification de l'annulation par le client")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} {self.heure} - {self.client.user.username} avec {self.coiffeuse.user.username}"

    class Meta:
        ordering = ['-date', '-heure']
