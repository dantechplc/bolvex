# Generated by Django 3.1.8 on 2023-01-07 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20230107_1145'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='roi_balance',
            new_name='expected_roi',
        ),
        migrations.RenameField(
            model_name='account',
            old_name='roi_balance_currency',
            new_name='expected_roi_currency',
        ),
    ]
