# Generated by Django 4.2.5 on 2023-10-23 22:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('acceso_vehicular', '0002_colorvehiculo_marcavehiculo_tipovehiculo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='empleado',
            name='jefe_inmediato',
        ),
    ]
