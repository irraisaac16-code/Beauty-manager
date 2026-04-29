from django.contrib import admin
from .models import Role, UserProfile, Service, Reservation

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    search_fields = ('user__username', 'role__name', 'phone')
    list_filter = ('role',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'price')
    ordering = ('name',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('date', 'heure', 'client', 'coiffeuse', 'service', 'statut', 'montant')
    search_fields = ('client__user__username', 'coiffeuse__user__username', 'service__name')
    list_filter = ('statut', 'date', 'coiffeuse', 'service')
    ordering = ('-date', '-heure')
    readonly_fields = ('created_at', 'updated_at')
