# Generated by Django 4.0.1 on 2022-03-09 03:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_room_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='has_access',
        ),
    ]
