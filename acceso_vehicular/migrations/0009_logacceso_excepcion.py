# Generated by Django 4.2.5 on 2023-12-10 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acceso_vehicular', '0008_alter_empleado_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='logacceso',
            name='excepcion',
            field=models.BooleanField(default=False),
        ),
    ]
