# Generated by Django 2.2.4 on 2019-08-20 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circles', '0002_auto_20190820_1354'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membership',
            old_name='is_Active',
            new_name='is_active',
        ),
    ]
