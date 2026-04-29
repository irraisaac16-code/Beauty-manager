# Restriction des horaires de réservation - Pause déjeuner

## Objectif
Empêcher les clients de prendre des rendez-vous entre 12h00 et 13h30 pour permettre une pause déjeuner au personnel.

## Modifications apportées

### 1. Modification du widget de sélection d'horaires (`manager/forms.py`)

**Fichier modifié :** `manager/forms.py`

**Classe :** `TimeSlotWidget`

**Méthode :** `_get_time_slots()`

**Changements :**
- Exclusion des créneaux entre 12h00 et 13h30
- Logique simplifiée : `if hour != 12 and hour != 13:`

**Avant :**
```python
for hour in range(start_hour, end_hour):
    # Créneau à l'heure pile
    time_slot = time(hour, 0)
    slots.append((time_slot.strftime('%H:%M'), f"{hour:02d}:00"))
    
    # Créneau à la demi-heure
    time_slot = time(hour, 30)
    slots.append((time_slot.strftime('%H:%M'), f"{hour:02d}:30"))
```

**Après :**
```python
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
```

### 2. Ajout de validation côté formulaire (`manager/forms.py`)

**Classe :** `SecureReservationForm`

**Méthode :** `clean_heure()`

**Ajout :**
```python
# Vérifier que l'heure n'est pas entre 12h00 et 13h30 (pause déjeuner)
if heure.hour == 12 or (heure.hour == 13 and heure.minute < 30):
    raise ValidationError("Les réservations ne sont pas possibles entre 12h00 et 13h30 (pause déjeuner).")
```

## Horaires disponibles

### Créneaux inclus (8h00 - 19h00) :
- 08:00 - 08:30
- 09:00 - 09:30
- 10:00 - 10:30
- 11:00 - 11:30
- 14:00 - 14:30
- 15:00 - 15:30
- 16:00 - 16:30
- 17:00 - 17:30
- 18:00 - 18:30

### Créneaux exclus (12h00 - 13h30) :
- 12:00 - 12:30
- 13:00 - 13:30

## Fonctionnalités

### 1. Restriction au niveau de l'interface utilisateur
- Les créneaux entre 12h00 et 13h30 n'apparaissent pas dans la liste déroulante
- Les utilisateurs ne peuvent pas sélectionner ces horaires

### 2. Validation côté serveur
- Double vérification au niveau du formulaire
- Message d'erreur explicite si quelqu'un tente de contourner la restriction
- Sécurité renforcée contre les tentatives de manipulation

### 3. Messages d'erreur clairs
- Message explicite : "Les réservations ne sont pas possibles entre 12h00 et 13h30 (pause déjeuner)."
- Indication claire de la raison de la restriction

## Tests effectués

### ✅ Tests de validation
- **Créneaux restreints :** 12:00, 12:30, 13:00, 13:30 correctement exclus
- **Créneaux autorisés :** 08:00, 11:30, 14:00, 18:30 correctement disponibles
- **Validation formulaire :** Les créneaux disponibles sont acceptés par le formulaire

### ✅ Tests d'interface
- Widget génère correctement 18 créneaux (au lieu de 22)
- Exclusion complète des créneaux 12h00-13h30
- Pas de créneaux manquants dans les autres plages horaires

## Avantages de l'implémentation

1. **Simplicité :** Logique claire et facile à maintenir
2. **Sécurité :** Double validation (interface + serveur)
3. **Flexibilité :** Facile à modifier si les horaires changent
4. **Expérience utilisateur :** Messages d'erreur explicites
5. **Cohérence :** Même restriction pour tous les utilisateurs

## Maintenance

### Pour modifier les horaires de restriction :
1. Modifier la condition dans `TimeSlotWidget._get_time_slots()`
2. Modifier la condition dans `SecureReservationForm.clean_heure()`
3. Mettre à jour le message d'erreur si nécessaire

### Exemple pour changer la restriction :
```python
# Pour exclure 11h00-12h00 au lieu de 12h00-13h30
if hour != 11 and hour != 12:
    # ... ajouter les créneaux
```

## Impact sur l'existant

- ✅ Aucun impact sur les réservations existantes
- ✅ Compatible avec toutes les fonctionnalités existantes
- ✅ Pas de modification de la base de données requise
- ✅ Rétrocompatible avec l'interface existante 