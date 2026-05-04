# Generated manually — garantit les rôles pour inscription / réservations sur base neuve

from django.db import migrations


def seed_roles(apps, schema_editor):
    Role = apps.get_model('manager', 'Role')
    for name in ('admin', 'client', 'coiffeuse'):
        Role.objects.get_or_create(name=name)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0006_reservation_justification_annulation'),
    ]

    operations = [
        migrations.RunPython(seed_roles, noop_reverse),
    ]
